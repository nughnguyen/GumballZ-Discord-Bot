import asyncio
import os
import platform
import random
import time

import aiohttp
import discord
from discord import Spotify
from discord.ext import commands
from dotenv import load_dotenv

from core import Context
from core.gumballz import gumballz

load_dotenv()

TOKEN = os.getenv("TOKEN")
SERVER_COUNT_CHANNEL_ID = int(os.getenv("SERVER_COUNT_CHANNEL_ID", "1453239949490126930"))
USER_COUNT_CHANNEL_ID = int(os.getenv("USER_COUNT_CHANNEL_ID", "1453240025780060231"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "1305771283199561852"))
COMMAND_LOG_WEBHOOK = os.getenv("COMMAND_LOG_WEBHOOK", "")
KEEP_ALIVE = os.getenv("KEEP_ALIVE", "false").lower() in ("1", "true", "yes")

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

client = gumballz()


async def update_stats():
    """Update server/user count channel names every 10 minutes."""
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            servers = len(client.guilds)
            users = sum(g.member_count for g in client.guilds if g.member_count is not None)

            server_channel = client.get_channel(SERVER_COUNT_CHANNEL_ID)
            user_channel = client.get_channel(USER_COUNT_CHANNEL_ID)

            if server_channel:
                await server_channel.edit(name=f"Servers: {servers}")
            if user_channel:
                await user_channel.edit(name=f"Users: {users}")
        except Exception as e:
            print(f"Error updating stats: {e}")

        await asyncio.sleep(600)


@client.event
async def on_ready():
    await client.wait_until_ready()
    print("""
        \033[1;31m
 ██████╗ ██╗   ██╗███╗   ███╗██████╗  █████╗ ██╗     ██╗     ███████╗
██╔════╝ ██║   ██║████╗ ████║██╔══██╗██╔══██╗██║     ██║     ╚══███╔╝
██║  ███╗██║   ██║██╔████╔██║██████╔╝███████║██║     ██║       ███╔╝ 
██║   ██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║██║     ██║      ███╔╝  
╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝██║  ██║███████╗███████╗███████╗
 ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
                                                                     
        \033[0m
       """)
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")
    try:
        synced = await client.tree.sync()
        print(f"Synced Total {len(list(client.commands))} Client Commands and {len(synced)} Slash Commands")
    except Exception as e:
        print(e)

    client.loop.create_task(update_stats())


@client.event
async def on_guild_join(guild: discord.Guild):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"GumballZ has been added to the server: **{guild.name}** (ID: `{guild.id}`)"
        )


@client.event
async def on_command_completion(context: commands.Context) -> None:
    if context.author.id == 561443914062757908 or not COMMAND_LOG_WEBHOOK:
        return

    executed_command = context.command.qualified_name.split("\n")[0]
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(COMMAND_LOG_WEBHOOK, session=session)
        embed = discord.Embed(color=0xFF0000)
        avatar_url = context.author.display_avatar.url
        embed.set_author(name=f"Cmd Executed: {executed_command}", icon_url=avatar_url)
        embed.set_thumbnail(url=avatar_url)

        if context.guild is not None:
            embed.add_field(name="User", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)
            embed.add_field(name="Server", value=f"{context.guild.name} (`{context.guild.id}`)", inline=False)
            embed.add_field(name="Channel", value=f"{context.channel.mention} (`{context.channel.id}`)", inline=False)
        else:
            embed.add_field(name="User (DM)", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)

        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text="GumballZ™ ❤️", icon_url=client.user.display_avatar.url)

        try:
            await webhook.send(embed=embed)
        except Exception as e:
            print(f"Command log webhook failed: {e}")


@client.command(name="spotify")
async def spotify(ctx: Context, user: discord.Member = None):
    """Shows what a user is listening to on Spotify."""
    user = user or ctx.author
    spotify_activity = next((a for a in user.activities if isinstance(a, Spotify)), None)
    if not spotify_activity:
        return await ctx.send(f"{user.name} is not listening to Spotify.")

    embed = discord.Embed(
        title=f"{user.name}'s Spotify",
        description=f"**Listening to:** {spotify_activity.title}",
        color=0x1DB954,
    )
    embed.set_thumbnail(url=spotify_activity.album_cover_url)
    embed.add_field(name="Artist", value=spotify_activity.artist)
    embed.add_field(name="Album", value=spotify_activity.album)
    embed.set_footer(text=f"Song started at {spotify_activity.created_at.strftime('%H:%M')}")
    await ctx.send(embed=embed)


