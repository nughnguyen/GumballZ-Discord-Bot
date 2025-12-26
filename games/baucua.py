import discord
import asyncio
import random
import utils.emojis as emojis

COLOR_INFO = 0x3498db
COLOR_WARNING = 0xf1c40f
COLOR_SUCCESS = 0x2ecc71

class BetModal(discord.ui.Modal):
    def __init__(self, side_name, side_emoji, current_balance, callback_func):
        super().__init__(title=f"Đặt Cược: {side_name}")
        self.current_balance = current_balance
        self.callback_func = callback_func
        self.side_name = side_name
        self.side_emoji = side_emoji

        self.amount = discord.ui.TextInput(
            label=f"Số tiền cược (Có: {current_balance:,.0f})",
            placeholder="Nhập số tiền hoặc 'all' để tất tay...",
            min_length=1,
            max_length=20, 
            required=True
        )
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            raw_value = self.amount.value.lower().strip()
            
            if raw_value in ["all", "all in", "tat ca", "hết"]:
                 amount = self.current_balance
            else:
                 amount = float(self.amount.value.replace(',', '').replace('.', ''))
            
            if amount <= 0:
                await interaction.response.send_message("❌ Số tiền cược phải lớn hơn 0!", ephemeral=True)
                return
            
            await self.callback_func(interaction, amount, self.side_name, self.side_emoji)

        except ValueError:
            await interaction.response.send_message("❌ Vui lòng nhập số hợp lệ!", ephemeral=True)

class PlayAgainView(discord.ui.View):
    def __init__(self, host_id, timeout=60):
        super().__init__(timeout=timeout)
        self.host_id = host_id
        self.choice = None
        self.next_interaction = None

    @discord.ui.button(label="Chơi Tiếp", style=discord.ButtonStyle.success)
    async def continue_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.host_id:
             await interaction.response.send_message("❌ Chỉ chủ phòng mới được chọn!", ephemeral=True)
             return
        self.choice = "continue"
        self.next_interaction = interaction
        self.stop()

    @discord.ui.button(label="Dừng Lại", style=discord.ButtonStyle.danger)
    async def stop_game(self, interaction: discord.Interaction, button: discord.ui.Button):
         if interaction.user.id != self.host_id:
             await interaction.response.send_message("❌ Chỉ chủ phòng mới được chọn!", ephemeral=True)
             return
         self.choice = "stop"
         self.next_interaction = interaction
         self.stop()

class BauCuaView(discord.ui.View):
    def __init__(self, bot, db, host_id, timeout=120):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.db = db
        self.host_id = host_id
        self.bets = {} # {user_id: {side: amount}}
        self.user_total_bet = {} # {user_id: total_amount}
        self.locked_balance = {} # {user_id: locked_amount}
        self.message = None
        self.stop_event = asyncio.Event()
        
        self.sides = [
            {"id": "side_1", "name": "Nai", "emoji": emojis.SIDE_1},
            {"id": "side_2", "name": "Bầu", "emoji": emojis.SIDE_2},
            {"id": "side_3", "name": "Mèo", "emoji": emojis.SIDE_3},
            {"id": "side_4", "name": "Cá", "emoji": emojis.SIDE_4},
            {"id": "side_5", "name": "Cua", "emoji": emojis.SIDE_5},
            {"id": "side_6", "name": "Tôm", "emoji": emojis.SIDE_6},
        ]

        for i, side in enumerate(self.sides):
            btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                emoji=side['emoji'],
                label=f" {side['name']} ", 
                custom_id=side['id'],
                row=0 if i < 3 else 1
            )
            btn.callback = self.create_callback(side)
            self.add_item(btn)

        self.spin_btn = discord.ui.Button(
            label="QUAY NGAY!", 
            style=discord.ButtonStyle.success,
            emoji="🎲",
            row=2,
            custom_id="spin_now"
        )
        self.spin_btn.callback = self.spin_callback
        self.add_item(self.spin_btn)

    def create_callback(self, side):
        async def callback(interaction: discord.Interaction):
            points = await self.db.get_player_points(interaction.user.id, interaction.guild_id)
            locked = self.locked_balance.get(interaction.user.id, 0)
            available = points - locked
            
            modal = BetModal(
                side_name=side['name'], 
                side_emoji=side['emoji'],
                current_balance=available, 
                callback_func=self.process_bet
            )
            await interaction.response.send_modal(modal)
        return callback

    async def process_bet(self, interaction: discord.Interaction, amount, side_name, side_emoji):
        user_id = interaction.user.id
        
        points = await self.db.get_player_points(interaction.user.id, interaction.guild_id)
        locked = self.locked_balance.get(user_id, 0)
        
        if (locked + amount) > points:
            await interaction.response.send_message(f"❌ Bạn không đủ tiền! (Đã cược: {locked:,.0f}, muốn cược thêm: {amount:,.0f})", ephemeral=True)
            return

        self.locked_balance[user_id] = locked + amount
        new_locked = self.locked_balance[user_id]
        
        if user_id not in self.bets:
            self.bets[user_id] = {}
            self.user_total_bet[user_id] = 0
            
        current_side_bet = self.bets[user_id].get(side_name, 0)
        self.bets[user_id][side_name] = current_side_bet + amount
        self.user_total_bet[user_id] += amount
        
        remaining = points - new_locked
        
        await interaction.response.send_message(
            f"✅ Đã cược **{amount:,.0f}** coiz {emojis.ANIMATED_EMOJI_COIZ} vào {side_emoji} {side_name}!\n"
            f"Số dư khả dụng: **{remaining:,.0f}** coiz {emojis.ANIMATED_EMOJI_COIZ}", 
            ephemeral=True
        )

    async def spin_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.host_id:
            await interaction.response.send_message("❌ Chỉ người tạo phòng mới được bấm quay!", ephemeral=True)
            return
        
        self.stop_event.set() 
        await interaction.response.defer()
        self.stop() 

    async def update_embed(self):
        if not self.message: return
        try:
            embed = self.message.embeds[0]
            
            total_pot = sum(self.user_total_bet.values())
            total_players = len(self.bets)
            embed.set_field_at(0, name="💰 Tổng Cược", value=f"**{total_pot:,.0f}** coiz {emojis.ANIMATED_EMOJI_COIZ} ({total_players} người chơi)", inline=False)
            
            bet_details = []
            for uid, user_bets in self.bets.items():
                b_str = []
                for s_name, amt in user_bets.items():
                    s_emoji = next((s['emoji'] for s in self.sides if s['name'] == s_name), "")
                    b_str.append(f"{s_emoji} {amt:,.0f}")
                bet_details.append(f"<@{uid}>: " + " | ".join(b_str))
            
            val = "\n".join(bet_details) if bet_details else "Chưa có cược"
            if len(val) > 1024: val = val[:1000] + "..."
            
            if len(embed.fields) > 1:
                embed.set_field_at(1, name="📝 Danh sách cược", value=val, inline=False)
            else:
                embed.add_field(name="📝 Danh sách cược", value=val, inline=False)

            await self.message.edit(embed=embed, view=self)
        except Exception:
            pass

