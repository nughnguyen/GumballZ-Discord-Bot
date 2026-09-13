from __future__ import annotations

from colorama import Fore, Style

from core import gumballz

# ____________ Commands ____________
from .commands.help import Help
from .commands.general import General
from .commands.music import Music
from .commands.automod import Automod
from .commands.welcome import Welcomer
from .commands.fun import Fun
from .commands.Games import Games
from .commands.extra import Extra
from .commands.owner import Owner, Badges
from .commands.voice import Voice
from .commands.afk import afk
from .commands.ignore import Ignore
from .commands.Media import Media
from .commands.Invc import Invcrole
from .commands.giveaway import Giveaway
from .commands.Embed import Embed
from .commands.steal import Steal
from .commands.timer import Timer
from .commands.blacklist import Blacklist
from .commands.block import Block
from .commands.nightmode import Nightmode
from .commands.tracking import Tracking
from .commands.autoresponder import AutoResponder
from .commands.customrole import Customrole
from .commands.autorole import AutoRole
from .commands.ticket import TicketCog
from .commands.logging import Logging
from .commands.translate import TranslateCog
from .commands.jail import Jail
from .commands.antinuke import Antinuke
from .commands.extraown import Extraowner
from .commands.anti_wl import Whitelist
from .commands.anti_unwl import Unwhitelist
from .commands.slots import Slots
from .commands.blackjack import Blackjack
from .commands.autoreact import AutoReaction
from .commands.stats import Stats
from .commands.notify import NotifCommands
from .commands.status import Status
from .commands.np import NoPrefix
from .commands.filters import FilterCog
from .commands.owner2 import Global
from .commands.qr import QR
from .commands.vanityroles import VanityRoles
from .commands.reactionroles import ReactionRoles
from .commands.messages import Messages
from .commands.fastgreet import FastGreet
from .commands.counting import Counting
from .commands.j2c import JoinToCreate
from .commands.ai import AI
from .commands.dms import StaffDMCog
from .commands.booster import Booster
from .commands.leveling import Leveling
from .commands.stickymessage import StickyMessage
from .commands.verification import Verification
from .commands.minecraft import Minecraft
from .commands.encryption import encryption
from .commands.calc import calculator
from .commands.joindm import joindm
from .commands.Birthday import Birthdays
from .commands.nitro import Nitro
from .commands.image import ImageCommands
from .commands.youtube import Youtube
from .commands.tts import TTS

# ____________ Events ____________
from .events.Errors import Errors
from .events.on_guild import Guild
from .events.autorole import Autorole2
from .events.auto import GuildJoinDM
from .events.greet2 import greet
from .events.mention import Mention
from .events.react import React
from .events.autoreact import AutoReactListener
from .events.ai import AIResponses
from .events.stickymessage import StickyMessageListener

# ____________ Help stubs ____________
from .gumballz.antinuke import _antinuke
from .gumballz.extra import _extra
from .gumballz.general import _general
from .gumballz.automod import _automod
from .gumballz.moderation import _moderation
from .gumballz.music import _music
from .gumballz.fun import _fun
from .gumballz.games import _games
from .gumballz.ignore import _ignore
from .gumballz.server import _server
from .gumballz.voice import _voice
from .gumballz.welcome import _welcome
from .gumballz.giveaway import _giveaway
from .gumballz.ticket import _ticket
from .gumballz.logging import _logging
from .gumballz.vanity import _vanity
from .gumballz.inviteTracker import inviteTracker
from .gumballz.counting import _Counting
from .gumballz.j2c import _J2C
from .gumballz.ai import _ai
from .gumballz.booster import __boost
from .gumballz.leveling import _leveling
from .gumballz.sticky import _sticky
from .gumballz.verify import _verify
from .gumballz.encryption import _encrypt
from .gumballz.mc import _mc
from .gumballz.joindm import _joindm
from .gumballz.birth import _birth
from .gumballz.tts import _tts

