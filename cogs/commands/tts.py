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


async def setup_tts_db():
    """Tạo bảng lưu config TTS cho mỗi guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tts_config (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL
            )
        """)
        await db.commit()


def _is_wavelink_playing(voice_client) -> bool:
    """Kiểm tra xem voice client có phải Wavelink Player đang phát nhạc không."""
    try:
        import wavelink
        if isinstance(voice_client, wavelink.Player) and voice_client.playing:
            return True
    except Exception:
        pass
    return False


async def _speak(voice_client: discord.VoiceClient, text: str):
    """
    Tạo audio TTS từ gTTS vào BytesIO buffer và phát qua FFmpegPCMAudio.
    Không ghi file tạm ra đĩa — hoàn toàn in-memory.
    Chờ cho đến khi audio phát xong.
    """
    from gtts import gTTS

    loop = asyncio.get_event_loop()

    # Tạo TTS trong thread pool để không block event loop
    def _gen_audio():
        buf = io.BytesIO()
        tts = gTTS(text=text, lang="vi", slow=False)
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf

    buf = await loop.run_in_executor(None, _gen_audio)

    # FFmpegPCMAudio đọc từ pipe stdin
    source = discord.FFmpegPCMAudio(buf, pipe=True)
    voice_client.play(source)

    # Chờ đến khi phát xong
    while voice_client.is_playing():
        await asyncio.sleep(0.3)


