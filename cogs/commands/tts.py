import io
import asyncio
import discord
from discord.ext import commands
import aiosqlite
import wavelink

from core import Context
from core.Cog import Cog
from utils.Tools import blacklist_check, ignore_check

DB_PATH = "db/tts.db"
COLOR = 0xFF0000

# Số giây chờ idle trước khi tự disconnect khỏi voice
IDLE_TIMEOUT = 180  # 3 phút


async def setup_tts_db():
    """Tạo bảng lưu config TTS, tự migrate nếu schema cũ bị sai."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tts_config'"
        ) as cursor:
            table_exists = await cursor.fetchone()

        if table_exists:
            async with db.execute("PRAGMA table_info(tts_config)") as cursor:
                cols = {row[1] for row in await cursor.fetchall()}
            if "channel_id" not in cols:
                await db.execute("DROP TABLE tts_config")
                await db.commit()

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tts_config (
                guild_id   INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL
            )
        """)
        await db.commit()


def _is_wavelink_playing(voice_client) -> bool:
    """Kiểm tra xem voice client có phải Wavelink Player đang phát nhạc không."""
    try:
        if isinstance(voice_client, wavelink.Player) and voice_client.playing:
            return True
    except Exception:
        pass
    return False


async def _speak(voice_client: discord.VoiceClient, text: str):
    """
    Generate TTS audio in-memory (BytesIO) và phát qua FFmpegPCMAudio.
    Chờ đến khi audio phát xong rồi mới return.
    """
    from gtts import gTTS
    loop = asyncio.get_event_loop()

    def _gen():
        buf = io.BytesIO()
        gTTS(text=text, lang="vi", slow=False).write_to_fp(buf)
        buf.seek(0)
        return buf

    buf = await loop.run_in_executor(None, _gen)
    source = discord.FFmpegPCMAudio(buf, pipe=True)
    voice_client.play(source)

    while voice_client.is_playing():
        await asyncio.sleep(0.3)


