import discord
import json
import random
import asyncio
import os
import utils.emojis as emojis

class VuaTiengVietGame:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.questions = []
        self.active_games = {} # channel_id -> data
        self.load_questions()

        # Constants (replicated from MarbleSoda config)
        self.POINTS_BASE = 5000
        self.POINTS_KHO = 25000
        self.POINTS_SIEU_KHO = 250000
        self.DATA_PATH = os.path.join("data", "vua_tieng_viet.json")

    def load_questions(self):
        try:
            path = os.path.join(os.getcwd(), "data", "vua_tieng_viet.json")
            if not os.path.exists(path):
                # Try relative to the script if absolute fails
                path = os.path.join(os.path.dirname(__file__), "..", "data", "vua_tieng_viet.json")
            
            with open(path, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            print(f"✅ Loaded {len(self.questions)} Vua Tieng Viet questions")
        except Exception as e:
            print(f"❌ Error loading Vua Tieng Viet questions: {e}")
            self.questions = []

    def shuffle_word(self, text):
        clean_text = "".join(filter(str.isalnum, text)).lower()
        chars = list(clean_text)
        random.shuffle(chars)
        return "/".join(chars)

    def generate_hint_text(self, question, revealed_indices):
        words = question.split()
        hint_parts = []
        global_idx = 0
        for word in words:
            word_parts = []
            for char in word:
                if char.isalnum():
                    if global_idx in revealed_indices:
                        word_parts.append(char.upper())
                    else:
                        word_parts.append("⬜")
                    global_idx += 1
            if word_parts:
                hint_parts.append("\u00A0".join(word_parts))
        return " - ".join(hint_parts)

    def cancel_timer(self, channel_id):
        if channel_id in self.active_games:
            task = self.active_games[channel_id].get("timer_task")
            if task and not task.done():
                task.cancel()

    async def hint_timer(self, channel, correct_answer):
        try:
            while True:
                await asyncio.sleep(45)
                if channel.id not in self.active_games: return
                
                game_data = self.active_games[channel.id]
                if game_data["answer"] != correct_answer or game_data["state"] != "playing": return
                
                revealed = game_data["revealed_indices"]
                total_chars = game_data["total_chars"]
                
                available = [i for i in range(total_chars) if i not in revealed]
                if available:
                    pick = random.choice(available)
                    revealed.add(pick)
                    
                    new_hint = self.generate_hint_text(correct_answer, revealed)
                    scrambled = game_data["scrambled"]
                    
                    embed = discord.Embed(
                        title="👑 Vua Tiếng Việt - Gợi Ý", 
                        description="⏳ Đã qua 45s! Bot mở giúp bạn 1 ô chữ:", 
                        color=0xFFA500
                    )
                    embed.add_field(name="Câu hỏi", value=f"**```\n{scrambled.upper()}\n```**", inline=False)
                    embed.add_field(name="Gợi ý đang mở", value=f"**{new_hint}**", inline=False)
                    embed.set_footer(text="⚠️ Điểm thưởng sẽ bị trừ tương ứng với số ô được mở sẵn.")
                    
                    await channel.send(embed=embed)
                else:
                    break
        except asyncio.CancelledError:
            pass

    async def start_new_round(self, channel):
        self.cancel_timer(channel.id)

        if not self.questions:
            await channel.send("❌ Không có dữ liệu câu hỏi!")
            return

        question = random.choice(self.questions)
        scrambled = self.shuffle_word(question)
        
        attempts = 0
        clean_question = "".join(filter(str.isalnum, question)).lower()
        while scrambled.replace('/', '') == clean_question and len(clean_question) > 1 and attempts < 5:
             scrambled = self.shuffle_word(question)
             attempts += 1
        
        total_chars = len(clean_question)
        revealed_indices = set()
        hint_text = self.generate_hint_text(question, revealed_indices)

        embed = discord.Embed(
            title="👑 Vua Tiếng Việt", 
            description="Sắp xếp các chữ cái sau thành từ hoặc câu có nghĩa:", 
            color=0xFFD700
        )
        embed.add_field(name="Câu hỏi", value=f"**```\n{scrambled.upper()}\n```**", inline=False)
        embed.add_field(name="Gợi ý số chữ", value=f"**{hint_text}**", inline=False)
        
        if len(question) > 25:
             reward_text = f"🔥 **SIÊU KHÓ** (>25 ký tự): **{self.POINTS_SIEU_KHO:,}** {emojis.ANIMATED_EMOJI_COIZ}"
        elif len(question) > 15:
             reward_text = f"🔥 **KHÓ** (>15 ký tự): **{self.POINTS_KHO:,}** {emojis.ANIMATED_EMOJI_COIZ}"
        else:
             reward_text = f"**{self.POINTS_BASE:,}** {emojis.ANIMATED_EMOJI_COIZ}"
        
        embed.add_field(name="🎁 Phần Thưởng", value=reward_text, inline=False)
        embed.set_footer(text="Gõ câu trả lời chính xác vào kênh chat! Dùng lệnh stop để dừng game.")

        await channel.send(embed=embed)
        
        task = self.bot.loop.create_task(self.hint_timer(channel, question))

        self.active_games[channel.id] = {
            "answer": question,
            "scrambled": scrambled,
            "state": "playing",
            "total_chars": total_chars,
            "revealed_indices": revealed_indices,
            "timer_task": task
        }

    async def start(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            channel = interaction_or_ctx.channel
            user = interaction_or_ctx.user
            guild_id = interaction_or_ctx.guild_id
            await interaction_or_ctx.response.send_message("🎮 Bắt đầu chuỗi game Vua Tiếng Việt!", ephemeral=True)
        else:
            channel = interaction_or_ctx.channel
            user = interaction_or_ctx.author
            guild_id = interaction_or_ctx.guild.id
            await interaction_or_ctx.send("🎮 Bắt đầu chuỗi game Vua Tiếng Việt!")

        if channel.id in self.active_games:
             return

        await self.start_new_round(channel)

        # Main game loop to handle answers
        while channel.id in self.active_games:
            try:
                def check(m):
                    return m.channel.id == channel.id and not m.author.bot

                message = await self.bot.wait_for('message', check=check, timeout=3600) # 1 hour timeout per message
                
                if channel.id not in self.active_games: break
                game_data = self.active_games[channel.id]
                if game_data["state"] != "playing": continue

                content = message.content.strip().lower()
                
                # Check for stop command
                if content in ["stop", ">vua-tieng-viet stop", ">vtv stop"]:
                    if message.author.id == user.id or message.author.guild_permissions.manage_messages:
                        await self.stop_game(channel)
                        break

                correct_answer = game_data["answer"]
                user_clean = " ".join(content.split())
                target_clean = " ".join(correct_answer.lower().split())

                if user_clean == target_clean:
                    self.cancel_timer(channel.id)
                    self.active_games[channel.id]["state"] = "waiting"
                    
                    revealed_count = len(game_data.get("revealed_indices", []))
                    total_chars = game_data.get("total_chars", 1)
                    
                    if len(correct_answer) > 25:
                        current_points = self.POINTS_SIEU_KHO
                    elif len(correct_answer) > 15:
                        current_points = self.POINTS_KHO
                    else:
                        current_points = self.POINTS_BASE
                    
                    points = int(current_points * (total_chars - revealed_count) / total_chars)
                    await self.db.add_points(message.author.id, guild_id, points)
                    
                    embed = discord.Embed(title=f"{emojis.EMOJI_GIVEAWAY} CHÚC MỪNG CHIẾN THẮNG!", color=0x00FF00)
                    embed.description = f"👑 {message.author.mention} đã trả lời chính xác!\n\nĐáp án: **{correct_answer}**"
                    embed.add_field(name="Phần thưởng", value=f"{points:,} coiz {emojis.ANIMATED_EMOJI_COIZ}\n(Trừ gợi ý: -{current_points - points:,} coiz {emojis.ANIMATED_EMOJI_COIZ})", inline=False)
                    
                    if len(correct_answer) > 25:
                       embed.set_footer(text=f"🔥 > 25 KÝ TỰ: SIÊU TO KHỔNG LỒ ({self.POINTS_SIEU_KHO:,} coiz!)")
                    elif len(correct_answer) > 15:
                       embed.set_footer(text=f"🔥 > 15 KÝ TỰ: THƯỞNG LỚN ({self.POINTS_KHO:,} coiz!)")
                    else:
                       embed.set_footer(text=f"Chuẩn bị câu tiếp theo trong 5 giây...")
                    
                    await channel.send(embed=embed)
                    await asyncio.sleep(5)
                    
                    if channel.id in self.active_games:
                        await self.start_new_round(channel)

            except asyncio.TimeoutError:
                await self.stop_game(channel)
                break
            except Exception as e:
                print(f"Error in VuaTiengViet loop: {e}")
                break

    async def stop_game(self, channel):
        if channel.id in self.active_games:
            self.cancel_timer(channel.id)
            game_data = self.active_games.pop(channel.id)
            msg = "🛑 Game đã kết thúc!"
            if game_data.get("state") == "playing":
                msg += f" Đáp án là: **{game_data['answer']}**"
            await channel.send(msg)