class TTS(Cog, name="TTS"):
    """Text-to-Speech — đọc tin nhắn qua voice channel."""

    def __init__(self, bot):
        self.bot = bot
        # guild_id -> text_channel_id (cache in-memory, đồng bộ với DB)
        self._tts_channels: dict[int, int] = {}
        # Lock per guild để tránh TTS chồng chéo nhau
        self._locks: dict[int, asyncio.Lock] = {}
        bot.loop.create_task(self._init())

    async def _init(self):
        await setup_tts_db()
        # Load toàn bộ config từ DB vào cache
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT guild_id, channel_id FROM tts_config") as cursor:
                rows = await cursor.fetchall()
                for guild_id, channel_id in rows:
                    self._tts_channels[guild_id] = channel_id

    def _get_lock(self, guild_id: int) -> asyncio.Lock:
        if guild_id not in self._locks:
            self._locks[guild_id] = asyncio.Lock()
        return self._locks[guild_id]

    # ─────────────────────────────── DB helpers ─────────────────────────────────

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

    # ─────────────────────────────── Commands ───────────────────────────────────

    @commands.command(
        name="say",
        usage="say <text>",
        help="Bot tự join voice channel của bạn và đọc to đoạn văn bản."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx: Context, *, text: str):
        """Đọc to một đoạn văn bản trong voice channel."""
        # Kiểm tra người dùng có trong voice channel không
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                description="❌ Bạn phải ở trong một voice channel để dùng lệnh này.",
                color=COLOR
            )
            return await ctx.reply(embed=embed, mention_author=False)

        vc_channel = ctx.author.voice.channel
        guild_vc = ctx.guild.voice_client

        # Nếu đang phát nhạc → không đọc
        if guild_vc and _is_wavelink_playing(guild_vc):
            embed = discord.Embed(
                description="🎵 Bot đang phát nhạc, không thể đọc TTS lúc này.",
                color=COLOR
            )
            return await ctx.reply(embed=embed, mention_author=False)

        # Nếu bot đang trong VC khác và đang phát audio → từ chối
        if guild_vc and guild_vc.is_playing():
            embed = discord.Embed(
                description="🔊 Bot đang nói chuyện, vui lòng chờ.",
                color=COLOR
            )
            return await ctx.reply(embed=embed, mention_author=False)

        lock = self._get_lock(ctx.guild.id)

        async with lock:
            try:
                # Connect hoặc move đến đúng channel
                if guild_vc is None:
                    vc = await vc_channel.connect()
                elif guild_vc.channel != vc_channel:
                    await guild_vc.move_to(vc_channel)
                    vc = guild_vc
                else:
                    vc = guild_vc

                confirm = discord.Embed(
                    description=f"🔊 Đang đọc: **{discord.utils.escape_markdown(text[:80])}{'...' if len(text) > 80 else ''}**",
                    color=COLOR
                )
                await ctx.reply(embed=confirm, mention_author=False)

                await _speak(vc, text)

            except discord.ClientException as e:
                await ctx.reply(
                    embed=discord.Embed(description=f"❌ Lỗi kết nối voice: {e}", color=COLOR),
                    mention_author=False
                )
            except Exception as e:
                await ctx.reply(
                    embed=discord.Embed(description=f"❌ Lỗi TTS: {e}", color=COLOR),
                    mention_author=False
                )
            finally:
                # Disconnect nếu không có auto-TTS đang bật
                vc_after = ctx.guild.voice_client
                if vc_after and not isinstance(vc_after, wavelink.Player):
                    if not vc_after.is_playing():
                        await vc_after.disconnect()

    # ─── Group: >tts ─────────────────────────────────────────────────────────────

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
        """Cài đặt kênh text để TTS tự động."""
        await self._save_tts(ctx.guild.id, channel.id)
        embed = discord.Embed(
            title="<:tick:1453391589148983367> TTS Đã Bật",
            description=(
                f"✅ Kênh TTS đã được đặt thành {channel.mention}.\n\n"
                f"📌 Khi bạn ở trong **voice channel**, mọi tin nhắn bạn gửi vào {channel.mention} "
                f"sẽ được bot đọc to.\n\n"
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
        """Tắt TTS tự động."""
        if ctx.guild.id not in self._tts_channels:
            embed = discord.Embed(
                description="ℹ️ TTS chưa được bật trong server này.",
                color=COLOR
            )
            return await ctx.reply(embed=embed, mention_author=False)

        await self._clear_tts(ctx.guild.id)

        # Disconnect bot nếu đang ở VC chỉ vì TTS
        guild_vc = ctx.guild.voice_client
        if guild_vc and not isinstance(guild_vc, wavelink.Player) and not guild_vc.is_playing():
            await guild_vc.disconnect()

        embed = discord.Embed(
            title="<:tick:1453391589148983367> TTS Đã Tắt",
            description="✅ Tính năng TTS tự động đã được tắt cho server này.",
            color=COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)

    @tts.command(
        name="status",
        usage="tts status",
        help="Xem kênh TTS đang được thiết lập cho server."
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tts_status(self, ctx: Context):
        """Xem trạng thái TTS."""
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
                description=f"TTS đang bật cho kênh: {ch_mention}",
                color=COLOR
            )
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)

    # ─────────────────────────────── Event Listener ─────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Tự động đọc tin nhắn trong kênh TTS đã cài."""
        # Bỏ qua: DM, bot, không có guild, không cấu hình
        if not message.guild or message.author.bot:
            return

        channel_id = self._tts_channels.get(message.guild.id)
        if not channel_id or message.channel.id != channel_id:
            return

        # Bỏ qua nếu người gửi không trong voice channel
        member = message.guild.get_member(message.author.id)
        if not member or not member.voice or not member.voice.channel:
            return

        # Bỏ qua tin nhắn trống hoặc chỉ có attachment
        text = message.content.strip()
        if not text:
            return

        # Bỏ qua lệnh bot (bắt đầu bằng prefix)
        if text.startswith(">") or text.startswith("/"):
            return

        guild_vc = message.guild.voice_client

        # Nếu đang phát nhạc Wavelink → bỏ qua
        if guild_vc and _is_wavelink_playing(guild_vc):
            return

        # Nếu bot đang nói (TTS khác) → bỏ qua (không queue)
        if guild_vc and guild_vc.is_playing():
            return

        vc_channel = member.voice.channel
        lock = self._get_lock(message.guild.id)

        async with lock:
            try:
                if guild_vc is None:
                    vc = await vc_channel.connect()
                elif guild_vc.channel != vc_channel:
                    await guild_vc.move_to(vc_channel)
                    vc = guild_vc
                else:
                    vc = guild_vc

                # Cắt text quá dài để tránh TTS quá lâu
                speak_text = text[:300]
                await _speak(vc, speak_text)

            except Exception:
                pass  # Lỗi TTS tự động không cần báo lại user
            finally:
                # Disconnect nếu không có ai còn trong VC
                vc_after = message.guild.voice_client
                if vc_after and not isinstance(vc_after, wavelink.Player):
                    if not vc_after.is_playing():
                        # Kiểm tra có ai còn trong VC không
                        if len(vc_after.channel.members) <= 1:
                            await vc_after.disconnect()
