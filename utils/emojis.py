"""
Emoji constants for Discord bot reactions and messages
Sử dụng Unicode emojis để tương thích với mọi server
"""

# Game States
START = "⚔️"
END = "🏁"
SCROLL = "📜"
BAR = "┃"

# Responses
CORRECT = "✅"
FIRE = "🔥"
HUNDRED = "💯"
WRONG = "❌"
SKULL = "💀"
MIND_BLOWN = "🤯"

# Timing
TIMEOUT = "⏰"
SNAIL = "🐌"
HOURGLASS = "⏳"

# Leaderboard
CROWN = "👑"
TROPHY = "🏆"
MEDAL_1ST = "🥇"
MEDAL_2ND = "🥈"
MEDAL_3RD = "🥉"

# Powerups
HINT = "💡"
PASS = "⏭️"
JOKER = "🃏"

# Bot Challenge
ROBOT = "🤖"
SWORD = "⚔️"
VS = "🆚"

# Misc
STAR = "⭐"
SPARKLES = "✨"
THINKING = "🤔"
CELEBRATION = "🎉"
SAD = "😢"
LIGHTNING = "⚡"
STREAK = "<a:fire:1449633627628376189>"
TADA_LEFT = "<a:tada_left:1450009773138247734>"
TADA_RIGHT = "<a:tada_right:1450009775642247218>"

# Custom Emoji
ANIMATED_EMOJI_CORRECT = "<a:tickmark:1449215039608459305>"
ANIMATED_EMOJI_WRONG = "<a:wrongmark:1449214999816830986>"
ANIMATED_EMOJI_DOT = "<a:bluedot:1375508734893363271>"
ANIMATED_EMOJI_COIZ = "<a:cattoken:1449205470861459546>"
ANIMATED_EMOJI_DISCORD = "<a:discord:1375511198036000899>"
EMOJI_DISCORD = "<discord:1449212058708213850>"
EMOJI_YOUTUBE = "<youtube:1449212122314838149>"
EMOJI_TIKTOK = "<tiktok:1449212222747447357>"
EMOJI_INSTAGRAM = "<instagram:1449212173673959454>"
EMOJI_FACEBOOK = "<facebook:1449211949861830908>"
EMOJI_INVITE = "<Invite:1449328307526176881>"
EMOJI_LINK = "<:link1:1449328347661471890>"
EMOJI_MOMO_PAY = "<:momo:1449636713247936512>"
EMOJI_GIVEAWAY = "<a:giveaway:1449637499470348339>"

# Bầu Cua (6 mặt của xúc xắc)
SIDE_1 = "<:nai:1449572167984611370>"
SIDE_2 = "<:bau:1449573245576548434>"
SIDE_3 = "<:meo:1449573262232260732>"
SIDE_4 = "<:ca:1449573251041722378>"
SIDE_5 = "<:cua:1449573256498512045>"
SIDE_6 = "<:tom:1449573240715612263>"

# Loading
LOADING = "<a:loading:1449348490269294773>"

def get_rank_emoji(rank: int) -> str:
    """Trả về emoji dựa trên thứ hạng"""
    if rank == 1:
        return MEDAL_1ST
    elif rank == 2:
        return MEDAL_2ND
    elif rank == 3:
        return MEDAL_3RD
    elif rank <= 10:
        return TROPHY
    else:
        return STAR

def get_random_correct_emoji() -> str:
    """Trả về emoji ngẫu nhiên cho câu trả lời đúng"""
    import random
    return random.choice([CORRECT, FIRE, HUNDRED, SPARKLES, LIGHTNING, ANIMATED_EMOJI_CORRECT, FIRE, HUNDRED])

def get_random_wrong_emoji() -> str:
    """Trả về emoji ngẫu nhiên cho câu trả lời sai"""
    import random
    return random.choice([WRONG, SKULL, MIND_BLOWN, SAD, ANIMATED_EMOJI_WRONG])

# --- FISHING GAME EMOJIS ---

# Biomes
BIOME_RIVER = "<:biome_river_circle:1450183939770683544>"
BIOME_OCEAN = "<:biome_ocean_circle:1450183937124073482>"
BIOME_SKY = "<:biome_sky_circle:1450183941985407120>"
BIOME_VOLCANIC = "<:biome_volcanic_circle:1450183948280926228>"
BIOME_SPACE = "<:biome_space_circle:1450183945969729586>"
BIOME_ALIEN = "<:biome_alien_circle:1450183934972395762>"

# Baits
BAIT_WORM = "<:bait_worm:1450183932304822465>"
BAIT_CRICKET = "<:bait_leech:1450183924352553152>" # Reusing leech image or placeholder if cricket not there, user can swap
BAIT_LEECH = "<:bait_leech:1450183924352553152>"
BAIT_MINNOW = "<:bait_fish:1450183921483649137>" # Using bait_fish
BAIT_MAGNET = "<:magnet:1450186383757938890>"
BAIT_MAGIC = "<:magic_bait_bandana:1450186378833956874>"
BAIT_WISE = "<:wise_bait2:1450186415383249119>"
BAIT_SUPPORT = "<:bait_support:1450183926948827206>"

