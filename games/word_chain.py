
import discord
from discord import ui
import asyncio
import random
import time
import os
import datetime
from typing import List, Dict, Optional, Tuple
from discord.ext import commands

import utils.emojis as emojis
from utils.validator import WordValidator
# Try importing dictionary service, if fails (e.g. not initialized), handle gracefully
try:
    from utils.dictionary_api import dictionary_service
except ImportError:
    dictionary_service = None

# ================= CONFIGURATION =================
class GameConfig:
    WORDS_VI_PATH = os.path.join("data", "words_vi.txt")
    WORDS_EN_PATH = os.path.join("data", "words_en.txt")
    DEFAULT_LANGUAGE = "vi"
    
    REGISTRATION_TIMEOUT = 60
    TURN_TIMEOUT = 15 # Seconds
    
    HINT_COST = 100
    PASS_COST = 20
    
    MIN_WORD_LENGTH_EN = 3
    
    POINTS_CORRECT = 10
    POINTS_LONG_WORD = 200 # English long word / Viet long word
    POINTS_TIMEOUT = -10
    POINTS_WRONG = -2
    
    MAX_WRONG_ATTEMPTS = 5
    LONG_WORD_THRESHOLD = 8 # Characters
    
    COLOR_INFO = 0x3498db
    COLOR_SUCCESS = 0x2ecc71
    COLOR_ERROR = 0xe74c3c
    COLOR_WARNING = 0xf1c40f
    COLOR_GOLD = 0xf1c40f
    
    LEVEL_BONUS = {
        'a1': 0, 'a2': 0,
        'b1': 10, 'b2': 20,
        'c1': 50, 'c2': 100,
        'academic': 30, 'formal': 20, 'literary': 30, 'specialized': 40
    }

# ================= HELPERS (Embeds & Views) =================

