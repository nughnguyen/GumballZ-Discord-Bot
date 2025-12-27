import discord
from discord.ext import commands
import os
from core import Cog, gumballz, Context
import games as games
from utils.Tools import *
from games import button_games as btn
from games import BauCuaGame, VuaTiengVietGame, WordChainGame
from utils.coins_db import CoinsDB
import random
import asyncio
import utils.game_utils as gu



class Games(Cog):
    """GumballZ Games"""

    def __init__(self, client: gumballz):
        self.client = client
        self.coins_db = CoinsDB()
        asyncio.create_task(self.coins_db.initialize())
        self.word_chain_game = WordChainGame(client, self.coins_db)

    def help_custom(self):
        emoji = '<:games:1453391627329470726>'
        label = "Games"
        description = "Play games with friends or bot."
        return emoji, label, description



    @commands.hybrid_command(name="chess",
                             help="Play Chess with a user.",
                             usage="Chess <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _chess(self, ctx: Context, player: discord.Member, bet: int = 0):
        if player == ctx.author:
            await ctx.send("You Cannot play game with yourself!",
                           mention_author=False)
        elif player.bot:
            await ctx.send("You cannot play with bots!")
        else:
            if not await gu.handle_pvp_bet_start(ctx, self.coins_db, player, bet):
                 return
                 
            game = btn.BetaChess(white=ctx.author, black=player)
            await game.start(ctx)
            
            winner = game.winner
            if winner:
                 loser = player if winner == ctx.author else ctx.author
                 await gu.process_bet_result(ctx, self.coins_db, winner, loser, bet, guild_id=0)
            else:
                 await gu.process_bet_result(ctx, self.coins_db, None, None, bet, tie=True, guild_id=0)


    @commands.hybrid_command(name="rps",
                             help="Play Rock Paper Scissor with bot/user.",
                             aliases=["rockpaperscissors"],
                             usage="Rockpaperscissors [member] [bet]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _rps(self, ctx: Context, player: discord.Member = None, bet: int = 0):
        if player and player.bot:
             # Assuming 'player' argument might capture the bot if mentioned, or passed as None implies Bot.
             # But usually users ping a bot to play against it? 
             # The code previously just initialized with 'player'. 
             # If player is None -> Bot. If player is Bot -> Bot?
             pass 

        if player and not player.bot:
             # PvP
             if not await gu.handle_pvp_bet_start(ctx, self.coins_db, player, bet):
                 return
             game = btn.BetaRockPaperScissors(player)
             await game.start(ctx, timeout=120)
             
             winner = game.winner
             if winner:
                 loser = player if winner == ctx.author else ctx.author
                 await gu.process_bet_result(ctx, self.coins_db, winner, loser, bet, guild_id=0)
             elif hasattr(game, 'winner') and game.winner is None: # Tie
                 await gu.process_bet_result(ctx, self.coins_db, None, None, bet, tie=True, guild_id=0)
                 
        else:
             # PvBot (player is None)
             if bet > 0:
                 if not await gu.check_balance(self.coins_db, ctx.author.id, bet):
                     await ctx.send(f"You don't have enough Coiz to bet {bet}!")
                     return
             
             game = btn.BetaRockPaperScissors(player) # player is None or Bot
             await game.start(ctx, timeout=120)
             
             # Logic regarding Bot game rewards
             # If bet > 0:
             #   Win: Author gets +bet (doubles money basically? Or just gets bet amount?)
             #        Usually betting 100 means you put 100, if win you get 100 back + 100 profit. 
             #        Our 'add_points' just adds X. 
             #        If I bet 100 against Bot:
             #           Start: Check > 100.
             #           Win: +100. (Net +100).
             #           Lose: -100. (Net -100).
             
             winner = game.winner
             if winner == ctx.author:
                 if bet > 0:
                      await ctx.send(f"You beat the bot and won **{bet} Coiz**!")
                      await self.coins_db.add_points(ctx.author.id, 0, bet)
                 else:
                      # Default reward? "Those not needing bet will get Coiz"
                      reward = 100
                      await ctx.send(f"You beat the bot! Reward: {reward} Coiz.")
                      await self.coins_db.add_points(ctx.author.id, 0, reward)
             elif winner is None and str(game.embed.description).startswith("**Tie"):
                 pass # Tie
             else: 
                 # User Lost (winner is None but not Tie, or specific indicator)
                 # In my RPS modification: Tie -> winner=None. User Win -> winner=User. User Lost (Bot Win) -> winner=None.
                 # I need to distinguish Tie vs Loss.
                 # I can check game.embed.description.
                 desc = str(game.embed.description)
                 if "Tie!" not in desc and "You Won!" not in desc:
                      # Loss
                      if bet > 0:
                           await ctx.send(f"You lost **{bet} Coiz** to the bot!")
                           await self.coins_db.add_points(ctx.author.id, 0, -bet)

    @commands.hybrid_command(name="tic-tac-toe",
                             help="play tic-tac-toe game with a user.",
                             aliases=["ttt", "tictactoe"],
                             usage="Ticktactoe <member> [bet]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(5, per=commands.BucketType.user, wait=False)
    @commands.guild_only()
    async def _ttt(self, ctx: Context, player: discord.Member, bet: int = 0):
        if player == ctx.author:
            await ctx.send("You Cannot play game with yourself!",
                           mention_author=False)
        elif player.bot:
            await ctx.send("You cannot play with bots!")
        else:
            if not await gu.handle_pvp_bet_start(ctx, self.coins_db, player, bet):
                 return
                 
            game = btn.BetaTictactoe(cross=ctx.author, circle=player)
            await game.start(ctx, timeout=30)
            
            winner = game.winner
            if winner:
                 loser = player if winner == ctx.author else ctx.author
                 await gu.process_bet_result(ctx, self.coins_db, winner, loser, bet, guild_id=0)
            else:
                 await gu.process_bet_result(ctx, self.coins_db, None, None, bet, tie=True, guild_id=0)

    @commands.hybrid_command(name="wordle",
                             help="Wordle Game | Play with bot.",
                             usage="Wordle")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _wordle(self, ctx: Context):
        game = games.Wordle()
        await game.start(ctx, timeout=120)
        
        if getattr(game, 'won', False):
             reward = 200
             emoji = "<a:cattoken:1449205470861459546>"
             await ctx.send(f"🎉 You won Wordle! Here is **{reward} Coiz** {emoji}!")
             await self.coins_db.add_points(ctx.author.id, 0, reward)

    @commands.hybrid_command(name="2048",
                             help="Play 2048 game with bot.",
                             aliases=["twenty48"],
                             usage="2048")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _2048(self, ctx: Context):
        game = btn.BetaTwenty48()
        await game.start(ctx, win_at=2048)
        
        if getattr(game, 'won', False):
             reward = 200
             emoji = "<a:cattoken:1449205470861459546>"
             await ctx.send(f"🎉 You reached 2048! Here is **{reward} Coiz** {emoji}!")
             await self.coins_db.add_points(ctx.author.id, 0, reward)

    @commands.hybrid_command(name="memory-game",
                             help="How strong is your memory?",
                             aliases=["memory"],
                             usage="memory-game")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _memory(self, ctx: Context):
        game = btn.MemoryGame()
        await game.start(ctx)

    @commands.hybrid_command(name="number-slider",
                             help="slide numbers with bot",
                             aliases=["slider"],
                             usage="slider")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _number_slider(self, ctx: Context):
        game = btn.NumberSlider()
        await game.start(ctx)

    @commands.hybrid_command(name="battleship",
                             help="Play battleship game with your friend.",
                             aliases=["battle-ship"],
                             usage="battleship <user> [bet]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _battle(self, ctx: Context, player: discord.Member, bet: int = 0):
        if player.bot:
             await ctx.send("You cannot play with bots!")
             return

        if not await gu.handle_pvp_bet_start(ctx, self.coins_db, player, bet):
             return
             
        game = btn.BetaBattleShip(player1=ctx.author, player2=player)
        await game.start(ctx)
        
        winner = game.winner
        if winner:
             loser = player if winner == ctx.author else ctx.author
             await gu.process_bet_result(ctx, self.coins_db, winner, loser, bet, guild_id=0)

    @commands.group(name="country-guesser",
                    help="Guess name of the country by flag.",
                    aliases=["guess", "guesser", "countryguesser"],
                    usage="country-guesser")
    @commands.guild_only()
    async def _country_guesser(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("country-guesser")

    @_country_guesser.command(name="start",
                              help="Starts the country guesser game. It's a 100 Seconds Game so suggested to play in a SPECIFIC CHANNEL.")
    async def _start_country_guesser(self, ctx: Context):
        game = games.CountryGuesser(is_flags=True, hints=2)
        await game.start(ctx)

    """@_country_guesser.command(name="end",
                              help="Ends the country guesser game.")
    async def _end_country_guesser(self, ctx: Context):
        await self.country_guesser_game.end_game_manually(ctx)"""

    @commands.hybrid_command(name="connectfour",
                             help="Play Connect Four game with user.",
                             aliases=["c4", "connect-four", "connect4"],
                             usage="connectfour <user> [bet]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    @commands.guild_only()
    async def _connectfour(self, ctx: Context, player: discord.Member, bet: int = 0):
        if player == ctx.author:
            await ctx.send("You cannot play against yourself!")
        elif player.bot:
            await ctx.send("You cannot play with bots!")
        else:
            if not await gu.handle_pvp_bet_start(ctx, self.coins_db, player, bet):
                 return
                 
            game = games.ConnectFour(red=ctx.author, blue=player)  
            await game.start(ctx, timeout=300)
            
            winner = game.winner
            if winner:
                 loser = player if winner == ctx.author else ctx.author
                 await gu.process_bet_result(ctx, self.coins_db, winner, loser, bet, guild_id=0)
            else:
                 await gu.process_bet_result(ctx, self.coins_db, None, None, bet, tie=True, guild_id=0)



    @commands.hybrid_command(name="lights-out",
                             help="Play Lights Show game with bot.",
                             aliases=["lightsout"],
                             usage="Lights-out")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(3, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _lights_show(self, ctx: Context):
        game = btn.LightsOut()
        await game.start(ctx)

    @commands.command(name="bau-cua",
                             help="Play Bau Cua Tom Ca game.",
                             aliases=["baucua", "bc"],
                             usage="bau-cua")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    async def _baucua(self, ctx: Context):
        try:
            game = BauCuaGame(self.client, self.coins_db)
            await game.start(ctx)
        except Exception as e:
            await ctx.send(f"⚠️ Error starting Bau Cua: {e}")
            import traceback
            traceback.print_exc()

    @commands.command(name="vua-tieng-viet",
                             help="Play Vua Tiếng Việt game.",
                             aliases=["vtv"],
                             usage="vua-tieng-viet")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    async def _vtv(self, ctx: Context):
        try:
            game = VuaTiengVietGame(self.client, self.coins_db)
            await game.start(ctx)
        except Exception as e:
            await ctx.send(f"⚠️ Error starting Vua Tiếng Việt: {e}")
            import traceback
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_message(self, message):
        if hasattr(self, 'word_chain_game') and self.word_chain_game:
            await self.word_chain_game.on_message(message)

    @commands.command(name="noi-tu",
                             help="Play Vietnamese Word Chain game.",
                             aliases=["nt"],
                             usage="noi-tu [stop]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    async def _noitu(self, ctx: Context, option: str = None):
        if option and option.lower() in ["stop", "end"]:
            if ctx.channel.id in self.word_chain_game.active_games:
                # Check permissions: Host or Admin
                game = self.word_chain_game.active_games[ctx.channel.id]
                if ctx.author.id == game['first_player_id'] or ctx.author.guild_permissions.manage_messages:
                    await self.word_chain_game.stop_game(ctx.channel)
                    await ctx.send("🛑 Đã dừng game!", delete_after=5)
                else:
                    await ctx.send("⚠️ Chỉ người tạo phòng hoặc Admin mới được dừng game!", delete_after=5)
            else:
                await ctx.send("⚠️ Không có game nào đang chạy ở kênh này!", delete_after=5)
            return

        await self.word_chain_game.start(ctx, "vi")

    @commands.command(name="wordchain",
                             help="Play English Word Chain game.",
                             aliases=["wc"],
                             usage="wordchain [stop]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    async def _wordchain(self, ctx: Context, option: str = None):
        if option and option.lower() in ["stop", "end"]:
            if ctx.channel.id in self.word_chain_game.active_games:
                # Check permissions
                game = self.word_chain_game.active_games[ctx.channel.id]
                if ctx.author.id == game['first_player_id'] or ctx.author.guild_permissions.manage_messages:
                    await self.word_chain_game.stop_game(ctx.channel)
                    await ctx.send("🛑 Game stopped!", delete_after=5)
                else:
                    await ctx.send("⚠️ Only the host or Admin can stop the game!", delete_after=5)
            else:
                await ctx.send("⚠️ No game running in this channel!", delete_after=5)
            return

        await self.word_chain_game.start(ctx, "en")

    @commands.group(name="fishing",
                             help="Games Commands\nGames\nblackjack , bau-cua, chess , tic-tac-toe , country-guesser , rps , lights-out , wordle , 2048 , memory-game , number-slider , battleship , connect-four , slots, counting, vua-tieng-viet, noi-tu, wordchain, fishing",
                             aliases=["fish"],
                             usage="fishing [option]")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.channel, wait=False)
    @commands.guild_only()
    async def _fishing(self, ctx: Context):
         if ctx.invoked_subcommand is None:
             # Default action: FISH
             game = games.FishingGame(self.client, self.coins_db)
             await game.fish(ctx)

    @_fishing.command(name="biomes", aliases=["khu-vuc", "map"])
    async def _fishing_biomes(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.biomes_cmd(ctx)

    @_fishing.command(name="shop", aliases=["st"])
    async def _fishing_shop(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.shop(ctx)

    @_fishing.command(name="bag", aliases=["inventory", "tui"])
    async def _fishing_inv(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.inventory(ctx)

    @_fishing.command(name="sell", aliases=["ban"])
    async def _fishing_sell(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.sell(ctx)
         
    @_fishing.command(name="stats", aliases=["profile"])
    async def _fishing_stats(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.fish_stats_cmd(ctx)

    @_fishing.command(name="goi-rong", aliases=["summon"])
    async def _fishing_summon(self, ctx: Context):
         game = games.FishingGame(self.client, self.coins_db)
         await game.summon_shenron(ctx)