class TTS(Cog, name="TTS"):
    """Text-to-Speech — đọc tin nhắn qua voice channel."""

    def __init__(self, bot):
        self.bot = bot
        # guild_id -> text_channel_id
        self._tts_channels: dict[int, int] = {}
        # Lock per guild để tránh TTS chồng chéo
        self._locks: dict[int, asyncio.Lock] = {}
        # Task idle-disconnect per guild
        self._idle_tasks: dict[int, asyncio.Task] = {}
        bot.loop.create_task(self._init())

    async def _init(self):
        await setup_tts_db()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT guild_id, channel_id FROM tts_config") as cursor:
                for guild_id, channel_id in await cursor.fetchall():
                    self._tts_channels[guild_id] = channel_id

    # ── Helpers ─────────────────────────────────────────────────────────────────

    def _get_lock(self, guild_id: int) -> asyncio.Lock:
        if guild_id not in self._locks:
            self._locks[guild_id] = asyncio.Lock()
        return self._locks[guild_id]

    def _reset_idle_timer(self, guild_id: int, vc: discord.VoiceClient):
        """Hủy timer cũ và bắt đầu đếm ngược idle mới."""
        old = self._idle_tasks.get(guild_id)
        if old and not old.done():
            old.cancel()
        task = self.bot.loop.create_task(self._idle_disconnect(guild_id, vc))
        self._idle_tasks[guild_id] = task

    def _cancel_idle_timer(self, guild_id: int):
        """Hủy idle timer nếu đang chạy (ví dụ khi music bắt đầu)."""
        old = self._idle_tasks.pop(guild_id, None)
        if old and not old.done():
            old.cancel()

    async def _idle_disconnect(self, guild_id: int, vc: discord.VoiceClient):
        """
        Chờ IDLE_TIMEOUT giây. Nếu hết giờ mà bot vẫn idle
        (không phát nhạc, không có TTS) thì tự disconnect.
        """
        await asyncio.sleep(IDLE_TIMEOUT)
        try:
            # Lấy lại voice client hiện tại của guild
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            current_vc = guild.voice_client
            if not current_vc:
                return

            # Nếu đang phát nhạc (Wavelink) → không disconnect
            if _is_wavelink_playing(current_vc):
                return

            # Nếu đang phát TTS → không disconnect (sẽ được reset sau)
            if current_vc.is_playing():
                return

            await current_vc.disconnect(force=True)
        except Exception:
            pass

    # ── DB helpers ───────────────────────────────────────────────────────────────

    async def _save_tts(self, guild_id: int, channel_id: int):
        self._tts_channels[guild_id] = channel_id
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT OR REPLACE INTO tts_config (guild_id, channel_id) VALUES (?, ?)",
                (guild_id, channel_id)
            )
            await db.commit()

    async def _clear_tts(self, guild_id: int):
        self._tts_channels.pop(guild_id, None)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM tts_config WHERE guild_id = ?", (guild_id,))
            await db.commit()

    # ── Voice connect helper ─────────────────────────────────────────────────────

    async def _ensure_connected(self, guild: discord.Guild, channel: discord.VoiceChannel) -> discord.VoiceClient:
        """Join / move đến đúng channel, trả về VoiceClient hiện tại."""
        vc = guild.voice_client
        if vc is None:
            return await channel.connect()
        if vc.channel != channel:
            await vc.move_to(channel)
        return vc

    # ── Commands ─────────────────────────────────────────────────────────────────

    @commands.command(
        name="say",
        usage="say <text>",
        help="Bot tự join voice channel của bạn và đọc to đoạn văn bản."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx: Context, *, text: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply(
                embed=discord.Embed(description="❌ Bạn phải ở trong voice channel để dùng lệnh này.", color=COLOR),
                mention_author=False
            )

        guild_vc = ctx.guild.voice_client

        # Đang phát nhạc Wavelink → không đọc
        if guild_vc and _is_wavelink_playing(guild_vc):
            return await ctx.reply(
                embed=discord.Embed(description="🎵 Bot đang phát nhạc, không thể đọc TTS lúc này.", color=COLOR),
                mention_author=False
            )

        # Đang phát TTS khác → không đọc
        if guild_vc and guild_vc.is_playing():
            return await ctx.reply(
                embed=discord.Embed(description="🔊 Bot đang bận, vui lòng chờ.", color=COLOR),
                mention_author=False
            )

        lock = self._get_lock(ctx.guild.id)
        async with lock:
            try:
                vc = await self._ensure_connected(ctx.guild, ctx.author.voice.channel)

                preview = discord.utils.escape_markdown(text[:80])
                suffix = "..." if len(text) > 80 else ""
                await ctx.reply(
                    embed=discord.Embed(description=f"🔊 Đang đọc: **{preview}{suffix}**", color=COLOR),
                    mention_author=False
                )

                # Hủy idle timer trong lúc đọc
                self._cancel_idle_timer(ctx.guild.id)
                await _speak(vc, text)

            except Exception as e:
                await ctx.reply(
                    embed=discord.Embed(description=f"❌ Lỗi TTS: {e}", color=COLOR),
                    mention_author=False
                )
            finally:
                # Sau khi đọc xong → bắt đầu đếm idle
                current_vc = ctx.guild.voice_client
                if current_vc and not isinstance(current_vc, wavelink.Player):
                    self._reset_idle_timer(ctx.guild.id, current_vc)

    # ── Group: >tts ──────────────────────────────────────────────────────────────

    @commands.group(
        name="tts",
        invoke_without_command=True,
        usage="tts <set|clear|status>",
        help="Quản lý tính năng tự động đọc tin nhắn TTS."
    )
    @blacklist_check()
    @ignore_check()
    async def tts(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @tts.command(
        name="set",
        usage="tts set <#channel>",
        help="Khi bạn ở trong voice chat, mọi tin nhắn bạn gửi trong channel này sẽ được bot đọc to."
    )
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def tts_set(self, ctx: Context, channel: discord.TextChannel):
        await self._save_tts(ctx.guild.id, channel.id)
        embed = discord.Embed(
            title="<:tick:1453391589148983367> TTS Đã Bật",
            description=(
                f"✅ Kênh TTS đã được đặt thành {channel.mention}.\n\n"
                f"📌 Khi bạn ở trong **voice channel**, mọi tin nhắn bạn gửi vào {channel.mention} "
                f"sẽ được bot đọc to.\n\n"
                f"⏱️ Bot sẽ tự rời phòng sau **{IDLE_TIMEOUT // 60} phút** không có hoạt động.\n"
                f"⚠️ Bot sẽ không đọc nếu đang phát nhạc."
            ),
            color=COLOR
        )
        embed.set_footer(text=f"Thiết lập bởi {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    @tts.command(
        name="clear",
        usage="tts clear",
        help="Tắt tính năng TTS tự động trong server này."
    )
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def tts_clear(self, ctx: Context):
        if ctx.guild.id not in self._tts_channels:
            return await ctx.reply(
                embed=discord.Embed(description="ℹ️ TTS chưa được bật trong server này.", color=COLOR),
                mention_author=False
            )

        await self._clear_tts(ctx.guild.id)
        self._cancel_idle_timer(ctx.guild.id)

        # Disconnect ngay nếu bot đang ở VC chỉ vì TTS
        guild_vc = ctx.guild.voice_client
        if guild_vc and not isinstance(guild_vc, wavelink.Player) and not guild_vc.is_playing():
            await guild_vc.disconnect()

        await ctx.reply(
            embed=discord.Embed(
                title="<:tick:1453391589148983367> TTS Đã Tắt",
                description="✅ Tính năng TTS tự động đã được tắt.",
                color=COLOR
            ),
            mention_author=False
        )

    @tts.command(
        name="status",
        usage="tts status",
        help="Xem kênh TTS đang được thiết lập cho server."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tts_status(self, ctx: Context):
        channel_id = self._tts_channels.get(ctx.guild.id)
        if not channel_id:
            embed = discord.Embed(
                description="ℹ️ TTS chưa được bật. Dùng `>tts set <#channel>` để bật.",
                color=COLOR
            )
        else:
            channel = ctx.guild.get_channel(channel_id)
            ch_mention = channel.mention if channel else f"ID: {channel_id} (đã bị xóa)"
            embed = discord.Embed(
                title="🔊 Trạng thái TTS",
                description=(
                    f"TTS đang bật cho kênh: {ch_mention}\n"
                    f"⏱️ Auto-disconnect sau: **{IDLE_TIMEOUT // 60} phút** idle"
                ),
                color=COLOR
            )
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    # ── Event Listener ───────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Tự động đọc tin nhắn trong kênh TTS đã cài."""
        if not message.guild or message.author.bot:
            return

        channel_id = self._tts_channels.get(message.guild.id)
        if not channel_id or message.channel.id != channel_id:
            return

        member = message.guild.get_member(message.author.id)
        if not member or not member.voice or not member.voice.channel:
            return

        text = message.content.strip()
        if not text or text.startswith(">") or text.startswith("/"):
            return

        guild_vc = message.guild.voice_client

        if guild_vc and _is_wavelink_playing(guild_vc):
            return

        if guild_vc and guild_vc.is_playing():
            return

        lock = self._get_lock(message.guild.id)
        async with lock:
            try:
                vc = await self._ensure_connected(message.guild, member.voice.channel)

                self._cancel_idle_timer(message.guild.id)
                await _speak(vc, text[:300])

            except Exception:
                pass
            finally:
                current_vc = message.guild.voice_client
                if current_vc and not isinstance(current_vc, wavelink.Player):
                    self._reset_idle_timer(message.guild.id, current_vc)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """
        Khi channel trở nên trống (chỉ còn bot) → bắt đầu idle timer.
        Khi có người join lại → hủy idle timer.
        """
        guild = member.guild
        guild_vc = guild.voice_client
        if not guild_vc or isinstance(guild_vc, wavelink.Player):
            return

        bot_channel = guild_vc.channel
        if not bot_channel:
            return

        human_members = [m for m in bot_channel.members if not m.bot]

        if not human_members:
            # Không còn ai → bắt đầu đếm idle
            self._reset_idle_timer(guild.id, guild_vc)
        else:
            # Có người → hủy idle timer (ai đó đang ở cùng)
            self._cancel_idle_timer(guild.id)