class RegistrationView(ui.View):
    def __init__(self, host_id: int, timeout: float):
        super().__init__(timeout=timeout)
        self.host_id = host_id
        self.registered_players = {host_id} # Host auto-registered
        self.game_started = False

    @ui.button(label="📝 Đăng Ký", style=discord.ButtonStyle.success, emoji="✅")
    async def join_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id in self.registered_players:
            await interaction.response.send_message("Bạn đã đăng ký rồi!", ephemeral=True)
            return
        
        self.registered_players.add(interaction.user.id)
        await self.update_embed(interaction)
        await interaction.response.send_message("Đăng ký thành công!", ephemeral=True)

    @ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary, emoji="🚪")
    async def leave_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in self.registered_players:
            await interaction.response.send_message("Bạn chưa đăng ký!", ephemeral=True)
            return
        
        if interaction.user.id == self.host_id:
             await interaction.response.send_message("Chủ phòng không thể hủy đăng ký! Hãy đợi hết giờ hoặc bắt đầu solo.", ephemeral=True)
             return

        self.registered_players.remove(interaction.user.id)
        await self.update_embed(interaction)
        await interaction.response.send_message("Đã hủy đăng ký!", ephemeral=True)

    @ui.button(label="🎮 Bắt Đầu", style=discord.ButtonStyle.primary, emoji="🚀")
    async def start_button(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("Chỉ chủ phòng mới được bắt đầu game!", ephemeral=True)
            return
        
        self.game_started = True
        self.stop()
        await interaction.response.defer()

    async def update_embed(self, interaction: discord.Interaction):
        try:
            embed = interaction.message.embeds[0]
            players = []
            for uid in self.registered_players:
                players.append(f"<@{uid}>")
                
            player_list_str = "\n".join(players) if players else "Chưa có ai"
            
            # Update field 0 (Players list)
            embed.set_field_at(0, name=f"👥 Đã Đăng Ký ({len(self.registered_players)} người)", value=player_list_str, inline=False)
            
            await interaction.message.edit(embed=embed)
        except Exception as e:
            print(f"Error updating registration embed: {e}")

class EmbedFactory:
    @staticmethod
    def create_rich_correct_answer_embed(author: discord.User, word: str, word_info: dict, meaning_vi: str, points: int, bonus_reason: str):
        embed = discord.Embed(
            title=f"{word.upper()}",
            color=GameConfig.COLOR_SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=f"Chính xác! - {author.display_name}", icon_url=author.display_avatar.url)
        
        desc_lines = []
        phonetic = ""
        if word_info and word_info.get('phonetic'):
            phonetic = f" /{word_info['phonetic']}/"
        if phonetic:
            desc_lines.append(f"`{phonetic}`")
        if meaning_vi:
            desc_lines.append(f"\n🇻🇳 Nghĩa:\n**{meaning_vi}**")
        embed.description = "".join(desc_lines)
        
        if word_info and word_info.get('audio_url'):
            embed.url = word_info['audio_url']
            
        if points > 0:
            embed.add_field(name="Từ hợp lệ", value=f"+{GameConfig.POINTS_CORRECT:,}", inline=True)
            bonuses = [b.strip() for b in bonus_reason.split('\n') if b.strip()] if bonus_reason else []
            for bonus in bonuses:
                embed.add_field(name="Bonus", value=bonus, inline=True)
            if bonuses:
                embed.add_field(name="Tổng cộng", value=f"**+{points:,}** {emojis.ANIMATED_EMOJI_COIZ}", inline=False)
        return [embed]

    @staticmethod
    def create_wrong_answer_embed(player_mention: str, word: str, reason: str):
        embed = discord.Embed(
            title=f"{emojis.get_random_wrong_emoji()} Sai Rồi!",
            description=f"{player_mention} - Từ **{word}** không hợp lệ",
            color=GameConfig.COLOR_ERROR,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Lý Do", value=reason, inline=False)
        embed.add_field(name="Coiz Bị Trừ", value=f"{GameConfig.POINTS_WRONG:,} Coiz {emojis.ANIMATED_EMOJI_COIZ}", inline=True)
        return embed

    @staticmethod
    def create_timeout_embed(player_mention: str):
        embed = discord.Embed(
            title=f"{emojis.TIMEOUT} Hết Giờ!",
            description=f"{player_mention} {emojis.SNAIL} đã không trả lời kịp thời! ({GameConfig.POINTS_TIMEOUT} Coiz)",
            color=GameConfig.COLOR_WARNING,
            timestamp=discord.utils.utcnow()
        )
        return embed

    @staticmethod
    def create_game_end_embed(winner_data: Dict, total_turns: int, used_words_count: int):
        embed = discord.Embed(
            title=f"{emojis.END} Trò Chơi Kết Thúc! {emojis.CELEBRATION}",
            description=f"Tổng số lượt chơi: **{total_turns}**\nTổng số từ đã dùng: **{used_words_count}**",
            color=GameConfig.COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        if winner_data:
            session_text = f"**{winner_data['session_points']:,} Coiz** {emojis.ANIMATED_EMOJI_COIZ}"
            embed.add_field(name=f"{emojis.CROWN} Người Chiến Thắng", value=f"<@{winner_data['user_id']}> vòng này kiếm được: {session_text}", inline=False)
        embed.set_footer(text="Cảm ơn đã chơi!")
        return embed

    @staticmethod
    def create_status_embed(game_state: Dict):
        embed = discord.Embed(title=f"{emojis.SCROLL} Trạng Thái Game", color=GameConfig.COLOR_INFO, timestamp=discord.utils.utcnow())
        embed.add_field(name="Từ Hiện Tại", value=f"```{game_state['current_word'].upper()}```", inline=False)
        embed.add_field(name="Người Chơi Hiện Tại", value=f"<@{game_state['current_player_id']}>", inline=True)
        embed.add_field(name="Số Từ Đã Dùng", value=str(len(game_state['used_words'])), inline=True)
        embed.add_field(name="Số Lượt", value=str(game_state['turn_count']), inline=True)
        return embed

    @staticmethod
    def create_hint_embed(hint: str, cost: int):
        embed = discord.Embed(title=f"{emojis.HINT} Gợi Ý", description=f"Từ tiếp theo bắt đầu bằng: **{hint}**", color=GameConfig.COLOR_INFO, timestamp=discord.utils.utcnow())
        embed.add_field(name="Chi Phí", value=f"-{cost:,} Coiz {emojis.ANIMATED_EMOJI_COIZ}", inline=True)
        return embed


# ================= MAIN GAME CLASS =================

class WordChainGame:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.validators = {}
        self.active_games = {} # In-memory storage: channel_id -> state dict
        self.active_timeouts = {} # channel_id -> asyncio.Task
        
        # Load words
        asyncio.create_task(self.load_word_lists())

    async def load_word_lists(self):
        fallback_words = {}

        # Vietnamese
        try:
            path_vi = GameConfig.WORDS_VI_PATH
            if not os.path.exists(path_vi): path_vi = os.path.join(os.getcwd(), path_vi)
            
            with open(path_vi, 'r', encoding='utf-8') as f:
                words_vi = [line.strip() for line in f if line.strip()]
            self.validators['vi'] = WordValidator('vi', words_vi)
            fallback_words['vi'] = set(words_vi)
            print(f"✅ Loaded {len(words_vi)} Vietnamese words")
        except Exception as e:
            print(f"❌ Error loading Vietnamese words: {e}")
            self.validators['vi'] = WordValidator('vi', [])
            fallback_words['vi'] = set()

        # English
        try:
            path_en = GameConfig.WORDS_EN_PATH
            if not os.path.exists(path_en): path_en = os.path.join(os.getcwd(), path_en)

            with open(path_en, 'r', encoding='utf-8') as f:
                words_en = [line.strip() for line in f if line.strip()]
            self.validators['en'] = WordValidator('en', words_en)
            fallback_words['en'] = set(words_en)
            print(f"✅ Loaded {len(words_en)} English words")
        except Exception as e:
            print(f"❌ Error loading English words: {e}")
            self.validators['en'] = WordValidator('en', [])
            fallback_words['en'] = set()
            
        # Initialize Dictionary Service for API support
        try:
            from utils.dictionary_api import init_dictionary_service
            await init_dictionary_service(use_api=True, fallback_words=fallback_words)
            print("✅ Dictionary API Service Initialized")
        except Exception as e:
             print(f"❌ Failed to initialize Dictionary API: {e}")

    def get_random_word(self, language: str) -> str:
        validator = self.validators.get(language)
        if validator and validator.word_list:
            return random.choice(list(validator.word_list))
        return "start" if language == "en" else "bat dau"

    async def start(self, interaction_or_ctx, language: str = "vi"):
        # Support both Context and Interaction
        if isinstance(interaction_or_ctx, commands.Context):
            author = interaction_or_ctx.author
            channel = interaction_or_ctx.channel
            send_method = interaction_or_ctx.send
            user_id = author.id
            guild_id = interaction_or_ctx.guild.id
        else:
            author = interaction_or_ctx.user
            channel = interaction_or_ctx.channel
            send_method = interaction_or_ctx.response.send_message
            user_id = author.id
            guild_id = interaction_or_ctx.guild_id

        if channel.id in self.active_games:
            msg = f"{emojis.ANIMATED_EMOJI_WRONG} Đã có game đang chơi!"
            if isinstance(interaction_or_ctx, discord.Interaction):
                await send_method(msg, ephemeral=True)
            else:
                await send_method(msg)
            return

        if language not in self.validators:
            msg = f"{emojis.ANIMATED_EMOJI_WRONG} Ngôn ngữ '{language}' chưa được hỗ trợ!"
            if isinstance(interaction_or_ctx, discord.Interaction):
                 await send_method(msg, ephemeral=True)
            else:
                 await send_method(msg)
            return

        # Registration
        lang_flag = "🇻🇳" if language == "vi" else "🇬🇧"
        lang_name = "Tiếng Việt" if language == "vi" else "English"
        reg_end_time = int(time.time() + GameConfig.REGISTRATION_TIMEOUT)

        reg_embed = discord.Embed(
            title=f"{emojis.START} Đăng Ký Tham Gia Game!",
            description=f"**Ngôn ngữ:** {lang_flag} {lang_name}\n⏳ Kết thúc đăng ký: <t:{reg_end_time}:R>",
            color=GameConfig.COLOR_INFO
        )
        reg_embed.add_field(name="👥 Đã Đăng Ký (0 người)", value="Chưa có ai", inline=False)
        reg_embed.add_field(name="📋 Hướng Dẫn", value=f"• Nhấn **📝 Đăng Ký** để tham gia\n• <@{user_id}> nhấn **🎮 Bắt Đầu**\n• Mỗi lượt: **{GameConfig.TURN_TIMEOUT}s**", inline=False)

        view = RegistrationView(host_id=user_id, timeout=GameConfig.REGISTRATION_TIMEOUT)
        
        if isinstance(interaction_or_ctx, discord.Interaction):
             await send_method(embed=reg_embed, view=view)
             message = await interaction_or_ctx.original_response()
             view.message = message # Hack for view to access message if needed
        else:
             message = await send_method(embed=reg_embed, view=view)
             view.message = message

        await view.wait()

        if not view.game_started:
            if channel.id not in self.active_games: # Only expire if not started
                 expire_embed = discord.Embed(title="❌ Hủy Đăng Ký", description="Hết thời gian đăng ký hoặc đã bị hủy.", color=GameConfig.COLOR_ERROR)
                 try:
                    await message.edit(embed=expire_embed, view=None)
                 except: pass
            return

        # Game Start Logic
        registered_players = list(view.registered_players)
        is_bot_challenge = len(registered_players) == 1
        
        if is_bot_challenge:
            first_player_id = registered_players[0]
            players_list = [first_player_id]
        else:
            random.shuffle(registered_players)
            players_list = registered_players
            first_player_id = players_list[0]
            
        first_word = self.get_random_word(language)

        # Initialize Game State
        self.active_games[channel.id] = {
            'guild_id': guild_id,
            'language': language,
            'current_word': first_word,
            'first_player_id': first_player_id,
            'current_player_id': first_player_id,
            'players': players_list,
            'used_words': {first_word},
            'turn_count': 0,
            'scores': {uid: 0 for uid in players_list},
            'started_at': time.time(),
            'is_bot_challenge': is_bot_challenge,
            'wrong_attempts': 0,
            'turn_start_time': time.time()
        }

        # Announcement
        start_embed = discord.Embed(
            title=f"{emojis.START} Game Bắt Đầu! {emojis.CELEBRATION}",
            description=f"**Ngôn ngữ:** {lang_flag} {lang_name}",
            color=GameConfig.COLOR_SUCCESS
        )
        start_embed.add_field(name=f"{emojis.SCROLL} Từ Đầu Tiên", value=f"```{first_word.upper()}```", inline=False)
        
        turn_end = int(time.time() + GameConfig.TURN_TIMEOUT)
        if is_bot_challenge:
             start_embed.add_field(name="🎮 Chế Độ", value=f"{emojis.ROBOT} **Bot Đưa Từ - Bạn Nối**", inline=False)
             start_embed.add_field(name=f"{emojis.TIMEOUT} Lượt Của Bạn", value=f"<@{first_player_id}> - Nối từ: **{first_word.upper()}**\nKết thúc: <t:{turn_end}:R>", inline=False)
        else:
             order_text = ""
             for idx, pid in enumerate(players_list, 1):
                marker = f"{emojis.FIRE} **→**" if pid == first_player_id else "  "
                order_text += f"{marker} **{idx}.** <@{pid}>\n"
             start_embed.add_field(name=f"👥 Thứ Tự", value=order_text, inline=False)
             start_embed.add_field(name=f"{emojis.TIMEOUT} Lượt Hiện Tại", value=f"<@{first_player_id}> - Kết thúc: <t:{turn_end}:R>", inline=False)

        await channel.send(embed=start_embed)
        await self.start_turn_timeout(channel.id, first_player_id)

    async def save_new_word(self, word: str, language: str):
        """Append a new valid word to the local dictionary file"""
        try:
            path = GameConfig.WORDS_EN_PATH if language == 'en' else GameConfig.WORDS_VI_PATH
            if not os.path.exists(path): path = os.path.join(os.getcwd(), path)
            
            def _append():
                with open(path, 'a', encoding='utf-8') as f:
                    f.write(f"\n{word}")
            
            # Use run_in_executor for file I/O to avoid blocking event loop
            await asyncio.get_running_loop().run_in_executor(None, _append)
            print(f"📝 Auto-saved new word to {language} dictionary: {word}")
        except Exception as e:
            print(f"❌ Error auto-saving new word: {e}")

    async def stop_game(self, channel):
        if channel.id not in self.active_games: return
        
        state = self.active_games[channel.id]
        
        # Determine winner
        winner_id = None
        max_score = -999999
        session_points = 0
        for uid, score in state['scores'].items():
            if score > max_score:
                max_score = score
                winner_id = uid
                session_points = score
        
        # Cleanup
        if channel.id in self.active_timeouts:
            self.active_timeouts[channel.id].cancel()
            del self.active_timeouts[channel.id]
        del self.active_games[channel.id]
        
        # Embed
        winner_data = {'user_id': winner_id, 'session_points': session_points} if winner_id else None
        embed = EmbedFactory.create_game_end_embed(winner_data, state['turn_count'], len(state['used_words'])) # Fixed: passed used_words count
        await channel.send(embed=embed)


    async def start_turn_timeout(self, channel_id, player_id):
        if channel_id in self.active_timeouts:
            self.active_timeouts[channel_id].cancel()
        
        self.active_timeouts[channel_id] = asyncio.create_task(self.timeout_handler(channel_id, player_id))

    async def timeout_handler(self, channel_id, player_id):
        try:
            await asyncio.sleep(GameConfig.TURN_TIMEOUT)
            
            if channel_id not in self.active_games: return
            state = self.active_games[channel_id]
            if state['current_player_id'] != player_id: return
            
            # Apply penalty
            await self.db.add_points(player_id, state['guild_id'], GameConfig.POINTS_TIMEOUT)
            state['scores'][player_id] = state['scores'].get(player_id, 0) + GameConfig.POINTS_TIMEOUT
            
            channel = self.bot.get_channel(channel_id)
            if channel:
                embed = EmbedFactory.create_timeout_embed(f"<@{player_id}>")
                await channel.send(embed=embed)
                
                # Next player
                next_player_id = self.get_next_player_id(state, player_id)
                await self.update_turn(channel, state, state['current_word'], next_player_id, False)

        except asyncio.CancelledError:
            pass

    def get_next_player_id(self, state, current_id):
        players = state['players']
        idx = players.index(current_id)
        return players[(idx + 1) % len(players)]

    async def update_turn(self, channel, state, word, next_player_id, from_correct_answer=True):
        state['current_word'] = word
        if from_correct_answer:
            state['used_words'].add(word)
            state['turn_count'] += 1
            state['wrong_attempts'] = 0
        
        state['current_player_id'] = next_player_id
        state['turn_start_time'] = time.time()
        
        if from_correct_answer:
             await channel.send(f"Lượt tiếp theo: <@{next_player_id}>")
        
        await self.start_turn_timeout(channel.id, next_player_id)

    async def on_message(self, message):
        if message.author.bot or message.channel.id not in self.active_games: return
        
        # FIX: Ignore valid commands (e.g. >nt stop)
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        state = self.active_games[message.channel.id]
        if state['current_player_id'] != message.author.id: return
        
        word = message.content.strip().lower()
        validator = self.validators[state['language']]
        
        # Check stop
        if word == "stop game":
             await self.stop_game(message.channel)
             return

        # V2: Min length check
        if state['language'] == 'en' and len(word) < GameConfig.MIN_WORD_LENGTH_EN:
             await message.channel.send(embed=EmbedFactory.create_wrong_answer_embed(message.author.mention, word, f"Từ tiếng Anh phải có ít nhất **{GameConfig.MIN_WORD_LENGTH_EN} chữ cái**!"))
             return

        if word in state['used_words']:
             await self.handle_wrong(message, state, word, "Từ này đã được sử dụng rồi!")
             return
            
        can_chain, reason = await validator.can_chain(state['current_word'], word)
        if not can_chain:
             await self.handle_wrong(message, state, word, reason)
             return

        # FEATURE: Auto-save new valid English words to local DB
        if state['language'] == 'en' and word not in validator.word_list:
             await self.save_new_word(word, 'en')
             validator.word_list.add(word)

        # CORRECT
        if message.channel.id in self.active_timeouts:
             self.active_timeouts[message.channel.id].cancel()

        # Logic points
        points = GameConfig.POINTS_CORRECT
        bonus_list = []
        elapsed = time.time() - state['turn_start_time']
        if elapsed < 5:
            points += 100
            bonus_list.append(f"⚡ Siêu tốc! (+100 {emojis.ANIMATED_EMOJI_COIZ})")
        elif elapsed < 10:
            points += 50
            bonus_list.append(f"🏃 Nhanh! (+50 {emojis.ANIMATED_EMOJI_COIZ})")
        
        # API meanings & Bonus
        word_info = None
        meaning_vi = None
        
        if state['language'] == 'en' and validator.cambridge_api:
             meaning_vi = await validator.cambridge_api.get_vietnamese_meaning(word)
             word_info = await validator.cambridge_api.get_word_info(word, 'en')
             if word_info and word_info.get('level'):
                  lvl = word_info['level']
                  p_lvl = GameConfig.LEVEL_BONUS.get(lvl, 0)
                  if p_lvl > 0:
                       points += p_lvl
                       bonus_list.append(f"📚 Level {lvl.upper()} (+{p_lvl} {emojis.ANIMATED_EMOJI_COIZ})")
             
             if len(word) >= GameConfig.LONG_WORD_THRESHOLD:
                  points += GameConfig.POINTS_LONG_WORD
                  bonus_list.append(f"📝 Từ dài! (+{GameConfig.POINTS_LONG_WORD})")
        
        elif validator.is_long_word(word):
             points += GameConfig.POINTS_LONG_WORD
             bonus_list.append(f"🔥 Từ dài! (+{GameConfig.POINTS_LONG_WORD})")

        # Save points
        await self.db.add_points(message.author.id, message.guild.id, points)
        state['scores'][message.author.id] = state['scores'].get(message.author.id, 0) + points
        
        bonus_reason = "\n".join(bonus_list)
        embeds_list = EmbedFactory.create_rich_correct_answer_embed(message.author, word, word_info, meaning_vi, points, bonus_reason)
        await message.channel.send(embeds=embeds_list)
        
        # Bot Challenge Logic
        if state['is_bot_challenge']:
            validator = self.validators[state['language']]
            next_char = validator.get_last_char(word)
            await message.channel.typing()
            await asyncio.sleep(1.5)
            
            bot_word = validator.get_bot_word(next_char, state['used_words'])
            if not bot_word:
                 # Win
                 win_embed = discord.Embed(title=f"{emojis.EMOJI_GIVEAWAY} Bạn Thắng!", description=f"{emojis.ROBOT} Bot đầu hàng!", color=GameConfig.COLOR_GOLD)
                 await message.channel.send(embed=win_embed)
                 await self.stop_game(message.channel)
                 return
            
            # Bot Turn
            bot_embed = discord.Embed(title=f"{emojis.ROBOT} Bot Đưa Từ Mới", description=f"```{bot_word.upper()}```", color=GameConfig.COLOR_INFO)
            await message.channel.send(embed=bot_embed)
            
            # Update state with BOT word, then pass back to player
            state['used_words'].add(bot_word)
            state['turn_count'] += 1
            await self.update_turn(message.channel, state, bot_word, message.author.id, False)

        else:
            next_pid = self.get_next_player_id(state, message.author.id)
            await self.update_turn(message.channel, state, word, next_pid, True)

    async def handle_wrong(self, message, state, word, reason):
        state['wrong_attempts'] += 1
        penalty = GameConfig.POINTS_WRONG
        
        await self.db.add_points(message.author.id, message.guild.id, penalty)
        state['scores'][message.author.id] = state['scores'].get(message.author.id, 0) + penalty
        
        if state['wrong_attempts'] >= GameConfig.MAX_WRONG_ATTEMPTS:
             await message.channel.send(embed=discord.Embed(title="Mất lượt", description=f"{message.author.mention} sai quá nhiều.", color=GameConfig.COLOR_ERROR))
             next_pid = self.get_next_player_id(state, message.author.id)
             await self.update_turn(message.channel, state, state['current_word'], next_pid, False)
        else:
             rem = GameConfig.MAX_WRONG_ATTEMPTS - state['wrong_attempts']
             await message.channel.send(embed=EmbedFactory.create_wrong_answer_embed(message.author.mention, word, f"{reason}\nCòn {rem} lần thử."))
