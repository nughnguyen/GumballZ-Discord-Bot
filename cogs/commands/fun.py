import discord
from discord.ext import commands
import random
import aiohttp
from discord import app_commands
from utils.Tools import blacklist_check, ignore_check

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giphy_api_key = "y3KcqQTdiS0RYcpNJrWn8hFGglKqX4is"

    async def red_footer(self, embed, ctx):
        embed.set_footer(text="GumballZ™ Pro Mode", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.color = 0xFF0000
        return embed

    async def fetch_giphy(self, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_api_key}&q={query}&limit=30&rating=pg") as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data['data']:
                    return random.choice(data['data'])['images']['original']['url']
                else:
                    return None

    def random_emoji(self):
        return random.choice(["😂", "🤣", "😆", "😳", "🥴", "🙃", "😜"])

    async def action_command(self, ctx, user: discord.Member, action: str):
        gif_url = await self.fetch_giphy(action)
        if not gif_url:
            await ctx.send("**Bruh 😒, GIPHY API is sleeping. Try later!**")
            return
        embed = discord.Embed(description=f"**{ctx.author.mention} {action}s {user.mention} {self.random_emoji()}**")
        embed.set_image(url=gif_url)
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command(name="shipp")
    @blacklist_check()
    @ignore_check()
    async def shipp(self, ctx, user1: discord.Member, user2: discord.Member):
        percentage = random.randint(0, 100)
        embed = discord.Embed(title=f"{self.random_emoji()} Ship Result", description=f"**{user1.mention} x {user2.mention} = {percentage}% Love**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def hug(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "hug")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def kiss(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "kiss")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def pat(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "pat")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def slap(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "slap")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def tickle(self, ctx, user: discord.Member):
        await self.action_command(ctx, user, "tickle")

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"**Result: {result}**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dice(self, ctx):
        result = random.randint(1, 6)
        embed = discord.Embed(title="🎲 Dice Roll", description=f"**You rolled a {result}!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command(name="8ball")
    @blacklist_check()
    @ignore_check()
    async def eight_ball(self, ctx, *, question: str):
        responses = ["It is certain.", "Without a doubt.", "You may rely on it.",
                     "Ask again later.", "Better not tell you now.",
                     "Don't count on it.", "My sources say no.", "Very doubtful."]
        embed = discord.Embed(title="🎱 Magic 8Ball", description=f"**Q:** {question}\n**A:** {random.choice(responses)}")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def roast(self, ctx, user: discord.Member):
        roasts = [
            f"{user.mention} you're the reason shampoo has instructions!",
            f"{user.mention} you have something on your chin... no, the third one down!",
            f"{user.mention} your secrets are safe with me. I never even listen when you tell me them."
        ]
        embed = discord.Embed(title="🔥 Roast Time", description=random.choice(roasts))
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def iq(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        iq_value = random.randint(50, 200)
        embed = discord.Embed(title="🧠 IQ Test", description=f"**{user.mention} has an IQ of {iq_value}!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def dumb(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        dumbness = random.randint(0, 100)
        embed = discord.Embed(title="🤪 Dumbness Test", description=f"**{user.mention} is {dumbness}% dumb!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def simprate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        simp_level = random.randint(0, 100)
        embed = discord.Embed(title="😳 Simp Rate", description=f"**{user.mention} is {simp_level}% simp!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def toxic(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        toxic_level = random.randint(0, 100)
        embed = discord.Embed(title="☠️ Toxic Meter", description=f"**{user.mention} is {toxic_level}% toxic!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def intelligence(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        intelligence = random.randint(0, 200)
        embed = discord.Embed(title="🧠 Intelligence Meter", description=f"**{user.mention} has {intelligence} IQ Points!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def genius(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        genius_level = random.randint(0, 100)
        embed = discord.Embed(title="🤓 Genius Rate", description=f"**{user.mention} is {genius_level}% genius!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def brainrate(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        brain_power = random.randint(0, 100)
        embed = discord.Embed(title="🧠 Brain Power", description=f"**{user.mention} is using {brain_power}% of their brain!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

    @commands.command()
    @blacklist_check()
    @ignore_check()
    async def howhot(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        hotness = random.randint(0, 100)
        embed = discord.Embed(title="🔥 Hotness Meter", description=f"**{user.mention} is {hotness}% hot!**")
        await ctx.send(embed=await self.red_footer(embed, ctx))

async def setup(bot):
    await bot.add_cog(Fun(bot))