# Fish - River
FISH_GOLDFISH = "<:fb_goldfish:1450186125699449063>"
FISH_COD = "<:fb_codraw:1450183874658177036>"
FISH_SALMON = "<:fb_salmonraw:1450186162751672462>"
FISH_RAW = "<:fb_fishraw:1450186115222081657>"
FISH_CRAB = "<:fb_crab:1450183877078290535>"
FISH_SHRIMP = "<:shrimpp:1450871719429410837>"

# Fish - Ocean
FISH_TROPICAL = "<:fb_tropicalfish:1450186180283859026>"
FISH_CLOWN = "<:fb_pufferfish:1450186157785747498>" # Placeholder/closest
FISH_TUNA = "<:tuna:1450186413147689050>"
FISH_SHARK = "<:fb_shark:1450186165222113331>"
FISH_DOLPHIN = "<:fb_dolphin:1450183881901871236>"
FISH_TURTLE = "<:fb_turtle:1450186182422958275>"
FISH_SQUID = "<:fb_squid:1450186170481901618>"

# Fish - Sky
FISH_RAINBOW = "<:fb_rainbowfish:1450186160256057486>"
FISH_AZURE = "<:fb_azure_fish:1450183870019272767>"
FISH_DIAMOND = "<:fb_diamondfish:1450183879804715059>"

# Fish - Volcanic
FISH_HOTCOD = "<:fb_hotcod:1450186133672689738>"
FISH_LAVAFISH = "<:fb_lavafish:1450186142531194921>"
FISH_FIREPUFFER = "<:fb_firepuffer:1450183890441343006>"

# Fish - Space
FISH_SPACE = "<:space_fish:1450186406809829487>"
FISH_SPACE_CRAB = "<:space_crab:1450186404695904336>"
FISH_EMERALD = "<:fb_emeraldfish:1450183884112138371>"

# Fish - Alien
FISH_ALIEN = "<:alien_fish:1450183900432433375>"
FISH_GUARDIAN = "<:fb_guardian:1450186128874405978>"
FISH_AXOLOTL = "<:axolotl:1450184690966462627>"
FISH_EMERALD_SQUID = "<:fb_emeraldsquid:1450183886112817223>"
FISH_ZEBRA = "<:zebrafish:1450186417652367390>"

# Treasures
CHEST_UNCOMMON = "<:chest_uncommon:1450184027376980060>"
CHEST_RARE = "<:chest_rare:1450184022411051098>"
CHEST_EPIC = "<:chest_epic:1450184016077783050>"
CHEST_LEGENDARY = "<:chest_legendary:1450184018908938413>"
CHEST_SUPER = "<:chest_super:1450184024705466601>"
CHEST_ARTIFACT = "<:chest_artifact:1450184013057622159>"

# Rods
ROD_PLASTIC = "<:fb_plasticrod:1450186154522443837>"
ROD_STEEL = "<:fb_steel_rod:1450186173371781323>"
ROD_ALLOY = "<:fb_alloy_rod:1450184511165038683>"
ROD_GOLDEN = "<:fb_goldenrod:1450186123421945876>"
ROD_FIBERGLASS = "<:fb_fiberglass_rod:1450183888403038393>"
ROD_HEAVY = "<:fb_heavyrod:1450186131105906718>"
ROD_OCEANIUM = "<:fb_oceaniumrod:1450186150517018837>"
ROD_SUPERIUM = "<:fb_superium_rod:1450186175770923099>"
ROD_SUPPORTER = "<:fb_supporterrod:1450186178191032415>"
ROD_HEAVIER = "<:heavier_rod:1450186372836229150>"
ROD_METEOR = "<:meteor_rod:1450186386240966851>"
ROD_SALTSPREADER = "<:saltspreader_rod:1450186397620113561>"
ROD_FLOATING = "<:fb_floatingrod:1450186117612568608>"
ROD_MAGMA = "<:fb_magma_rod:1450186146402275388>"
ROD_DIAMOND = "<:diagonic_ultrafat_rod:1450184499370528831>" # Placeholder
ROD_LAVA = "<:fb_lava_rod:1450186139574079559>"
ROD_SKY = "<:fb_skyrod:1450186167868854292>"
ROD_SPACE = "<:space_rod:1450186408777089156>"
ROD_ALIEN = "<:alien_rod:1450183903590481931>"
ROD_INFINITY = "<:fb_infinity_rod:1450186137644830771>"
ROD_DONATOR = "<:donator_rod:1450184502927163435>"

# Charms
CHARM_BLUE = "<:charm_blue:1450183956417876060>"
CHARM_CYAN = "<:charm_cyan:1450183959714467932>"
CHARM_GREEN = "<:charm_green:1450183962671583395>"
CHARM_LBLUE = "<:charm_lblue:1450183965158932480>"
CHARM_PINK = "<:charm_pink:1450187997315338320>"
CHARM_RED = "<:charm_red:1450183972859678760>"
CHARM_WHITE = "<:charm_white:1450184008062341141>"
CHARM_YELLOW = "<:charm_yellow:1450184010788638801>"

