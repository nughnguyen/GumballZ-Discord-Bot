import discord
from discord.ext import commands
from discord import app_commands, Interaction
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.gumballz import gumballz
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
from utils import help as vhelp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import asyncio
from utils.config import serverLink
from utils.Tools import *

color = 0xFF0000
client = gumballz()

class HelpCommand(commands.HelpCommand):

  async def send_ignore_message(self, ctx, ignore_type: str):
    if ignore_type == "channel":
      await ctx.reply(f"This channel is ignored.", mention_author=False)
    elif ignore_type == "command":
      await ctx.reply(f"{ctx.author.mention} This Command, Channel, or You have been ignored here.", delete_after=6)
    elif ignore_type == "user":
      await ctx.reply(f"You are ignored.", mention_author=False)

  async def on_help_command_error(self, ctx, error):
    errors = [
      commands.CommandOnCooldown, commands.CommandNotFound,
      discord.HTTPException, commands.CommandInvokeError
    ]
    if not type(error) in errors:
      await self.context.reply(f"Unknown Error Occurred\n{error.original}",
                               mention_author=False)
    else:
      if type(error) == commands.CommandOnCooldown:
        return
    return await super().on_help_command_error(ctx, error)

  async def command_not_found(self, string: str) -> None:
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
        return

    if not check_ignore:
        await self.send_ignore_message(ctx, "command")
        return

    cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
    matches = get_close_matches(string, cmds)

    embed = discord.Embed(
        title="GumballZ Helper",
        description=f">>> **Ops! Command not found with the name** `{string}`.",
        color=0xFF0000
    )
                          
    #if matches:
        #match_list = "\n".join([f"{index}. `{match}`" for index, match in enumerate(matches, start=1)])
        #embed.add_field(name="Did you mean:", value=match_list, inline=True)

    await ctx.reply(embed=embed, mention_author=True)

  async def send_bot_help(self, mapping):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    # Show loading embed
    loading_embed = discord.Embed(
      description="<a:loadingred:1453413861121069147> Loading help Menu...",
      color=0xFF0000
    )
    loading_msg = await ctx.reply(embed=loading_embed)

    # Wait 2 seconds
    await asyncio.sleep(2)

    # Delete loading message
    with suppress(discord.NotFound):
      await loading_msg.delete()

    data = await getConfig(self.context.guild.id)
    prefix = data["prefix"]
    filtered = await self.filter_commands(self.context.bot.walk_commands(), sort=True)

    embed = discord.Embed(
        description=(
         f"**<a:ArrowRed:1453413846755578079> __Start GumballZ Today__**\n"        
         f"**<:Arrow:1453391681142390876> Type {prefix}antinuke enable**\n"
         f"**<:Arrow:1453391681142390876> Server Prefix:** `{prefix}`\n"
         f"**<:Arrow:1453391681142390876> Total Commands:** `{len(set(self.context.bot.walk_commands()))}`\n"),         
        color=0xFF0000)
    embed.set_author(name=f"{ctx.author}", 
                     icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    
    embed.add_field(
        name="<:Cloud:1453391936080711680>  __**Main Features**__",
        value=">>> \n <:Safe:1453391577962643476>  `»` Security\n" 
              " <:bot:1453391686611898431>  `»` Automoderation\n"
              " <:codebase:1453391605565231105>  `»` Developer\n"
              " <:wrench:1453391598426656818>  `»` Utility\n" 
              " <:music:1453391554990313562>  `»` Music\n"
              " <:wifi:1453391596002349097>  `»` Autoreact & responder\n"
              " <:sword:1453391584694374470>  `»` Moderation\n"
              " <:people:1453391564088021152>  `»` Autorole & Invc\n"
              " <:rocket:1453391575232282818>  `»` Fun\n"
              " <:games:1453391627329470726>  `»` Games\n" 
              " <:ban:1453391684661674076>  `»` Ignore Channels\n"
              " <:wifi:1453391596002349097> `»` Server\n"
              " <:unmute:1453391593917907147>  `»` Voice\n"
              " <:seed:1453391580043153448>  `»` Welcomer\n"  
              " <:tada:1453391586737131695>  `»` Giveaway\n"
              " <:ticket:1453391591698862191>  `»` Ticket <:New:1453394998807625820>\n"
              " <:people:1453391564088021152>  `»` Invite Tracker <:New:1453394998807625820>\n"
    )
    
    embed.add_field(
        name=" <:module:1453391552029135000>  __**Extra Features**__",
        value=">>> \n <:cast:1453391688763576421>  `»` Advance Logging\n"
              " <:starr:1453391665145446400>  `»` Vanityroles\n"
              
              " <:counting:1453394890342793318>  `»` Counting <:New:1453394998807625820>\n"
              " <:system:1453395385962987630>  `»` J2C <:New:1453394998807625820>\n"
              " <:ai:1453395017681993730>  `»` AI <:New:1453394998807625820>\n"
              " <:boost:1453391600817410190>  `»` Boost <:New:1453394998807625820>\n"
              " <:levelup:1453394897309536307>  `»` Leveling <:New:1453394998807625820>\n"
              " <:pin:1453394906612633661>  `»` Sticky <:New:1453394998807625820>\n"
              " <:thunder:1453394963780862117>  `»` Verification <:New:1453394998807625820>\n"
              " <:lock:1453394996043448441>  `»` Encryption <:New:1453394998807625820>\n" 
              " <:mc:1453394900065456250>  `»` Minecraft <:New:1453394998807625820>\n"
              " <:msg:1453394902611394571>  `»` Joindm <:New:1453394998807625820>\n"
              " <:circle:1453395027211456575>  `»` Birthday <:New:1453394998807625820>\n"
              " <:circle:1453391690848276614>  `»` Customrole\n"
              " <:coin:1449205470861459546>  `»` Economy <:New:1453394998807625820>\n" 
    )

    embed.set_footer(
      text=f"Requested By {self.context.author} | [Support](https://dsc.gg/thenoicez)",
    )
    
    view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
    await ctx.reply(embed=embed, view=view)

  async def send_command_help(self, command):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    GumballZ = f">>> {command.help}" if command.help else '>>> No Help Provided...'
    embed = discord.Embed(
        description=f"""{GumballZ}""",
        color=color)
    alias = ' & '.join(command.aliases)

    embed.add_field(name="**Alt cmd**",
                      value=f"```{alias}```" if command.aliases else "No Alt cmd",
                      inline=False)
    embed.add_field(name="**Usage**",
                      value=f"```{self.context.prefix}{command.signature}```\n")
    embed.set_author(name=f"{command.qualified_name.title()} Command")
    embed.set_footer(text="<[] = optional | < > = required • Use Prefix Before Commands.")
    await self.context.reply(embed=embed, mention_author=False)

  def get_command_signature(self, command: commands.Command) -> str:
    parent = command.full_parent_name
    if len(command.aliases) > 0:
      aliases = ' | '.join(command.aliases)
      fmt = f'[{command.name} | {aliases}]'
      if parent:
        fmt = f'{parent}'
      alias = f'[{command.name} | {aliases}]'
    else:
      alias = command.name if not parent else f'{parent} {command.name}'
    return f'{alias} {command.signature}'

  def common_command_formatting(self, embed_like, command):
    embed_like.title = self.get_command_signature(command)
    if command.description:
      embed_like.description = f'{command.description}\n\n{command.help}'
    else:
      embed_like.description = command.help or 'No help found...'

  async def send_group_help(self, group):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [
        (
            f"`{self.context.prefix}{cmd.qualified_name}`\n",
            f"{cmd.short_doc if cmd.short_doc else ''}\n\u200b"
        )
        for cmd in group.commands
      ]

    count = len(group.commands)

    embeds = FieldPagePaginator(
      entries=entries,
      title=f"{group.qualified_name.title()} [{count}]",
      description="< > Duty | [ ] Optional\n",
      per_page=4
    ).get_pages()   
    
    paginator = Paginator(ctx, embeds)
    await paginator.paginate()

  async def send_cog_help(self, cog):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [(
      f"> `{self.context.prefix}{cmd.qualified_name}`",
      f"-# Description : {cmd.short_doc if cmd.short_doc else ''}"
      f"\n\u200b",
    ) for cmd in cog.get_commands()]
    paginator = Paginator(source=FieldPagePaginator(
      entries=entries,
      title=f"GumballZ's {cog.qualified_name.title()} ({len(cog.get_commands())})",
      description="`<..> Required | [..] Optional`\n\n",
      color=0xFF0000,
      per_page=4),
                          ctx=self.context)
    await paginator.paginate()


class Help(Cog, name="help"):

  def __init__(self, client: gumballz):
    self._original_help_command = client.help_command
    attributes = {
      'name': "help",
      'aliases': ['h'],
      'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
      'help': 'Shows help about bot, a command, or a category'
    }
    client.help_command = HelpCommand(command_attrs=attributes)
    client.help_command.cog = self

  async def cog_unload(self):
    self.help_command = self._original_help_command