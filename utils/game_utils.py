import discord
from discord.ext import commands
import asyncio
from typing import Optional

# Import Emojis if possible, or define them here if circular import issues arise.
# We will just use the string provided in emojis.py if we can't import easily or pass it in.
# ANIMATED_EMOJI_COIZ = "<a:cattoken:1449205470861459546>" 

async def check_balance(coins_db, user_id, amount):
    bal = await coins_db.get_player_points(user_id, 0)
    return bal >= amount

async def process_bet_result(ctx, coins_db, winner, loser, bet, tie=False, guild_id=0):
    """
    Handles the transfer of Coiz involved in a bet.
    """
    ANIMATED_EMOJI_COIZ = "<a:cattoken:1449205470861459546>"
    
    if bet <= 0:
        return

    if tie:
        await ctx.send(f"It's a tie! No Coiz {ANIMATED_EMOJI_COIZ} exchanged.")
        return

    # Add to winner
    await coins_db.add_points(winner.id, guild_id, bet)
    # Deduct from loser
    await coins_db.add_points(loser.id, guild_id, -bet)
    
    await ctx.send(f"🏆 {winner.mention} won **{bet} Coiz** {ANIMATED_EMOJI_COIZ} from {loser.mention}!")

class ChallengeView(discord.ui.View):
    def __init__(self, author, opponent, bet, timeout=60):
        super().__init__(timeout=timeout)
        self.author = author
        self.opponent = opponent
        self.bet = bet
        self.accepted = False
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            return await interaction.response.send_message("Not your challenge!", ephemeral=True)
        self.accepted = True
        self.stop()
        
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
             return await interaction.response.send_message("Not your challenge!", ephemeral=True)
        self.accepted = False
        self.stop()

async def handle_pvp_bet_start(ctx, coins_db, opponent, bet):
    ANIMATED_EMOJI_COIZ = "<a:cattoken:1449205470861459546>"

    if bet < 0:
        await ctx.send("Bet amount cannot be negative!")
        return False
        
    if bet == 0:
        return True # Just play for fun

    # Check Author Balance
    if not await check_balance(coins_db, ctx.author.id, bet):
        await ctx.send(f"You don't have enough Coiz {ANIMATED_EMOJI_COIZ}! You need {bet} Coiz {ANIMATED_EMOJI_COIZ}.")
        return False
        
    # Check Opponent Balance
    if not await check_balance(coins_db, opponent.id, bet):
        await ctx.send(f"{opponent.mention} doesn't have enough Coiz {ANIMATED_EMOJI_COIZ}! They need {bet} Coiz {ANIMATED_EMOJI_COIZ}.")
        return False

    # Send Challenge
    view = ChallengeView(ctx.author, opponent, bet)
    msg = await ctx.send(f"{opponent.mention}, {ctx.author.name} challenges you to a game for **{bet} Coiz** {ANIMATED_EMOJI_COIZ}! Do you accept?", view=view)
    await view.wait()
    
    if view.accepted:
        # Re-check balances just in case (race condition check)
        if not await check_balance(coins_db, ctx.author.id, bet):
             await ctx.send(f"Check failed: You no longer have enough Coiz {ANIMATED_EMOJI_COIZ}.")
             return False
        if not await check_balance(coins_db, opponent.id, bet):
             await ctx.send(f"Check failed: {opponent.mention} no longer has enough Coiz {ANIMATED_EMOJI_COIZ}.")
             return False
        await msg.edit(content=f"Challenge Accepted! Game starting... (Bet: {bet} Coiz {ANIMATED_EMOJI_COIZ})", view=None)
        return True
    else:
        await msg.edit(content="Challenge declined.", view=None)
        return False
