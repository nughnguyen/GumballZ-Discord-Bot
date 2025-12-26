import discord
from discord.ext import commands, tasks
import urllib.parse
import aiohttp
import os
import time
import random
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Cấu hình Donation từ .env
# Account 1 (Casso)
BANK_ID_1 = os.getenv("BANK_ID", "OCB") 
ACCOUNT_NO_1 = os.getenv("BANK_ACCOUNT_NO", "CASS1808QUOCHUNG") 
ACCOUNT_NAME_1 = os.getenv("BANK_ACCOUNT_NAME", "NGUYEN QUOC HUNG") 

# Account 2 (SePay)
BANK_ID_2 = os.getenv("BANK_ID_2", "OCB")
ACCOUNT_NO_2 = os.getenv("BANK_ACCOUNT_NO_2", "SEPQUOCHUNG1808")
ACCOUNT_NAME_2 = os.getenv("BANK_ACCOUNT_NAME_2", "NGUYEN QUOC HUNG")

PHONE_NUMBER = os.getenv("MOMO_PHONE", "0388205003")
WEB_URL = os.getenv("DONATION_WEB_URL", "https://gumballzhub.vercel.app")
TEMPLATE = os.getenv("TEMPLATE", "compact") 

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def generate_invoice(interaction: discord.Interaction, ctx, amount: int, method: str, supabase: Client):
    """Hàm chung để tạo và gửi hóa đơn thanh toán"""
    expiry_seconds = 600 # 10 phút
    expiry_timestamp = int(time.time() + expiry_seconds)
    trans_code = f"GUMZ{random.randint(100000, 999999)}"
    
    # Tính Coiz nhận được
    coiz_received = (amount // 1000) * 10000
    if amount >= 50000:
        coiz_received = int(coiz_received * 1.1)

    # Lựa chọn ngẫu nhiên tài khoản ngân hàng (Load balancing)
    # 0: Primary (Casso), 1: Secondary (SePay)
    selected_acc = random.choice([
        {"id": BANK_ID_1, "no": ACCOUNT_NO_1, "name": ACCOUNT_NAME_1},
        {"id": BANK_ID_2, "no": ACCOUNT_NO_2, "name": ACCOUNT_NAME_2}
    ])
    
    # Nếu thông tin acc 2 chưa đủ, fallback về acc 1
    if not selected_acc["no"]: 
        selected_acc = {"id": BANK_ID_1, "no": ACCOUNT_NO_1, "name": ACCOUNT_NAME_1}

    # 1. Tạo giao dịch trên Supabase
    if supabase:
        try:
            data = {
                "user_id": str(ctx.author.id),
                "user_name": ctx.author.name,
                "amount": amount,
                "coiz_reward": coiz_received,
                "trans_code": trans_code,
                "method": method,
                "status": "pending",
                "handled": False,
                "expires_at": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(expiry_timestamp))
            }
            supabase.table("transactions").insert(data).execute()
        except Exception as e:
            error_str = str(e)
            if "42703" in error_str or "column" in error_str:
                 print(f"❌ [DB Error] Bảng 'transactions' thiếu cột! Vui lòng chạy file 'supabase_schema.sql'.")
            print(f"Lỗi tạo giao dịch Supabase: {e}")

    # 2. Tạo link Web & QR
    content_safe = urllib.parse.quote(trans_code)
    params = {
        "amount": amount,
        "content": trans_code,
        "method": method,
        "userId": ctx.author.id,
        "userName": ctx.author.name,
        "expiry": expiry_timestamp
    }
    query_string = urllib.parse.urlencode(params)
    web_link = f"{WEB_URL}/payment?{query_string}"
    
    # QR Generation URL
    qr_url = ""
    if method == "VIETQR" or method == "VNPAY":
        qr_url = f"https://img.vietqr.io/image/{selected_acc['id']}-{selected_acc['no']}-{TEMPLATE}.png?amount={amount}&addInfo={content_safe}&accountName={urllib.parse.quote(selected_acc['name'])}"
    elif method == "MOMO":
        momo_link = f"https://me.momo.vn/{PHONE_NUMBER}?money={amount}&note={content_safe}"
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(momo_link)}"

    # Embed Hóa Đơn
    embed = discord.Embed(title="💳 Thanh Toán", color=discord.Color.gold())
    
    method_display = method
    if method != "MOMO":
        method_display = f"{method} ({selected_acc['id']})"

    embed.description = (
        f"Bạn đã chọn nạp **{amount:,} VND** qua **{method_display}**.\n"
        f"Sẽ nhận được: **{coiz_received:,} Coiz** <a:cattoken:1449205470861459546>\n\n"
        f"⚠️ **LƯU Ý QUAN TRỌNG:**\n"
        f"1. Nội dung chuyển khoản: `{trans_code}`\n"
        f"2. Thời gian còn lại: **{expiry_seconds // 60} phút tới** (Hết hạn lúc <t:{expiry_timestamp}:T>)\n"
        f"3. Nếu chuyển khoản khi hết hạn: **KHÔNG ĐƯỢC TÍNH & KHÔNG CHỊU TRÁCH NHIỆM.**\n"
    )
    if qr_url:
        embed.set_image(url=qr_url)
        
    embed.set_footer(text=f"Mã giao dịch: {trans_code} • Vui lòng quét mã QR để chính xác nhất.")
    embed.timestamp = discord.utils.utcnow()
    
    # Thumbnail - Use User Avatar as requested
    if ctx.author:
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
    else:
        embed.set_thumbnail(url="https://i.pinimg.com/564x/a7/67/6f/a7676f23602519199d3434674722880a.jpg")

    # View with Payment Button
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="THANH TOÁN NGAY", url=web_link, style=discord.ButtonStyle.link, emoji="💸"))
    
    # Reply 
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class AmountModal(discord.ui.Modal):
    def __init__(self, ctx, method, supabase):
        super().__init__(title="Nhập số tiền bạn muốn nạp")
        self.ctx = ctx
        self.method = method
        self.supabase = supabase
        
        self.amount_input = discord.ui.TextInput(
            label="Số tiền (VND)",
            placeholder="Ví dụ: 10000, 20000, 50000...",
            min_length=4,
            max_length=9,
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value.replace(",", "").replace(".", "")) # Remove separators if user types 10.000
            if amount < 1000:
                return await interaction.response.send_message("❌ Số tiền tối thiểu là 1,000 VND.", ephemeral=True)
            
            await generate_invoice(interaction, self.ctx, amount, self.method, self.supabase)
            
        except ValueError:
            await interaction.response.send_message("❌ Vui lòng nhập một số hợp lệ.", ephemeral=True)