@client.command(name="makeinvite", aliases=["createinvite", "makeinv"])
@commands.is_owner()
async def make_invite(ctx: Context, guild_id: int = None):
    """Creates an invite for a specified server (owner only)."""
    if guild_id is None:
        return await ctx.send("Please provide a Guild ID.")

    guild = client.get_guild(guild_id)
    if not guild:
        return await ctx.send("Invalid Guild ID. I am not in that server.")

    if guild.system_channel and guild.system_channel.permissions_for(guild.me).create_instant_invite:
        try:
            invite = await guild.system_channel.create_invite(
                max_age=0, max_uses=0, unique=True, reason="Owner requested invite."
            )
            return await ctx.send(f"Invite for **{guild.name}**:\n{invite.url}")
        except Exception:
            pass

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(
                    max_age=0, max_uses=0, unique=True, reason="Owner requested invite."
                )
                return await ctx.send(f"Invite for **{guild.name}** (from #{channel.name}):\n{invite.url}")
            except Exception:
                continue

    await ctx.send(f"I don't have 'Create Instant Invite' permission in any channel in **{guild.name}**.")


@client.command(name="create_hook", aliases=["makehook"])
@commands.has_permissions(administrator=True)
async def create_hook(ctx: Context, *, name: str = None):
    """Creates a webhook in the current channel."""
    if name is None:
        return await ctx.send("Please provide a name for the webhook.")

    try:
        webhook = await ctx.channel.create_webhook(name=name, reason=f"Created by {ctx.author}")
        embed = discord.Embed(
            title="✅ Webhook Created",
            description=f"A webhook named **{webhook.name}** was created.",
            color=0xFF0000,
        )
        await ctx.author.send(
            f"Webhook URL for **{webhook.name}** in **{ctx.channel.name}**:\n||{webhook.url}||",
            embed=embed,
        )
        await ctx.send("Webhook created. I've sent the URL to your DMs.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to create webhooks here.")
    except Exception:
        await ctx.send(f"Webhook created: **{webhook.name}**\n||{webhook.url}||\n(I could not DM you the URL.)")


@client.command(name="delete_hook", aliases=["delhook"])
@commands.has_permissions(administrator=True)
async def delete_hook(ctx: Context, webhook_url: str = None):
    """Deletes a webhook using its URL."""
    if webhook_url is None:
        return await ctx.send("Please provide the webhook URL to delete.")

    try:
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook_url, session=session)
            await webhook.delete(reason=f"Deleted by {ctx.author}")
        await ctx.send("✅ Webhook deleted successfully.")
    except (discord.NotFound, ValueError):
        await ctx.send("❌ Webhook not found or URL is invalid.")


@client.command(name="list_hooks", aliases=["hooks"])
@commands.has_permissions(administrator=True)
async def list_hooks(ctx: Context):
    """Lists all webhooks in the current channel."""
    try:
        webhooks = await ctx.channel.webhooks()
        if not webhooks:
            return await ctx.send("No webhooks found in this channel.")

        embed = discord.Embed(title=f"Webhooks in #{ctx.channel.name}", color=0xFF0000)
        embed.description = "\n".join(f"**Name:** {wh.name} | **ID:** `{wh.id}`" for wh in webhooks)
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permission to view webhooks in this channel.")


@client.command()
async def reaction(ctx: Context):
    """See how fast you can react to the correct emoji."""
    emojis = ["🍪", "🎉", "🧋", "🍒", "🍑", "💸", "🌙", "💕"]
    correct_emoji = random.choice(emojis)
    random.shuffle(emojis)

    embed = discord.Embed(
        title="Reaction Test",
        description="I will show an emoji in a few seconds. Get ready to click it!",
        color=0xFF0000,
    )
    message = await ctx.send(embed=embed)

    for emoji in emojis:
        await message.add_reaction(emoji)

    await asyncio.sleep(random.uniform(2.0, 7.0))
    embed.description = f"**GET THE {correct_emoji} EMOJI!**"
    await message.edit(embed=embed)
    start_time = time.time()

    def check(reaction_emoji, user):
        return (
            reaction_emoji.message.id == message.id
            and str(reaction_emoji.emoji) == correct_emoji
            and user == ctx.author
        )

    try:
        _, user = await client.wait_for("reaction_add", timeout=15.0, check=check)
        reaction_time = time.time() - start_time
        embed.description = f"{user.mention} got the {correct_emoji} in **{reaction_time:.2f} seconds**!"
        await message.edit(embed=embed)
    except asyncio.TimeoutError:
        embed.description = "Timeout! You were too slow."
        await message.edit(embed=embed)


def keep_alive():
    from threading import Thread
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def home():
        return "GumballZ™ 2025"

    Thread(target=lambda: app.run(host="0.0.0.0", port=19346), daemon=True).start()


async def main():
    async with client:
        os.system("cls" if platform.system() == "Windows" else "clear")
        await client.load_extension("jishaku")

        max_retries = 5
        for attempt in range(max_retries):
            try:
                await client.start(TOKEN)
                break
            except discord.HTTPException as e:
                if e.status == 429:
                    wait_time = min((2 ** attempt) + random.random(), 60)
                    print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        else:
            raise Exception("Bot failed to start after multiple retries due to rate limiting.")


if __name__ == "__main__":
    if KEEP_ALIVE:
        keep_alive()
    asyncio.run(main())