class BauCuaGame:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.sides_map = {
            "Nai": emojis.SIDE_1,
            "Bầu": emojis.SIDE_2,
            "Mèo": emojis.SIDE_3,
            "Cá": emojis.SIDE_4,
            "Cua": emojis.SIDE_5,
            "Tôm": emojis.SIDE_6
        }
        self.sides_list = list(self.sides_map.keys())

    async def animate_waiting(self, view: BauCuaView):
        while not view.stop_event.is_set():
            if view.message:
                try:
                    await view.update_embed()
                except Exception:
                    pass
            await asyncio.sleep(1.0)

    async def start(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            host_id = interaction_or_ctx.user.id
            host_name = interaction_or_ctx.user.display_name
        else:
            host_id = interaction_or_ctx.author.id
            host_name = interaction_or_ctx.author.display_name
            
        current_act = interaction_or_ctx
        
        while True:
            await self.run_round(current_act)
            
            play_again_view = PlayAgainView(host_id)
            try:
                msg = await current_act.channel.send(
                    f"**{host_name}**, bạn có muốn tiếp tục chơi Bầu Cua không?", 
                    view=play_again_view
                )
            except Exception:
                break
            
            await play_again_view.wait()
            
            if play_again_view.choice == "continue":
                current_act = play_again_view.next_interaction
                try:
                    await msg.delete()
                except:
                    pass
                continue
            else:
                if play_again_view.next_interaction:
                    await play_again_view.next_interaction.response.send_message("👋 Cảm ơn đã chơi! Hẹn gặp lại.", ephemeral=True)
                try:
                    await msg.edit(view=None)
                except:
                    pass
                break

    async def run_round(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            host = interaction_or_ctx.user
            guild_id = interaction_or_ctx.guild_id
        else:
            host = interaction_or_ctx.author
            guild_id = interaction_or_ctx.guild.id

        embed = discord.Embed(
            title="🎲 BẦU CUA TÔM CÁ 🎲",
            description=(
                f"Hãy đặt cược vào các cửa bên dưới!\n"
                f"Tối đa cược: **không giới hạn**, có thể đặt cược nhiều lần\n"
                f"Nhập **all** để đặt cược toàn bộ tiền\n"
                f"Người tạo phòng: {host.mention}\n"
                f"⚠️ Tiền sẽ được trừ và cộng sau khi quay xong!"
            ),
            color=COLOR_INFO
        )
        
        embed.add_field(name="💰 Tổng Cược", value=f"**0** coiz {emojis.ANIMATED_EMOJI_COIZ} (0 người chơi)", inline=False)
        embed.set_image(url="https://media.discordapp.net/attachments/1449574237734965311/1449574316361519175/bau-cua.jpg?ex=693f64c8&is=693e1348&hm=55e841a05991f0f8d26114203ffb8b28def31e942729034aaa7cd0245f46ef58&=&format=webp&width=1240&height=829")
        embed.add_field(name="📝 Danh sách cược", value="Chưa có cược", inline=False)

        view = BauCuaView(self.bot, self.db, host.id, timeout=120)
        
        if isinstance(interaction_or_ctx, discord.Interaction):
            await interaction_or_ctx.response.send_message(embed=embed, view=view)
            view.message = await interaction_or_ctx.original_response()
        else:
            view.message = await interaction_or_ctx.send(embed=embed, view=view)
        
        anim_task = asyncio.create_task(self.animate_waiting(view))
        await view.wait()
        
        view.stop_event.set()
        await asyncio.sleep(0.5) 
        anim_task.cancel()

        valid_bets = {} 
        current_balances = {} 
        
        for uid, user_bets in view.bets.items():
            total_bet_req = sum(user_bets.values())
            
            if uid not in current_balances:
                current_balances[uid] = await self.db.get_player_points(uid, guild_id)
            
            balance = current_balances[uid]
            
            if balance >= total_bet_req:
                valid_bets[uid] = user_bets
                await self.db.add_points(uid, guild_id, -total_bet_req)
                current_balances[uid] -= total_bet_req
            else:
                try:
                     await view.message.channel.send(f"⚠️ <@{uid}> không đủ tiền để thực hiện cược (Cần: {total_bet_req:,.0f}, Có: {balance:,.0f}). Hủy cược!")
                except: pass
        
        load_embed = discord.Embed(
            title="🎲 ĐANG QUAY...",
            description="",
            color=COLOR_WARNING
        )
        
        def format_reveal(revealed_indices, results):
            slots = []
            for i in range(3):
                if i in revealed_indices:
                    slots.append(self.sides_map[results[i]])
                else:
                    slots.append(emojis.LOADING)
            return " | ".join(slots)

        result_names = [random.choice(self.sides_list) for _ in range(3)]
        
        load_embed.description = f"# {emojis.LOADING} | {emojis.LOADING} | {emojis.LOADING}"
        await view.message.edit(embed=load_embed, view=None)
        await asyncio.sleep(1.5)
        
        load_embed.description = f"# {format_reveal([0], result_names)}"
        await view.message.edit(embed=load_embed)
        await asyncio.sleep(1.5)
        
        load_embed.description = f"# {format_reveal([0, 1], result_names)}"
        await view.message.edit(embed=load_embed)
        await asyncio.sleep(1.5)
        
        final_desc = f"# {format_reveal([0, 1, 2], result_names)}"
        load_embed.description = final_desc
        await view.message.edit(embed=load_embed)
        await asyncio.sleep(1)

        summary_lines = []
        
        for user_id, user_bets in valid_bets.items():
            total_bet = sum(user_bets.values())
            total_payout = 0
            win_details = []
            
            for side_name, amount in user_bets.items():
                count = result_names.count(side_name)
                if count > 0:
                    profit = amount * count
                    payout_for_side = amount + profit
                    total_payout += payout_for_side
                    side_emoji = self.sides_map[side_name]
                    win_details.append(f"{side_emoji} x{count} (+{profit:,.0f})")

            if total_payout > 0:
                await self.db.add_points(user_id, guild_id, total_payout)

            net_outcome = total_payout - total_bet
            user_mention = f"<@{user_id}>"
            
            if net_outcome > 0:
                detail_str = ", ".join(win_details)
                line = f"🎉 {user_mention}: **+{net_outcome:,.0f}** {emojis.ANIMATED_EMOJI_COIZ}\n   ╚ {detail_str}"
                summary_lines.append(line)
            elif net_outcome == 0:
                line = f"😐 {user_mention}: **Hòa vốn** {emojis.ANIMATED_EMOJI_COIZ}"
                summary_lines.append(line)
            else:
                line = f"💸 {user_mention}: **{net_outcome:,.0f}** {emojis.ANIMATED_EMOJI_COIZ}"
                summary_lines.append(line)

        result_emojis = [self.sides_map[name] for name in result_names]
        result_str = " ".join(result_emojis)
        end_embed = discord.Embed(
            title=f"🎲 KẾT QUẢ: {result_str}",
            color=COLOR_SUCCESS
        )
        end_embed.description = final_desc + "\n\n"
        
        if summary_lines:
            end_embed.add_field(name="📊 Tổng Kết", value="\n".join(summary_lines), inline=False)
        else:
            end_embed.add_field(name="😅 Kết Quả", value="Không có người chơi nào đặt cược!", inline=False)
            
        await view.message.edit(embed=end_embed)
