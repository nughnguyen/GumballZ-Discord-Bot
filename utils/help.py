import discord
import re
from utils.Tools import *

# Navigation button emojis (edit IDs here if you re-upload)
NAV_EMOJIS = {
    "home": "<:rewind:1453652995991404584>",
    "back": "<:icons_next:1453658490248626258>",  # flipped via back callback; keep a valid ID from your server
    "quit": "<:delete:1453602008786534514>",
    "next": "<:icons_next:1453658490248626258>",
    "last": "<:forward:1453664212768260187>",
    "home_select": "<:icon_home:1453800906519871629>",
}

NAV_FALLBACK = {
    "home": "⏪",
    "back": "◀️",
    "quit": "🗑️",
    "next": "▶️",
    "last": "⏩",
    "home_select": "🏠",
    "category": "📂",
}

_CUSTOM_RE = re.compile(r"<a?:([a-zA-Z0-9_]+):(\d+)>")


def resolve_component_emoji(bot: discord.Client, emoji_str: str, fallback: str = "📂"):
    """Use custom emoji on buttons/selects only if the bot can access it."""
    if not emoji_str:
        return fallback
    if not emoji_str.startswith("<"):
        return emoji_str

    match = _CUSTOM_RE.fullmatch(emoji_str.strip())
    if not match:
        return fallback

    name, emoji_id = match.group(1), int(match.group(2))
    cached = bot.get_emoji(emoji_id) if bot else None
    if cached is not None:
        return cached

    # Bot cannot see this emoji → unicode fallback (avoids Discord 400 on components)
    return fallback


class Dropdown(discord.ui.Select):

    def __init__(self, ctx, options, placeholder="Choose a Category for Help", row=None):
        super().__init__(placeholder=placeholder,
                         min_values=1,
                         max_values=1,
                         options=options,
                         row=row)
        self.invoker = ctx.author

    async def callback(self, interaction: discord.Interaction):
        if self.invoker == interaction.user:
            index = self.view.find_index_from_select(self.values[0])
            if not index:
                index = 0
            await self.view.set_page(index, interaction)
        else:
            await interaction.response.send_message(
                "You must run this command to interact with it.", ephemeral=True)


