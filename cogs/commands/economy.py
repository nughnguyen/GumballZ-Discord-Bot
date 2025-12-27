import discord
from discord.ext import commands
from utils.coins_db import CoinsDB
from utils.Tools import *

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coins_db = CoinsDB()

    def help_custom(self):
        emoji = '<a:cattoken:1449205470861459546>' 
        label = "Economy"
        description = "Manage your Coiz and transactions."
        return emoji, label, description

    @commands.hybrid_command(
        name="transfer",
        aliases=["give", "pay", "gift"],
        help="Transfer Coiz to another user.",
        usage="transfer <user> <amount>"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transfer(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.bot:
            await ctx.send("You cannot send Coiz to bots.")
            return
        if member.id == ctx.author.id:
            await ctx.send("You cannot send Coiz to yourself.")
            return
        if amount <= 0:
            await ctx.send("Amount must be positive.")
            return

        # Check balance
        sender_balance = await self.coins_db.get_player_points(ctx.author.id, 0) # 0 for global
        if sender_balance < amount:
            await ctx.send(f"You do not have enough Coiz. Current balance: **{int(sender_balance):,}**")
            return

        # Perform transfer
        await self.coins_db.add_points(ctx.author.id, 0, -amount)
        await self.coins_db.add_points(member.id, 0, amount)

        emoji = "<a:cattoken:1449205470861459546>"
        await ctx.send(f"💸 Successfully transferred **{amount:,}** Coiz {emoji} to {member.mention}!")

    @commands.hybrid_command(
        name="balance",
        aliases=["bal", "wallet", "coiz", "money"],
        help="Check your Coiz balance.",
        usage="balance [user]"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        balance = await self.coins_db.get_player_points(target.id, 0)
        emoji = "<a:cattoken:1449205470861459546>"
        
        embed = discord.Embed(
            title=f"{target.display_name}'s Balance",
            color=0xFF0000,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Coiz", value=f"**{int(balance):,}** {emoji}", inline=False)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name="add_coiz", aliases=["addcoiz", "give_coiz"])
    @commands.is_owner()
    async def add_coiz(self, ctx, member: discord.Member, amount: int):
        """Adds Coiz to a user."""
        if amount <= 0:
            await ctx.send("Amount must be positive.")
            return
            
        await self.coins_db.add_points(member.id, 0, amount)
        await ctx.send(f"<:tick:1453391589148983367> Successfully added **{amount:,}** Coiz to {member.mention}.")

    @commands.command(name="remove_coiz", aliases=["removecoiz", "take_coiz"])
    @commands.is_owner()
    async def remove_coiz(self, ctx, member: discord.Member, amount: int):
        """Removes Coiz from a user."""
        if amount <= 0:
            await ctx.send("Amount must be positive.")
            return
            
        await self.coins_db.add_points(member.id, 0, -amount)
        await ctx.send(f"<:tick:1453391589148983367> Successfully removed **{amount:,}** Coiz from {member.mention}.")