# Badges
BADGE_50_SHADES = "<:50_shades_of_gray_badge:1450183895143284848>"
BADGE_ADMIN = "<:administrator_badge:1450183897882169344>"
BADGE_AMETHYST = "<:amethyst_badge:1450183907143057448>"
BADGE_BLACK = "<:black_badge:1450183950738653338>"
BADGE_PINK = "<:badge_pink:1450183914319515709>"
BADGE_BRONZE = "<:bronze_medal:1450184881047998628>"
BADGE_EMERALD = "<:emerald_badge:1450184507624783933>"
BADGE_GOLD = "<:gold_medal:1450186184826421298>"
BADGE_PLATINUM = "<:platinum_medal:1450186389328101436>"
BADGE_RANDOM = "<:random_badge:1450186392478154883>"
BADGE_RUBY = "<:ruby_badge:1450186394788958279>"
BADGE_SAPPHIRE = "<:sapphire_badge:1450186399524323508>"
BADGE_SILVER = "<:silver_medal:1450186402196226168>"
BADGE_SUPPORTER = "<:supporter_badge:1450186410832298095>"

# Misc
ITEM_HOOK = "<:hook:1450186375050821745>"
ITEM_ROD = "<:fb_fishingrod:1450183892794609674>"
ITEM_CHEST = "<:fb_chest:1450183873102086216>"


# King Fish
KING_RIVER1 = "<a:koifish:1450867278777291003>" # Cá Koi
KING_RIVER2 = "<a:pixelfish:1450867286343942164>" # Cá Vàng
KING_RIVER3 = "<:megagyarados:1450868551391907840>" #Mega Gyarados
KING_RIVER4 = "<:fishmoon:1450868541241954304>" # Cá Mặt Trăng
KING_RIVER5 = "<:skeletonfish:1450868559969390813>" # Cá Xương

KING_OCEAN1 = "<a:babydory:1450867281306320916>" #Baby Dory
KING_OCEAN2 = "<a:lovingshark:1450867275732357363>" #Love Shark
KING_OCEAN3 = "<a:pearl:1450872451058761861>" #Ngọc Trai
KING_OCEAN4 = "<a:jellyfish:1450867283516981330>" #Jellyfish
KING_OCEAN5 = "<:Aquaman:1450872448898568234>" #Aquaman

KING_SKY1 = "<:f16:1450913449440972953>" # Tiêm Kích F16
KING_SKY2 = "<a:phoenix:1450913387901882581>" # Phoenix
KING_SKY3 = "<:neondragon:1450913393241231500>" # Neon Dragon
KING_SKY4 = "<a:cloud:1450914579822678086>" # Mây
KING_SKY5 = "<a:rainbow:1450914577947689126>" # Cầu Vồng

KING_VOLCANIC1 = "<a:altalavadrone:1450917230219890729>" # Altalavadrone
KING_VOLCANIC2 = "<a:fireheart:1450917235962019990>" # Fireheart
KING_VOLCANIC3 = "<:netherstar:1450917238302572614>" # Netherstar
KING_VOLCANIC4 = "<:netherite:1450917240584011888>" # Netherite
KING_VOLCANIC5 = "<a:lavamerka:1450917244224934101>" # Lavamerka

KING_SPACE1 = "<:meteor:1450919174460412047>" # Meteor
KING_SPACE2 = "<:milkyway:1450919168365826048>" # Milky Way
KING_SPACE3 = "<:wishbottle:1450919178918952970>" # Lọ Điều Ước
KING_SPACE4 = "<a:astronautinspace:1450919182433652817>" # Astronaut

KING_ALIEN1 = "<a:alientwerk:1450919172052615272>" # Alien Werk
KING_ALIEN2 = "<a:gokuultra:1450921671522390156>" # Goku Ultra
KING_ALIEN3 = "<a:pinkamongus:1450920937057685836>" # Pink Among Us
KING_ALIEN4 = "<a:blueishufo:1450920931504558201>" # Blueish UFO

# 7 DragonBall
DRAGONBALL_1 = "<:1star:1450903892631093258>" # 1 Star
DRAGONBALL_2 = "<:2star:1450903895814570127>" # 2 Star
DRAGONBALL_3 = "<:3star:1450903900252143757>" # 3 Star
DRAGONBALL_4 = "<:4star:1450903904773738718>" # 4 Star
DRAGONBALL_5 = "<:5star:1450903866617893107>" # 5 Star
DRAGONBALL_6 = "<:6star:1450903872049778748>" # 6 Star
DRAGONBALL_7 = "<:7star:1450903877577871390>" # 7 Star
DRAGONBALL_FULL = "<:full7star:1450903889795874967>" # 7 Star Full