class View(discord.ui.View):

    def __init__(self, mapping: dict, ctx: discord.ext.commands.context.Context, homeembed: discord.embeds.Embed, ui: int):
        super().__init__(timeout=None)
        self.mapping, self.ctx, self.home = mapping, ctx, homeembed
        self.index, self.buttons = 0, None
        self.current_page = 0

        self.options, self.embeds, self.total_pages = self.gen_embeds()

        if ui == 0:
            self.add_item(Dropdown(ctx=self.ctx, options=self.options[:25]))
        elif ui == 1:
            self.buttons = self.add_buttons()
        elif ui == 2:
            self.buttons = self.add_buttons()
            mid_point = len(self.options) // 2
            options_1 = self.options[:mid_point][:25]
            options_2 = self.options[mid_point:][:25]

            if options_1:
                self.add_item(Dropdown(ctx=self.ctx, options=options_1, placeholder="📋 Main Commands", row=1))
            if options_2:
                self.add_item(Dropdown(ctx=self.ctx, options=options_2, placeholder="⚡ Extra Commands", row=2))
        else:
            self.buttons = self.add_buttons()
            self.add_item(Dropdown(ctx=self.ctx, options=self.options[:25]))

    def add_buttons(self):
        bot = self.ctx.bot

        def btn(key: str) -> discord.PartialEmoji | str:
            return resolve_component_emoji(bot, NAV_EMOJIS[key], NAV_FALLBACK[key])

        self.homeB = discord.ui.Button(label="", emoji=btn("home"), style=discord.ButtonStyle.secondary)
        self.homeB.callback = self.home_callback

        self.backB = discord.ui.Button(label="", emoji=btn("back"), style=discord.ButtonStyle.secondary)
        self.backB.callback = self.back_callback

        self.quitB = discord.ui.Button(label="", emoji=btn("quit"), style=discord.ButtonStyle.danger)
        self.quitB.callback = self.quit_callback

        self.nextB = discord.ui.Button(label="", emoji=btn("next"), style=discord.ButtonStyle.secondary)
        self.nextB.callback = self.next_callback

        self.lastB = discord.ui.Button(label="", emoji=btn("last"), style=discord.ButtonStyle.secondary)
        self.lastB.callback = self.last_callback

        buttons = [self.homeB, self.backB, self.quitB, self.nextB, self.lastB]
        for button in buttons:
            self.add_item(button)
        return buttons

    async def home_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return
        await self.set_page(0, interaction)

    async def back_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return
        current_page = self.index - 1 if self.index > 0 else len(self.embeds) - 1
        await self.set_page(current_page, interaction)

    async def quit_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return
        await self.quit(interaction)

    async def next_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return
        current_page = self.index + 1 if self.index < len(self.embeds) - 1 else 0
        await self.set_page(current_page, interaction)

    async def last_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("You must run this command to interact with it.", ephemeral=True)
            return
        await self.set_page(len(self.embeds) - 1, interaction)

    def find_index_from_select(self, value):
        i = 0
        used_labels = set()
        for cog in self.get_cogs():
            if cog is None or cog.__class__.__name__ == "Roleplay":
                continue
            if "help_custom" in dir(cog):
                _, label, _ = cog.help_custom()
                original_label = label
                counter = 1
                while label in used_labels:
                    label = f"{original_label} {counter}"
                    counter += 1
                used_labels.add(label)
                if label == value or value.startswith(original_label + " "):
                    return i + 1
                i += 1
        return 0

    def get_cogs(self):
        return list(self.mapping.keys())

    def gen_embeds(self):
        options, embeds = [], []
        total_pages = 0
        used_labels = set()
        bot = self.ctx.bot

        home_emoji = resolve_component_emoji(
            bot, NAV_EMOJIS["home_select"], NAV_FALLBACK["home_select"]
        )
        options.append(discord.SelectOption(label="Home", emoji=home_emoji, description="Main menu"))
        embeds.append(self.home)
        total_pages += 1
        used_labels.add("Home")

        for cog in self.get_cogs():
            if cog is None or cog.__class__.__name__ == "Roleplay":
                continue
            if "help_custom" not in dir(cog):
                continue
            emoji, label, description = cog.help_custom()
            original_label = label
            counter = 1
            while label in used_labels:
                label = f"{original_label} {counter}"
                counter += 1
            used_labels.add(label)

            select_emoji = resolve_component_emoji(bot, emoji, NAV_FALLBACK["category"])
            options.append(
                discord.SelectOption(
                    label=label[:100],
                    emoji=select_emoji,
                    description=(description or "Category")[:100],
                )
            )

            # Embed titles can always show custom emoji markup
            embed = discord.Embed(title=f"{emoji} {original_label}", color=0xFF0000)
            for command in cog.get_commands():
                params = "".join(f" <{param}>" for param in command.clean_params if param not in ["self", "ctx"])
                help_text = command.help or "No description available"
                if len(help_text) > 1020:
                    help_text = help_text[:1017] + "..."
                field_name = f"{command.name}{params}"[:256]
                if len(embed.fields) >= 25:
                    break
                embed.add_field(name=field_name, value=f"{help_text}\n•", inline=False)
            embeds.append(embed)
            total_pages += 1

        avatar = self.ctx.bot.user.display_avatar.url if self.ctx.bot.user else None
        self.home.set_footer(
            text=f"• Help page 1/{total_pages} | Requested by: {self.ctx.author.display_name}",
            icon_url=avatar,
        )
        return options, embeds, total_pages

    async def quit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()

    async def to_page(self, page: int, interaction: discord.Interaction):
        if not self.index + page < 0 or not self.index + page > len(self.options):
            await self.set_index(page)
            embed = self.embeds[self.index]
            avatar = self.ctx.bot.user.display_avatar.url if self.ctx.bot.user else None
            embed.set_footer(
                text=f"• Help page {self.index + 1}/{self.total_pages} | Requested by: {self.ctx.author.display_name}",
                icon_url=avatar,
            )
            await interaction.response.edit_message(embed=embed, view=self)

    async def set_page(self, page: int, interaction: discord.Interaction):
        self.index = page
        self.current_page = page
        await self.to_page(0, interaction)

    async def set_index(self, page):
        self.index += page
        if self.buttons:
            self.homeB.disabled = (self.index == 0)
            self.backB.disabled = (self.index == 0)
            self.nextB.disabled = (self.index == len(self.options) - 1)
            self.lastB.disabled = (self.index == len(self.options) - 1)

    async def set_last_page(self, interaction: discord.Interaction):
        await self.set_page(len(self.options) - 1, interaction)