class PaymentMethodView(discord.ui.View):
    def __init__(self, ctx, amount, supabase: Client):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.amount = amount
        self.supabase = supabase

    async def handle_click(self, interaction: discord.Interaction, method: str):
        if self.amount:
            # Nếu đã có số tiền (nhập từ lệnh), tạo hóa đơn luôn
            await generate_invoice(interaction, self.ctx, self.amount, method, self.supabase)
        else:
            # Nếu chưa có, hiện Modal nhập tiền
            await interaction.response.send_modal(AmountModal(self.ctx, method, self.supabase))

    @discord.ui.button(label="MOMO", style=discord.ButtonStyle.primary, emoji="<:momo:1449636713247936512>")
    async def btn_momo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "MOMO")

    @discord.ui.button(label="VNPAY", style=discord.ButtonStyle.primary, emoji="👛")
    async def btn_vnpay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "VNPAY")

    @discord.ui.button(label="VIETQR", style=discord.ButtonStyle.success, emoji="🏦")
    async def btn_vietqr(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_click(interaction, "VIETQR")

class QR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase: Client = None
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("✅ [QR] Connected to Supabase!")
            except Exception as e:
                print(f"❌ [QR] Supabase connection failed: {e}")
        
        self.check_transactions.start()

    def cog_unload(self):
        self.check_transactions.cancel()

    @commands.command(
        name="donate",
        aliases=["qr", "qrcode", "momo", "banking", "nap"],
        help="Nạp Coiz ủng hộ bot.",
        description="Mở menu nạp Coiz tự động.",
        with_app_command=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx, amount: int = None):
        # Kiểm tra min amount nếu có
        if amount and amount < 1000:
            return await ctx.reply("❌ Số tiền tối thiểu là 1,000 VND.")

        # Hiển thị Embed Chính ngay lập tức
        embed = discord.Embed(
            title="💎 NẠP COIZ | ỦNG HỘ SERVER",
            description=(
                "Chào mừng bạn đến với hệ thống nạp Coiz tự động 24/7!\n\n"
                "🎁 **QUYỀN LỢI KHI NẠP COIZ**\n"
                "✨ Tham gia các minigame giải trí\n"
                "✨ Đua Top Tỷ Phú Server\n"
                "✨ Mua các vật phẩm/quyền lợi (sắp ra mắt)\n"
                "❤️ Góp phần duy trì Bot hoạt động ổn định\n\n"
                "💰 **TỶ GIÁ QUY ĐỔI:**\n"
                "💵 `1,000 VND = 10,000 Coiz` <a:cattoken:1449205470861459546>\n"
                "🔥 **Khuyến mãi:** Tặng thêm 10% khi nạp trên 50k!\n"
                "🎣 **Đặc biệt:** Nạp tối thiểu **10,000 VND** nhận ngay **Cần Nhà Tài Trợ** (Donator Rod)!\n\n"
                "💳 **PHƯƠNG THỨC THANH TOÁN:**\n"
                "1. **MOMO** – Ví điện tử thông dụng\n"
                "2. **VNPAY** – Quét mã tiện lợi\n"
                "3. **VIETQR** – Chuyển khoản mọi ngân hàng (MB, VCB, OCB...)\n\n"
                "👇 **Chọn phương thức thanh toán bên dưới để bắt đầu:**"
            ),
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1305044754173661245/1321744654512984094/money.gif") 
        embed.set_image(url="https://media.discordapp.net/attachments/1305044754173661245/1321743602128551988/thenoicez_banner.png")
        embed.set_footer(text="Hệ thống xử lý tự động trong vài giây • Cảm ơn bạn đã ủng hộ!")
        
        view = PaymentMethodView(ctx, amount, self.supabase)
        await ctx.reply(embed=embed, view=view)

    @tasks.loop(seconds=60)
    async def check_transactions(self):
        """Kiểm tra các giao dịch 'pending' xem đã chuyển sang 'completed' chưa trong Supabase"""
        if not self.supabase: return
        
        try:
            # Lấy các giao dịch có status='completed' NHƯNG chưa xử lý logic cộng tiền (handled=False)
            response = self.supabase.table("transactions").select("*").eq("status", "completed").eq("handled", False).execute()
            transactions = response.data
            
            if not transactions: return

            for tx in transactions:
                try:
                    user_id = int(tx['user_id'])
                    amount_coiz = tx['coiz_reward']
                    trans_code = tx['trans_code']
                    
                    # 1. Update handled=True ngay lập tức
                    self.supabase.table("transactions").update({"handled": True}).eq("id", tx['id']).execute()
                    
                    # 2. Add Coins Logic
                    from utils import coins_db
                    user = self.bot.get_user(user_id)
                    
                    # Notify User
                    if user:
                        try:
                            await user.send(
                                f"✅ **THANH TOÁN THÀNH CÔNG!**\n"
                                f"Mã giao dịch: `{trans_code}`\n"
                                f"Bạn đã nhận được: **{amount_coiz:,} Coiz** <a:cattoken:1449205470861459546>\n"
                                "Cảm ơn bạn đã ủng hộ GumballZ!"
                            )
                        except: pass
                    
                    print(f"✅ [Payment] Processed {trans_code} for User {user_id} (+{amount_coiz} Coiz)")
                    
                except Exception as inner_e:
                     print(f"❌ Error processing TX {tx.get('id')}: {inner_e}")

        except Exception as e:
            error_str = str(e)
            if "42703" in error_str or "column" in error_str:
                print(f"❌ [DB Error] Bảng 'transactions' thiếu cột! Vui lòng chạy file 'supabase_schema.sql' trong Supabase.")
            else:
                 print(f"⚠ Error querying Supabase: {e}")

    @check_transactions.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(QR(bot))