# ____________ Antinuke ____________
from .antinuke.anti_member_update import AntiMemberUpdate
from .antinuke.antiban import AntiBan
from .antinuke.antibotadd import AntiBotAdd
from .antinuke.antichcr import AntiChannelCreate
from .antinuke.antichdl import AntiChannelDelete
from .antinuke.antichup import AntiChannelUpdate
from .antinuke.antieveryone import AntiEveryone
from .antinuke.antiguild import AntiGuildUpdate
from .antinuke.antiIntegration import AntiIntegration
from .antinuke.antikick import AntiKick
from .antinuke.antiprune import AntiPrune
from .antinuke.antirlcr import AntiRoleCreate
from .antinuke.antirldl import AntiRoleDelete
from .antinuke.antirlup import AntiRoleUpdate
from .antinuke.antiwebhook import AntiWebhookUpdate
from .antinuke.antiwebhookcr import AntiWebhookCreate
from .antinuke.antiwebhookdl import AntiWebhookDelete

# ____________ Automod ____________
from .automod.antispam import AntiSpam
from .automod.anticaps import AntiCaps
from .automod.antilink import AntiLink
from .automod.anti_invites import AntiInvite
from .automod.anti_mass_mention import AntiMassMention
from .automod.anti_emoji_spam import AntiEmojiSpam

# ____________ Moderation ____________
from .moderation.ban import Ban
from .moderation.unban import Unban
from .moderation.timeout import Mute
from .moderation.unmute import Unmute
from .moderation.lock import Lock
from .moderation.unlock import Unlock
from .moderation.hide import Hide
from .moderation.unhide import Unhide
from .moderation.kick import Kick
from .moderation.warn import Warn
from .moderation.role import Role
from .moderation.message import Message
from .moderation.moderation import Moderation
from .moderation.topcheck import TopCheck
from .moderation.snipe import Snipe


COGS = [
    # Commands
    Help, General, Music, Automod, Welcomer, Fun, Tracking, Games, Extra, Voice,
    Owner, Customrole, afk, Embed, Media, Ignore, Invcrole, Giveaway, Steal, Booster,
    Timer, Blacklist, Block, Nightmode, Badges, Antinuke, Whitelist, Unwhitelist,
    Extraowner, Slots, Blackjack, Stats, Status, NoPrefix, FilterCog, Global,
    TicketCog, Logging, QR, VanityRoles, ReactionRoles, Messages, TranslateCog,
    FastGreet, Jail, JoinToCreate, AI, StaffDMCog, Leveling, StickyMessage,
    Verification, Minecraft, encryption, calculator, joindm, Birthdays, Nitro,
    ImageCommands, Youtube, TTS,
    # Help stubs
    _antinuke, _extra, _general, _automod, _moderation, _music, _fun, _games,
    _ignore, _server, _voice, _welcome, _giveaway, _ticket, _logging, _vanity,
    inviteTracker, Counting, _Counting, _J2C, _ai, __boost, _leveling, _sticky,
    _verify, _encrypt, _mc, _joindm, _birth, _tts,
    # Events
    Guild, Errors, Autorole2, GuildJoinDM, greet, AutoResponder, Mention, AutoRole,
    React, AutoReaction, AutoReactListener, NotifCommands, StickyMessageListener,
    AIResponses,
    # Antinuke
    AntiMemberUpdate, AntiBan, AntiBotAdd, AntiChannelCreate, AntiChannelDelete,
    AntiChannelUpdate, AntiEveryone, AntiGuildUpdate, AntiIntegration, AntiKick,
    AntiPrune, AntiRoleCreate, AntiRoleDelete, AntiRoleUpdate, AntiWebhookUpdate,
    AntiWebhookCreate, AntiWebhookDelete,
    # Automod
    AntiSpam, AntiCaps, AntiInvite, AntiLink, AntiMassMention, AntiEmojiSpam,
    # Moderation
    Ban, Unban, Mute, Unmute, Lock, Unlock, Hide, Unhide, Kick, Warn, Role,
    Message, Moderation, TopCheck, Snipe,
]


async def setup(bot: gumballz):
    for cog in COGS:
        await bot.add_cog(cog(bot))
        print(Fore.RED + Style.BRIGHT + f"Loaded cog: {cog.__name__}")
    print(Fore.RED + Style.BRIGHT + f"All Gumballz Cogs loaded successfully ({len(COGS)}).")
