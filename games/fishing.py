import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
import json
from typing import Optional, Dict
from utils import emojis


# --- CONSTANTS & CONFIGURATION ---

RARITIES = {
    "Common":    {"color": 0x95A5A6, "chance": 80, "mul": 1.0, "emoji": "⚪"},
    "Uncommon":  {"color": 0x2ECC71, "chance": 30, "mul": 2.5, "emoji": "🟢"},
    "Rare":      {"color": 0x3498DB, "chance": 10, "mul": 5.0, "emoji": "🔵"},
    "Epic":      {"color": 0x9B59B6, "chance": 5,  "mul": 15.0, "emoji": "🟣"},
    "Legendary": {"color": 0xF1C40F, "chance": 1, "mul": 50.0, "emoji": "🟡"},
    "Mythical":  {"color": 0xE74C3C, "chance": 0.01, "mul": 500.0, "emoji": "🔴"}
}

BIOMES = {
    "River": {
        "name": "Dòng Sông",
        "desc": "Nơi bắt đầu của mọi cần thủ.",
        "req_level": 1,
        "req_money": 0,
        "emoji": emojis.BIOME_RIVER,
        "fish": [
            {"name": "Cá Chép", "base_value": 10, "min_size": 10, "max_size": 30, "emoji": emojis.FISH_RAW, "spawn_rate": 35},
            {"name": "Cá Diếp", "base_value": 20, "min_size": 5, "max_size": 20, "emoji": emojis.FISH_GOLDFISH, "spawn_rate": 30},
            {"name": "Cá Hồi", "base_value": 30, "min_size": 30, "max_size": 60, "emoji": emojis.FISH_SALMON, "spawn_rate": 20},
            {"name": "Cá Tuyết", "base_value": 40, "min_size": 40, "max_size": 80, "emoji": emojis.FISH_COD, "spawn_rate": 10},
            {"name": "Cua", "base_value": 30, "min_size": 5, "max_size": 30, "emoji": emojis.FISH_CRAB, "spawn_rate": 15},
            {"name": "Tôm", "base_value": 30, "min_size": 5, "max_size": 30, "emoji": emojis.FISH_SHRIMP, "spawn_rate": 15},
            {"name": "Cá Koi", "base_value": 10000000, "min_size": 30, "max_size": 100, "emoji": emojis.KING_RIVER1, "spawn_rate": 0.02},
            {"name": "Cá Vàng", "base_value": 2500000, "min_size": 5, "max_size": 30, "emoji": emojis.KING_RIVER2, "spawn_rate": 0.2},
            {"name": "Mega Gyarados", "base_value": 50000000, "min_size": 300, "max_size": 1000, "emoji": emojis.KING_RIVER3, "spawn_rate": 0.01},
            {"name": "Cá Mặt Trăng", "base_value": 100000, "min_size": 20, "max_size": 60, "emoji": emojis.KING_RIVER4, "spawn_rate": 0.05},
            {"name": "Cá Xương", "base_value": 500000, "min_size": 5, "max_size": 30, "emoji": emojis.KING_RIVER5, "spawn_rate": 0.2},
        ]
    },
    "Ocean": {
        "name": "Đại Dương",
        "desc": "Biển cả mênh mông với những loài cá lớn.",
        "req_level": 5,
        "req_money": 50000,
        "emoji": emojis.BIOME_OCEAN,
        "fish": [
            {"name": "Cá Nhiệt Đới", "base_value": 50, "min_size": 10, "max_size": 30, "emoji": emojis.FISH_TROPICAL, "spawn_rate": 35},
            {"name": "Cá Ngừ", "base_value": 100, "min_size": 50, "max_size": 150, "emoji": emojis.FISH_TUNA, "spawn_rate": 25},
            {"name": "Cá Mập", "base_value": 300, "min_size": 200, "max_size": 500, "emoji": emojis.FISH_SHARK, "spawn_rate": 5},
            {"name": "Cá Heo", "base_value": 500, "min_size": 150, "max_size": 300, "emoji": emojis.FISH_DOLPHIN, "spawn_rate": 10},
            {"name": "Rùa Biển", "base_value": 200, "min_size": 50, "max_size": 100, "emoji": emojis.FISH_TURTLE, "spawn_rate": 15},
            {"name": "Mực Ống", "base_value": 80, "min_size": 20, "max_size": 60, "emoji": emojis.FISH_SQUID, "spawn_rate": 10},
            {"name": "Baby Dory", "base_value": 500000, "min_size": 5, "max_size": 30, "emoji": emojis.KING_OCEAN1, "spawn_rate": 0.05},
            {"name": "Love Shark", "base_value": 25000000, "min_size": 200, "max_size": 800, "emoji": emojis.KING_OCEAN2, "spawn_rate": 0.02},
            {"name": "Ngọc Trai", "base_value": 10000000, "min_size": 10, "max_size": 50, "emoji": emojis.KING_OCEAN3, "spawn_rate": 0.05},
            {"name": "Jellyfish", "base_value": 100000, "min_size": 50, "max_size": 100, "emoji": emojis.KING_OCEAN4, "spawn_rate": 0.05},
            {"name": "Aquaman", "base_value": 50000000, "min_size": 150, "max_size": 200, "emoji": emojis.KING_OCEAN5, "spawn_rate": 0.01},
        ]
    },
    "Sky": {
        "name": "Vùng Trời",
        "desc": "Câu cá trên những đám mây.",
        "req_level": 10,
        "req_money": 100000,
        "emoji": emojis.BIOME_SKY,
        "fish": [
            {"name": "Cá Cầu Vồng", "base_value": 800, "min_size": 30, "max_size": 100, "emoji": emojis.FISH_RAINBOW, "spawn_rate": 50},
            {"name": "Cá Azure", "base_value": 1000, "min_size": 40, "max_size": 120, "emoji": emojis.FISH_AZURE, "spawn_rate": 35},
            {"name": "Cá Kim Cương", "base_value": 2000, "min_size": 20, "max_size": 50, "emoji": emojis.FISH_DIAMOND, "spawn_rate": 15},
            {"name": "Tiêm Kích F16", "base_value": 20000000, "min_size": 1000, "max_size": 2000, "emoji": emojis.KING_SKY1, "spawn_rate": 0.01},
            {"name": "Phoenix", "base_value": 50000000, "min_size": 300, "max_size": 1000, "emoji": emojis.KING_SKY2, "spawn_rate": 0.005},
            {"name": "Neon Dragon", "base_value": 100000000, "min_size": 500, "max_size": 2000, "emoji": emojis.KING_SKY3, "spawn_rate": 0.005},
            {"name": "Mây", "base_value": 10000000, "min_size": 100, "max_size": 500, "emoji": emojis.KING_SKY4, "spawn_rate": 0.5},
            {"name": "Cầu Vồng", "base_value": 10000000, "min_size": 100, "max_size": 500, "emoji": emojis.KING_SKY5, "spawn_rate": 0.5},
        ]
    },
    "Volcano": {
        "name": "Núi Lửa",
        "desc": "Nóng bỏng tay, cá nướng tại chỗ.",
        "req_level": 20,
        "req_money": 500000,
        "emoji": emojis.BIOME_VOLCANIC,
        "fish": [
            {"name": "Cá Nóng", "base_value": 1500, "min_size": 30, "max_size": 80, "emoji": emojis.FISH_HOTCOD, "spawn_rate": 50},
            {"name": "Cá Dung Nham", "base_value": 3000, "min_size": 50, "max_size": 150, "emoji": emojis.FISH_LAVAFISH, "spawn_rate": 35},
            {"name": "Cá Nóc Lửa", "base_value": 4000, "min_size": 40, "max_size": 90, "emoji": emojis.FISH_FIREPUFFER, "spawn_rate": 15},
            {"name": "Altalavadrone", "base_value": 3000000, "min_size": 100, "max_size": 300, "emoji": emojis.KING_VOLCANIC1, "spawn_rate": 0.5},
            {"name": "Fireheart", "base_value": 5000000, "min_size": 50, "max_size": 150, "emoji": emojis.KING_VOLCANIC2, "spawn_rate": 0.4},
            {"name": "Netherstar", "base_value": 80000000, "min_size": 20, "max_size": 50, "emoji": emojis.KING_VOLCANIC3, "spawn_rate": 0.005},
            {"name": "Netherite", "base_value": 50000000, "min_size": 30, "max_size": 80, "emoji": emojis.KING_VOLCANIC4, "spawn_rate": 0.05},
            {"name": "Lavamerka", "base_value": 1000000, "min_size": 150, "max_size": 300, "emoji": emojis.KING_VOLCANIC5, "spawn_rate": 0.5},
        ]
    },
    "Space": {
        "name": "Vũ Trụ",
        "desc": "Không trọng lực, cá siêu hiếm.",
        "req_level": 40,
        "req_money": 10000000,
        "emoji": emojis.BIOME_SPACE,
        "fish": [
            {"name": "Cá Vũ Trụ", "base_value": 8000, "min_size": 100, "max_size": 300, "emoji": emojis.FISH_SPACE, "spawn_rate": 50},
            {"name": "Cua Không Gian", "base_value": 10000, "min_size": 50, "max_size": 120, "emoji": emojis.FISH_SPACE_CRAB, "spawn_rate": 35},
            {"name": "Cá Lục Bảo", "base_value": 15000, "min_size": 80, "max_size": 200, "emoji": emojis.FISH_EMERALD, "spawn_rate": 15},
            {"name": "Meteor", "base_value": 100000000, "min_size": 5000, "max_size": 50000, "emoji": emojis.KING_SPACE1, "spawn_rate": 0.02},
            {"name": "Milky Way", "base_value": 500000000, "min_size": 100000, "max_size": 500000, "emoji": emojis.KING_SPACE2, "spawn_rate": 0.001},
            {"name": "Lọ Điều Ước", "base_value": 50000000, "min_size": 10, "max_size": 40, "emoji": emojis.KING_SPACE3, "spawn_rate": 0.5},
            {"name": "Astronaut", "base_value": 80000000, "min_size": 150, "max_size": 250, "emoji": emojis.KING_SPACE4, "spawn_rate": 0.5},
        ]
    },
    "Alien": {
        "name": "Hành Tinh Lạ",
        "desc": "Những sinh vật bí ẩn từ thế giới khác.",
        "req_level": 60,
        "req_money": 50000000,
        "emoji": emojis.BIOME_ALIEN,
        "fish": [
            {"name": "Cá Ngoài Hành Tinh", "base_value": 25000, "min_size": 100, "max_size": 400, "emoji": emojis.FISH_ALIEN, "spawn_rate": 30},
            {"name": "Vệ Binh Biển", "base_value": 40000, "min_size": 200, "max_size": 600, "emoji": emojis.FISH_GUARDIAN, "spawn_rate": 25},
            {"name": "Axolotl Thần", "base_value": 50000, "min_size": 50, "max_size": 150, "emoji": emojis.FISH_AXOLOTL, "spawn_rate": 20},
            {"name": "Mực Lục Bảo", "base_value": 60000, "min_size": 300, "max_size": 800, "emoji": emojis.FISH_EMERALD_SQUID, "spawn_rate": 15},
            {"name": "Cá Ngựa Vằn", "base_value": 80000, "min_size": 100, "max_size": 200, "emoji": emojis.FISH_ZEBRA, "spawn_rate": 10},
            {"name": "Alien Werk", "base_value": 200000000, "min_size": 100, "max_size": 300, "emoji": emojis.KING_ALIEN1, "spawn_rate": 0.05},
            {"name": "Goku Ultra", "base_value": 1000000000, "min_size": 150, "max_size": 200, "emoji": emojis.KING_ALIEN2, "spawn_rate": 0.0001},
            {"name": "Pink Among Us", "base_value": 10000000, "min_size": 50, "max_size": 150, "emoji": emojis.KING_ALIEN3, "spawn_rate": 0.1},
            {"name": "Blueish UFO", "base_value": 150000000, "min_size": 500, "max_size": 2000, "emoji": emojis.KING_ALIEN4, "spawn_rate": 0.1},
        ]
    }
}

RODS = {
    "Plastic Rod":    {"name": "Cần Nhựa",       "price": 0,          "power": 0,    "luck": 0,   "emoji": emojis.ROD_PLASTIC, "durability": None},
    "Steel Rod":      {"name": "Cần Thép",       "price": 10000,       "power": 10,   "luck": 5,   "emoji": emojis.ROD_STEEL, "durability": 50},
    "Alloy Rod":      {"name": "Cần Hợp Kim",    "price": 20000,      "power": 18,   "luck": 10,  "emoji": emojis.ROD_ALLOY, "durability": 80},
    "Fiberglass Rod": {"name": "Cần Sợi Thủy Tinh", "price": 40000,   "power": 22,   "luck": 12,  "emoji": emojis.ROD_FIBERGLASS, "durability": 100},
    "Golden Rod":     {"name": "Cần Vàng",       "price": 80000,      "power": 30,   "luck": 20,  "emoji": emojis.ROD_GOLDEN, "durability": 150},
    "Floating Rod":   {"name": "Cần Nổi",        "price": 100000,      "power": 40,   "luck": 25,  "emoji": emojis.ROD_FLOATING, "durability": 180},
    "Heavy Rod":      {"name": "Cần Hạng Nặng",  "price": 130000,      "power": 55,   "luck": 15,  "emoji": emojis.ROD_HEAVY, "durability": 200},
    "Heavier Rod":    {"name": "Cần Siêu Nặng",  "price": 150000,      "power": 70,   "luck": 20,  "emoji": emojis.ROD_HEAVIER, "durability": 220},
    "Lava Rod":       {"name": "Cần Dung Nham",  "price": 180000,     "power": 85,   "luck": 30,  "emoji": emojis.ROD_LAVA, "durability": 250},
    "Magma Rod":      {"name": "Cần Magma",      "price": 200000,     "power": 100,  "luck": 35,  "emoji": emojis.ROD_MAGMA, "durability": 300},
    "Oceanium Rod":   {"name": "Cần Đại Dương",  "price": 250000,     "power": 120,  "luck": 50,  "emoji": emojis.ROD_OCEANIUM, "durability": 400},
    "Sky Rod":        {"name": "Cần Bầu Trời",   "price": 500000,     "power": 150,  "luck": 60,  "emoji": emojis.ROD_SKY, "durability": 500},
    "Meteor Rod":     {"name": "Cần Thiên Thạch","price": 800000,     "power": 180,  "luck": 70,  "emoji": emojis.ROD_METEOR, "durability": 600},
    "Space Rod":      {"name": "Cần Vũ Trụ",     "price": 1000000,    "power": 300,  "luck": 250, "emoji": emojis.ROD_SPACE, "durability": 800},
    "Superium Rod":   {"name": "Cần Siêu Cấp",   "price": 2000000,    "power": 500,  "luck": 500, "emoji": emojis.ROD_SUPERIUM, "durability": 1000},
    "Diamond Rod":    {"name": "Cần Kim Cương",  "price": 3000000,    "power": 4500,  "luck": 1000, "emoji": emojis.ROD_DIAMOND, "durability": 1200},
    "Alien Rod":      {"name": "Cần Alien",      "price": 5000000,   "power": 6000,  "luck": 2500, "emoji": emojis.ROD_ALIEN, "durability": 1500},
    "Saltspreader":   {"name": "Cần Rắc Muối",   "price": 75000000,   "power": 7500,  "luck": 3000, "emoji": emojis.ROD_SALTSPREADER, "durability": 2000},
    "Infinity Rod":   {"name": "Cần Vô Cực",     "price": 100000000,   "power": 10000, "luck": 5000, "emoji": emojis.ROD_INFINITY, "durability": 5000},
    "Donator Rod":    {"name": "Cần Nhà Tài Trợ","price": 0,          "power": 50, "luck": 20, "emoji": emojis.ROD_DONATOR, "description": "Cần câu dành riêng cho Nhà Tài Trợ (Không thể mua)", "durability": None},
}
# Map old keys to new if necessary, but here we assume clean slate or migration
ROD_LIST = list(RODS.keys())

BADGES = {
    "Bronze":    {"name": "Huy hiệu Đồng", "desc": "Câu được tổng cộng 100 con cá", "emoji": emojis.BADGE_BRONZE, "req_type": "total_fish", "req_val": 100},
    "Silver":    {"name": "Huy hiệu Bạc",  "desc": "Câu được tổng cộng 500 con cá", "emoji": emojis.BADGE_SILVER, "req_type": "total_fish", "req_val": 500},
    "Gold":      {"name": "Huy hiệu Vàng", "desc": "Câu được tổng cộng 1000 con cá", "emoji": emojis.BADGE_GOLD, "req_type": "total_fish", "req_val": 1000},
    "Platinum":  {"name": "Huy hiệu Bạch Kim", "desc": "Câu được tổng cộng 5000 con cá", "emoji": emojis.BADGE_PLATINUM, "req_type": "total_fish", "req_val": 5000},
    "Amethyst":  {"name": "Huy hiệu Thạch Anh", "desc": "Kiếm được 1 triệu Coiz từ câu cá", "emoji": emojis.BADGE_AMETHYST, "req_type": "total_earn", "req_val": 1000000},
    "Emerald":   {"name": "Huy hiệu Lục Bảo", "desc": "Kiếm được 10 triệu Coiz từ câu cá", "emoji": emojis.BADGE_EMERALD, "req_type": "total_earn", "req_val": 10000000},
    "Ruby":      {"name": "Huy hiệu Hồng Ngọc", "desc": "Kiếm được 100 triệu Coiz từ câu cá", "emoji": emojis.BADGE_RUBY, "req_type": "total_earn", "req_val": 100000000},
    "Sapphire":  {"name": "Huy hiệu Sapphire", "desc": "Sở hữu 10 loại Cần câu khác nhau", "emoji": emojis.BADGE_SAPPHIRE, "req_type": "rod_count", "req_val": 10},
    "50Shades":  {"name": "50 Sắc Thái", "desc": "Sở hữu 20 loại Cần câu khác nhau", "emoji": emojis.BADGE_50_SHADES, "req_type": "rod_count", "req_val": 20},
    "Admin":     {"name": "Admin", "desc": "Dành cho Admin", "emoji": emojis.BADGE_ADMIN, "req_type": "admin", "req_val": 0},
    "Supporter": {"name": "Người Ủng Hộ", "desc": "Dành cho Donator", "emoji": emojis.BADGE_SUPPORTER, "req_type": "manual", "req_val": 0},
    "DragonHunter": {"name": "Thợ Săn Rồng", "desc": "Sưu tập đủ 7 Viên Ngọc Rồng", "emoji": emojis.DRAGONBALL_FULL, "req_type": "dragon_balls", "req_val": 7},
    "KingFisher": {"name": "Vua Câu Cá", "desc": "Câu được tất cả các loài Boss", "emoji": emojis.KING_ALIEN2, "req_type": "king_fish_all", "req_val": 0},
}

DRAGON_BALLS = {
    1: {"name": "1 Sao", "emoji": emojis.DRAGONBALL_1},
    2: {"name": "2 Sao", "emoji": emojis.DRAGONBALL_2},
    3: {"name": "3 Sao", "emoji": emojis.DRAGONBALL_3},
    4: {"name": "4 Sao", "emoji": emojis.DRAGONBALL_4},
    5: {"name": "5 Sao", "emoji": emojis.DRAGONBALL_5},
    6: {"name": "6 Sao", "emoji": emojis.DRAGONBALL_6},
    7: {"name": "7 Sao", "emoji": emojis.DRAGONBALL_7},
}

BAITS = {
    "Worms":           {"name": "Mồi Giun",    "price": 0,     "power": 0,  "luck": 0,  "desc": "Mồi câu cơ bản (Miễn phí).", "emoji": emojis.BAIT_WORM},
    "Cricket":         {"name": "Dế Mèn",      "price": 200,    "power": 5,  "luck": 2,  "desc": "Thu hút cá nhỏ.", "emoji": emojis.BAIT_CRICKET},
    "Leeches":         {"name": "Đỉa",         "price": 500,    "power": 8,  "luck": 4,  "desc": "Bám dính tốt.", "emoji": emojis.BAIT_LEECH},
    "Minnows":         {"name": "Cá Con",      "price": 1500,   "power": 12, "luck": 8,  "desc": "Dụ cá săn mồi.", "emoji": emojis.BAIT_MINNOW},
    "Support Bait":    {"name": "Mồi Hỗ Trợ",  "price": 15000,  "power": 30, "luck": 25, "desc": "Tăng khả năng câu.", "emoji": emojis.BAIT_SUPPORT},
    "Magic Bait":      {"name": "Mồi Ma Thuật","price": 50000,  "power": 50, "luck": 40, "desc": "Có ma thuật huyền bí.", "emoji": emojis.BAIT_MAGIC},
    "Wise Bait":       {"name": "Mồi Thông Thái","price": 100000,"power": 80, "luck": 60, "desc": "Dụ cá hiếm cực tốt.", "emoji": emojis.BAIT_WISE},
    "Magnet":          {"name": "Nam Châm",    "price": 200000, "power": 30, "luck": 20, "desc": "Hút 2-4 con cá một lúc!", "emoji": emojis.BAIT_MAGNET, "is_special": True},
}

TREASURES = [
    {"name": "Rương Gỗ",        "value": 2000,   "emoji": emojis.CHEST_UNCOMMON},
    {"name": "Rương Sắt",       "value": 5000,   "emoji": emojis.CHEST_RARE},
    {"name": "Rương Vàng",      "value": 20000,  "emoji": emojis.CHEST_EPIC},
    {"name": "Rương Kim Cương", "value": 100000, "emoji": emojis.CHEST_LEGENDARY},
    {"name": "Rương Kho Báu",   "value": 500000, "emoji": emojis.CHEST_SUPER},
    {"name": "Cổ Vật",          "value": 1000000,"emoji": emojis.CHEST_ARTIFACT},
]

CHARMS = {
    "Lucky Charm": {"name": "Bùa May Mắn", "price": 50000, "power": 0, "luck": 50, "duration_min": 1, "duration_max": 60, "emoji": emojis.CHARM_GREEN},
    "Power Charm": {"name": "Bùa Sức Mạnh", "price": 50000, "power": 50, "luck": 0, "duration_min": 1, "duration_max": 60, "emoji": emojis.CHARM_RED},
    "Golden Charm": {"name": "Bùa Vàng", "price": 50000, "power": 50, "luck": 50, "duration_min": 1, "duration_max": 60, "emoji": emojis.CHARM_YELLOW},
    "XP Charm": {"name": "Bùa Kinh Nghiệm I", "price": 100000, "power": 0, "luck": 0, "xp_mul": 1.5, "duration_min": 1, "duration_max": 60, "emoji": "📗"},
    "Super XP Charm": {"name": "Bùa Kinh Nghiệm II", "price": 200000, "power": 0, "luck": 0, "xp_mul": 2.0, "duration_min": 1, "duration_max": 60, "emoji": "📘"},
}

class ChangeBaitView(discord.ui.View):
    def __init__(self, cog, user_id, baits_inv, parent_view):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.baits_inv = baits_inv
        self.parent_view = parent_view
        
        # Populate buttons
        for key, count in baits_inv.items():
            if count > 0:
                info = BAITS.get(key, {"name": key, "emoji": "🪱"})
                btn = discord.ui.Button(label=f"{info['name']} (x{count})", emoji=info['emoji'], style=discord.ButtonStyle.secondary)
                
                async def callback(inter, k=key, n=info['name']):
                    await self.equip_bait(inter, k, n)
                    
                btn.callback = callback
                self.add_item(btn)

    async def equip_bait(self, interaction: discord.Interaction, key, name):
        if key == "Magnet":
            # Prompt for sub-bait
            other_baits = {k: v for k, v in self.baits_inv.items() if k != "Magnet" and v > 0}
            
            if not other_baits:
                 await self._do_equip(interaction, key, None)
                 return
                 
            view = discord.ui.View()
            options = [discord.SelectOption(label="Không dùng kèm", value="none", emoji="❌")]
            
            for k, count in other_baits.items():
                 b_info = BAITS.get(k, {"name": k, "emoji": "🪱"})
                 options.append(discord.SelectOption(label=f"{b_info['name']} (x{count})", value=k, emoji=b_info['emoji']))
            
            select = discord.ui.Select(placeholder="Chọn mồi dùng kèm Nam Châm...", options=options[:25])
            
            async def sub_callback(inter):
                 val = select.values[0]
                 sub_bait = val if val != "none" else None
                 await self._do_equip(inter, "Magnet", sub_bait)
            
            select.callback = sub_callback
            view.add_item(select)
            
            await interaction.response.send_message("🧲 Bạn có muốn dùng kèm mồi khác để tăng hiệu quả không?", view=view, ephemeral=True)
            return

        await self._do_equip(interaction, key, None)

    async def _do_equip(self, interaction, key, sub_bait):
        data = await self.cog.db.get_fishing_data(self.user_id)
        stats = data.get("stats", {})
        stats["current_bait"] = key
        stats["magnet_sub_bait"] = sub_bait
        await self.cog.db.update_fishing_data(self.user_id, stats=stats)
        
        msg = f"✅ Đã trang bị mồi **{BAITS.get(key,{}).get('name', key)}**!"
        if sub_bait:
             msg += f" (Kèm: **{BAITS.get(sub_bait,{}).get('name', sub_bait)}**)"
        
        if interaction.response.is_done():
             await interaction.edit_original_response(content=msg, view=None)
        else:
             await interaction.response.send_message(msg, ephemeral=True) 

class ChangeRodView(discord.ui.View):
    def __init__(self, cog, user_id, owned_rods, current_rod, parent_view, durability_map=None):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.owned_rods = owned_rods
        self.current_rod = current_rod
        self.parent_view = parent_view
        if durability_map is None: durability_map = {}
        
        for rod_key in owned_rods:
            info = RODS.get(rod_key, {"name": rod_key, "emoji": "🎣"})
            style = discord.ButtonStyle.primary if rod_key == current_rod else discord.ButtonStyle.secondary
            disabled = (rod_key == current_rod)
            
            dura = durability_map.get(rod_key)
            max_dura = info.get("durability")
            label_s = info['name']
            if dura is not None and max_dura:
                label_s += f" [{dura}/{max_dura}]"
            
            btn = discord.ui.Button(label=label_s, emoji=info['emoji'], style=style, disabled=disabled)
            
            async def callback(inter, k=rod_key, n=info['name']):
                await self.equip_rod(inter, k, n)
            
            btn.callback = callback
            self.add_item(btn)

    async def equip_rod(self, interaction: discord.Interaction, key, name):
        await self.cog.db.update_fishing_data(self.user_id, rod_type=key)
        await interaction.response.send_message(f"✅ Đã trang bị **{name}**!", ephemeral=True)

class ShopSelectView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog

    @discord.ui.select(
        placeholder="🏪 Chọn cửa hàng muốn ghé thăm...",
        min_values=1, 
        max_values=1,
        options=[
            discord.SelectOption(label="Cửa Hàng Mồi", emoji="🪱", description="Mua mồi câu (Giun, Dế, Nam Châm...)", value="bait"),
            discord.SelectOption(label="Cửa Hàng Cần", emoji="🎣", description="Nâng cấp cần câu mới", value="rod"),
            discord.SelectOption(label="Cửa Hàng Bùa", emoji="🧿", description="Mua bùa buff chỉ số", value="charm"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        choice = select.values[0]
        if choice == "bait":
             # Call the command callback manually
             await self.cog.bait_shop.callback(self.cog, interaction)
        elif choice == "rod":
             await self.cog.rod_shop.callback(self.cog, interaction)
        elif choice == "charm":
             # Charm shop is a regular method, not a command anymore
             await self.cog.charm_shop(interaction)


class ConfirmUnlockView(discord.ui.View):
    def __init__(self, cog, user_id, biome_key, cost):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.biome_key = biome_key
        self.cost = cost

    @discord.ui.button(label="Xác Nhận Mở Khóa", style=discord.ButtonStyle.success, emoji="🔓")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        
        # Re-check money
        bal = await self.cog.db.get_player_points(self.user_id, interaction.guild_id)
        if bal < self.cost:
             await interaction.response.send_message(f"❌ Bạn không đủ tiền! Cần {self.cost:,.2f} Coiz.", ephemeral=True)
             return

        await self.cog.db.add_points(self.user_id, interaction.guild_id, -self.cost)
        
        # Update unlock data
        data = await self.cog.db.get_fishing_data(self.user_id)
        stats = data.get("stats", {})
        unlocked = stats.get("unlocked_biomes", ["River"])
        
        if self.biome_key not in unlocked:
            unlocked.append(self.biome_key)
            stats["unlocked_biomes"] = unlocked
        
        # Move to new biome
        stats["current_biome"] = self.biome_key
        await self.cog.db.update_fishing_data(self.user_id, stats=stats)

        b_info = BIOMES[self.biome_key]
        await interaction.response.edit_message(content=f"🎉 Đã mở khóa và chuyển đến **{b_info['emoji']} {b_info['name']}**!", view=None, embed=None)

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
         if interaction.user.id != self.user_id: return
         await interaction.response.edit_message(content="❌ Đã hủy mở khóa.", view=None, embed=None)

class BiomeSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="🗺️ Xem thông tin vùng...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        self.view.selected_biome = self.values[0]
        self.view.update_components()
        embed = self.view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)

class BiomeSelectView(discord.ui.View):
    def __init__(self, cog, user_id, current_biome, stats):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        if current_biome not in BIOMES:
            current_biome = "River"
        self.current_biome = current_biome
        self.selected_biome = current_biome
        self.stats = stats
        self.unlocked = stats.get("unlocked_biomes", ["River"])
        if "River" not in self.unlocked:
            self.unlocked.insert(0, "River")
        self.update_components()

    def update_components(self):
        self.clear_items()
        
        options = []
        for k, v in BIOMES.items():
            is_unlocked = k in self.unlocked
            label = v["name"]
            emoji = v["emoji"]
            desc = "Đã mở khóa" if is_unlocked else "🔒 Locked"
            options.append(discord.SelectOption(label=label, emoji=emoji, value=k, description=desc, default=(k==self.selected_biome)))
        self.add_item(BiomeSelect(options))
        
        if self.selected_biome in self.unlocked:
             style = discord.ButtonStyle.secondary if self.selected_biome == self.current_biome else discord.ButtonStyle.success
             label = "Đang Ở Đây" if self.selected_biome == self.current_biome else "Đi Đến Đây"
             disabled = (self.selected_biome == self.current_biome)
             
             btn = discord.ui.Button(label=label, style=style, disabled=disabled, emoji="✅")
             btn.callback = self.move_callback
             self.add_item(btn)
        else:
             cost = BIOMES[self.selected_biome].get("req_money", 0)
             btn = discord.ui.Button(label=f"Mở Khóa ({cost:,} Coiz)", style=discord.ButtonStyle.primary, emoji="🔓")
             btn.callback = self.unlock_callback
             self.add_item(btn)

    def get_embed(self):
        b_data = BIOMES[self.selected_biome]
        embed = discord.Embed(title=f"{b_data['emoji']} {b_data['name']}", description=b_data['desc'], color=discord.Color.blue())
        
        req_level = b_data.get("req_level", 1)
        req_money = b_data.get("req_money", 0)
        status = "✅ Đã mở khóa" if self.selected_biome in self.unlocked else f"🔒 Yêu cầu: Level {req_level} | {req_money:,} Coiz"
        embed.add_field(name="📍 Trạng Thái", value=status, inline=False)
        
        fish_list = b_data.get("fish", [])
        fish_desc = "\n".join([f"- {f['emoji']} {f['name']}" for f in fish_list])
        embed.add_field(name="🐟 Các loài cá:", value=fish_desc or "Chưa có thông tin", inline=False)
        return embed

    async def move_callback(self, interaction: discord.Interaction):
         if interaction.user.id != self.user_id: return
         self.stats["current_biome"] = self.selected_biome
         await self.cog.db.update_fishing_data(self.user_id, stats=self.stats)
         await interaction.response.edit_message(content=f"✅ Đã chuyển đến **{BIOMES[self.selected_biome]['name']}**!", view=None, embed=None)

    async def unlock_callback(self, interaction: discord.Interaction):
         if interaction.user.id != self.user_id: return
         b_key = self.selected_biome
         b_data = BIOMES[b_key]
         cost = b_data.get("req_money", 0)
         req_level = b_data.get("req_level", 1)
         user_level = self.stats.get("level", 1)
         
         if user_level < req_level:
              await interaction.response.send_message(f"❌ Bạn cấp thấp! Cần Level {req_level}.", ephemeral=True)
              return
              
         user_point = await self.cog.db.get_player_points(self.user_id, interaction.guild_id)
         if user_point < cost:
              await interaction.response.send_message(f"❌ Bạn không đủ tiền! Cần {cost:,} Coiz.", ephemeral=True)
              return
              
         await self.cog.db.add_points(self.user_id, interaction.guild_id, -cost)
         self.unlocked.append(b_key)
         self.stats["unlocked_biomes"] = self.unlocked
         self.stats["current_biome"] = b_key
         await self.cog.db.update_fishing_data(self.user_id, stats=self.stats)
         
         await interaction.response.edit_message(content=f"🎉 Đã mở khóa và chuyển đến **{b_data['name']}**!", view=None, embed=None)

class FishingView(discord.ui.View):
    def __init__(self, cog, user_id, current_biome, last_catch=None):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        if current_biome not in BIOMES:
            current_biome = "River"
        self.current_biome = current_biome
        self.last_catch = last_catch
        self.message = None

    @discord.ui.button(label="Câu Tiếp", style=discord.ButtonStyle.success, emoji="🎣")
    async def fish_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        self.timeout = 60
        await interaction.response.defer()
        await self.cog.process_fishing(interaction, self.current_biome, view=self)

    @discord.ui.button(label="Bán Nhanh", style=discord.ButtonStyle.secondary, emoji="💰")
    async def sell_fast(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        if not self.last_catch:
            await interaction.response.send_message("❌ Không có cá để bán hoặc đã bán rồi!", ephemeral=True)
            return

        catches = self.last_catch if isinstance(self.last_catch, list) else [self.last_catch]
        total_val = 0
        names_sold = []
        
        data = await self.cog.db.get_fishing_data(self.user_id)
        inv = data.get("inventory", {})
        fish_inv = inv.get("fish", {})

        for fish in catches:
            f_name = fish['name']
            f_val = fish['value']
            if f_name in fish_inv and fish_inv[f_name]["count"] > 0:
                fish_inv[f_name]["count"] -= 1
                fish_inv[f_name]["total_value"] -= f_val
                if fish_inv[f_name]["count"] <= 0: del fish_inv[f_name]
                total_val += f_val
                names_sold.append(f_name)

        if total_val > 0:
            stats = data.get("stats", {})
            stats["lifetime_money"] = stats.get("lifetime_money", 0) + total_val
            
            await self.cog.db.update_fishing_data(self.user_id, inventory=inv, stats=stats)
            await self.cog.db.add_points(self.user_id, interaction.guild_id, total_val)
            
            await self.cog.check_badges(self.user_id, interaction.channel)
            
            button.disabled = True
            button.label = "Đã Bán"
            self.last_catch = None
            await interaction.response.edit_message(view=self)
            names_summary = ", ".join(set(names_sold))
            cnt = len(names_sold)
            await interaction.followup.send(f"✅ Đã bán **{cnt}x cá** ({names_summary}) với giá **{total_val:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}", ephemeral=True)
        else:
             await interaction.response.send_message("❌ Cá này không còn trong túi đồ (có thể đã bán?)", ephemeral=True)

    @discord.ui.button(label="Chuyển Vùng", style=discord.ButtonStyle.secondary, emoji="🗺️", row=1)
    async def change_biome(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        # Call the existing command logic function to ensure consistency (same interface as /khu-vuc)
        await self.cog.show_biomes_ui(interaction)

    @discord.ui.button(label="Đổi Mồi", style=discord.ButtonStyle.secondary, emoji="🪱", row=1)
    async def change_bait(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        data = await self.cog.db.get_fishing_data(self.user_id)
        inv = data.get("inventory", {})
        baits_inv = inv.get("baits", {})
        if not baits_inv:
            await interaction.response.send_message("❌ Túi mồi trống không! Hãy vào Shop mua thêm.", ephemeral=True)
            return
        view = ChangeBaitView(self.cog, self.user_id, baits_inv, self)
        await interaction.response.send_message("👇 **Chọn mồi câu muốn dùng:**", view=view, ephemeral=True)

    @discord.ui.button(label="Đổi Cần", style=discord.ButtonStyle.secondary, emoji="🥢", row=1)
    async def change_rod(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        data = await self.cog.db.get_fishing_data(self.user_id)
        current_rod = data.get("rod_type", "Plastic Rod")
        
        inv = data.get("inventory", {})
        owned = inv.get("rods", [])
        durability_map = inv.get("rod_durability", {})

        # Ensure default
        if not owned: owned = ["Plastic Rod"]
        
        # Sync current rod if missing (migration fix)
        if current_rod not in owned:
            owned.append(current_rod)
            inv["rods"] = owned
            await self.cog.db.update_fishing_data(self.user_id, inventory=inv)

        view = ChangeRodView(self.cog, self.user_id, owned, current_rod, self, durability_map)
        await interaction.response.send_message(f"👇 **Chọn cần câu ({len(owned)} sở hữu):**", view=view, ephemeral=True)


class UseCharmSelect(discord.ui.Select):
    def __init__(self, cog, user_id, charm_list):
        self.cog = cog
        self.user_id = user_id
        options = []
        for i, c in enumerate(charm_list[:25]):
             c_info = CHARMS.get(c['key'], {"emoji": "🧿"})
             minutes = c['duration'] // 60
             options.append(discord.SelectOption(
                label=f"{c.get('name', 'Bùa')} ({minutes}p)",
                value=str(i),
                description=f"Kích hoạt {minutes}p",
                emoji=c_info.get('emoji', '🧿')
             ))
        super().__init__(placeholder="Chọn bùa để sử dụng...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        d = await self.cog.db.get_fishing_data(self.user_id)
        i_v = d.get("inventory", {})
        c_list = i_v.get("charms", [])
        
        if idx >= len(c_list):
            await interaction.response.send_message("❌ Bùa không tồn tại hoặc lỗi dữ liệu!", ephemeral=True)
            return
        
        try:
            used_charm = c_list.pop(idx)
        except IndexError:
             await interaction.response.send_message("❌ Bùa không tồn tại!", ephemeral=True)
             return
        
        # Activate
        st = d.get("stats", {})
        ac = st.get("active_charms", {})
        
        import time
        now = int(time.time())
        current_end = ac.get(used_charm['key'], now)
        if current_end < now: current_end = now
        
        ac[used_charm['key']] = current_end + used_charm['duration']
        st["active_charms"] = ac
        
        await self.cog.db.update_fishing_data(self.user_id, inventory=i_v, stats=st)
        await interaction.response.send_message(f"✨ Đã kích hoạt **{used_charm['name']}**! Hiệu lực thêm {used_charm['duration']//60} phút.", ephemeral=True)

class InventoryView(discord.ui.View):
    def __init__(self, cog, user_id, user_data):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.user_data = user_data
        
        self.add_item(InventorySelect(cog, user_id, user_data))

    @discord.ui.button(label="Dùng Bùa", style=discord.ButtonStyle.success, emoji="🔮", row=1)
    async def use_charm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        
        # Refresh data to be safe
        d = await self.cog.db.get_fishing_data(self.user_id)
        charms = d.get("inventory", {}).get("charms", [])
        
        if not charms:
             await interaction.response.send_message("❌ Bạn không có bùa nào để dùng!", ephemeral=True)
             return

        view = discord.ui.View()
        view.add_item(UseCharmSelect(self.cog, self.user_id, charms))
        await interaction.response.send_message("👇 **Chọn bùa muốn kích hoạt:**", view=view, ephemeral=True)

class InventorySelect(discord.ui.Select):
    def __init__(self, cog, user_id, user_data):
        self.cog = cog
        self.user_id = user_id
        self.user_data = user_data
        
        options = [
            discord.SelectOption(label="Cần Câu", emoji="🎣", value="rod", description="Xem danh sách cần câu"),
            discord.SelectOption(label="Cá", emoji="🐟", value="fish", description="Xem kho cá câu được"),
            discord.SelectOption(label="Mồi Câu", emoji="🪱", value="bait", description="Xem số lượng mồi"),
            discord.SelectOption(label="Bùa Chú", emoji="🧿", value="charm", description="Xem bùa buff")
        ]
        super().__init__(placeholder="Chọn túi đồ để xem...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id: 
            return # Silent fail or ephemeral msg
        
        val = self.values[0]
        inv = self.user_data.get("inventory", {})
        embed = discord.Embed(title=f"🎒 TÚI ĐỒ", color=discord.Color.gold())
        
        if val == "rod":
            rods_inv = inv.get("rods", [])
            dura_map = inv.get("rod_durability", {})
            current_rod = self.user_data.get("rod_type", "Plastic Rod")
            
            if rods_inv:
                rod_lines = []
                for r in rods_inv:
                    r_info = RODS.get(r, {"name": r, "emoji": "🎣", "durability": None})
                    dura = dura_map.get(r)
                    max_d = r_info.get("durability")
                    dura_str = "Vĩnh viễn"
                    if max_d:
                        cur = dura if dura is not None else max_d
                        dura_str = f"{cur}/{max_d}"
                    status = "✅ (Đang dùng)" if r == current_rod else ""
                    rod_lines.append(f"{r_info['emoji']} **{r_info['name']}** {status} [Độ bền: {dura_str}]")
                embed.description = "\n".join(rod_lines)
            else:
                embed.description = "Chưa sở hữu cần nào."

        elif val == "fish":
            fish_inv = inv.get("fish", {})
            if fish_inv:
                normal_fish = []
                boss_fish = []
                total_val = 0
                total_count = 0
                
                # Check for "KingFisher" badge tracking
                all_bosses_caught = True
                total_bosses = 0
                caught_bosses = 0
                
                # Prepare a lookup for spawn rates to identify bosses
                fish_meta = {}
                boss_names = set()
                for b_val in BIOMES.values():
                    for f in b_val["fish"]:
                        fish_meta[f["name"]] = f
                        if f.get("spawn_rate", 10) < 1.0:
                            boss_names.add(f["name"])

                total_bosses = len(boss_names)

                for name, info in fish_inv.items():
                    count = info.get("count", 0)
                    if count <= 0: continue
                    
                    val_fish = info.get("total_value", 0)
                    meta = fish_meta.get(name, {"emoji": "🐟", "spawn_rate": 10})
                    emoji_icon = meta.get("emoji", "🐟")
                    is_boss = meta.get("spawn_rate", 10) < 1.0
                    
                    line = f"• {emoji_icon} **{name}**: x{count} ({val_fish:,})"
                    
                    if is_boss:
                        boss_fish.append(line)
                        if name in boss_names:
                             caught_bosses += 1 # Count distinct bosses caught
                    else:
                        normal_fish.append(line)
                        
                    total_val += val_fish
                    total_count += count

                # Verify King Fisher Badge (Caught ALL boss types)
                # Instead of counting unique caught, we check if all boss_names are in fish_inv keys
                caught_boss_names_inv = [k for k in fish_inv.keys() if k in boss_names and fish_inv[k].get("count", 0) > 0]
                if len(caught_boss_names_inv) >= total_bosses and total_bosses > 0:
                     # Trigger Badge Check (Async, so we just ensure logic exists in check_badges or trigger here)
                     # ideally we trigger self.cog.check_badges() but that's a coroutine. 
                     # Since this is a view callback, we can await it.
                     pass 
                
                # Update badge progress implicitly via check_badges later or do it now?
                # User asked to "system save progress if user caught all bosses then award badge".
                # The BADGES constant has "KingFisher": ..., "req_type": "king_fish_all"
                # We need to ensure check_badges handles "king_fish_all".

                # Display Logic with Pagination
                max_chars = 1000
                
                # Normal Fish Field
                normal_text = "\n".join(normal_fish) if normal_fish else "Trống"
                if len(normal_text) > max_chars:
                    # Simple truncation for now as buttons need more class structure
                    # Or we can split into multiple fields?
                    # Let's split into chunks
                    chunks = [normal_text[i:i+max_chars] for i in range(0, len(normal_text), max_chars)]
                    embed.add_field(name=f"🐟 Cá Thường ({len(normal_fish)})", value=chunks[0], inline=False)
                    if len(chunks) > 1:
                        embed.add_field(name="🐟 Cá Thường (Tiếp)", value=chunks[1][:1000] + "...", inline=False)
                else:
                    embed.add_field(name=f"🐟 Cá Thường ({len(normal_fish)})", value=normal_text, inline=False)

                # Boss Fish Field
                if boss_fish:
                    boss_text = "\n".join(boss_fish)
                    embed.add_field(name=f"👑 VUA CÁ ({len(boss_fish)})", value=boss_text, inline=False)
                
                embed.set_footer(text=f"Tổng: {total_count} con | Giá trị: {total_val:,} Coiz")
                
                # Check badges immediately to ensure update
                await self.cog.check_badges(self.user_id, interaction.channel)

            else:
                embed.description = "Thùng cá trống rỗng."

        elif val == "bait":
            bait_inv = inv.get("baits", {})
            bait_list = []
            if bait_inv:
                for k, v in bait_inv.items():
                    b_info = BAITS.get(k, {"name": k, "emoji": "🪱"})
                    if v > 0:
                        bait_list.append(f"{b_info['emoji']} **{b_info['name']}**: {v}")
            embed.description = "\n".join(bait_list) if bait_list else "Hết mồi câu rồi!"

        elif val == "charm":
            charm_inv = inv.get("charms", [])
            if charm_inv:
                charm_list = []
                for i, c in enumerate(charm_inv):
                    minutes = c['duration'] // 60
                    c_info = CHARMS.get(c['key'], {"emoji": "🧿"})
                    charm_list.append(f"**{i+1}.** {c_info.get('emoji', '🧿')} {c.get('name', 'Bùa')} ({minutes}p)")
                embed.description = "\n".join(charm_list)
            else:
                embed.description = "Không có bùa nào."
                
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.primary, emoji="🛒", row=1)
    async def open_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id: return
        view = ShopSelectView(self.cog)
        await interaction.response.send_message("🏪 **Bạn muốn vào cửa hàng nào?**", view=view, ephemeral=True)

class FishingGame:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # Helper for response compatibility
    async def _respond(self, interaction, *args, **kwargs):
        if isinstance(interaction, commands.Context):
            if "ephemeral" in kwargs: del kwargs["ephemeral"] # Context doesn't support ephemeral
            # If view is in kwargs, ensure it is passed
            return await interaction.send(*args, **kwargs)
        else:
            if hasattr(interaction, "response") and not interaction.response.is_done():
                return await interaction.response.send_message(*args, **kwargs)
            else:
                return await interaction.followup.send(*args, **kwargs)

    # ... (Command implementations inside class)

    async def get_stats_multiplier(self, user_id):
        """Calculate total Power and Luck from Rod + Bait + Active Charms"""
        data = await self.db.get_fishing_data(user_id)
        stats = data.get("stats", {})
        
        # Rod Stats
        rod_key = data.get("rod_type", "Plastic Rod")
        rod = RODS.get(rod_key, RODS["Plastic Rod"])
        
        # Bait Stats
        bait_key = stats.get("current_bait")
        bait = BAITS.get(bait_key, {"power": 0, "luck": 0})
        
        active_charms = stats.get("active_charms", {})
        import time
        current_time = int(time.time())
        
        charm_power = 0
        charm_luck = 0
        expired_charms = []
        
        charm_power = 0
        charm_luck = 0
        xp_mul = 1.0 # Default Multiplier
        expired_charms = []
        
        for c_key, expire_at in active_charms.items():
            if current_time < expire_at:
                c_info = CHARMS.get(c_key)
                if c_info:
                    charm_power += c_info.get("power", 0)
                    charm_luck += c_info.get("luck", 0)
                    xp_mul = max(xp_mul, c_info.get("xp_mul", 1.0))
            else:
                expired_charms.append(c_key)
        
        # Clean up expired
        if expired_charms:
            for k in expired_charms:
                del active_charms[k]
            stats["active_charms"] = active_charms
            # We don't save DB here to avoid async write race conditions in tight loops, 
            # relying on next update. Or we can just let it update next time something is saved.
        
        total_power = rod["power"] + bait.get("power", 0) + charm_power
        total_luck = rod["luck"] + bait.get("luck", 0) + charm_luck
        
        return total_power, total_luck, data, bait_key, xp_mul

    async def charm_shop(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧿 CỬA HÀNG BÙA CHÚ", description="Mua bùa để tăng chỉ số trong thời gian ngắn! (Ngẫu nhiên 3-30p)", color=discord.Color.purple())
        
        for key, info in CHARMS.items():
            embed.add_field(
                name=f"{info['emoji']} {info['name']}",
                value=f"💰 Giá: **{info['price']:,.2f}** Coiz {emojis.ANIMATED_EMOJI_COIZ}\n💪 Power: +{info['power']} | 🍀 Luck: +{info['luck']}\n⏱️ Thời gian: {info['duration_min']}-{info['duration_max']} phút",
                inline=False
            )
            
        view = discord.ui.View()
        
        for key, info in CHARMS.items():
            btn = discord.ui.Button(label=info['name'], emoji=info['emoji'], style=discord.ButtonStyle.secondary)
            
            async def callback(inter, k=key, i=info):
                # Buy logic
                cost = i["price"]
                user_point = await self.db.get_player_points(inter.user.id, inter.guild_id)
                
                if user_point < cost:
                    await inter.response.send_message("❌ Không đủ tiền!", ephemeral=True)
                    return
                
                # Randomized duration on purchase
                duration_min = i["duration_min"]
                duration_max = i["duration_max"]
                duration_sec = random.randint(duration_min * 60, duration_max * 60)
                
                await self.db.add_points(inter.user.id, inter.guild_id, -cost)
                
                data = await self.db.get_fishing_data(inter.user.id)
                inv = data.get("inventory", {})
                if "charms" not in inv: inv["charms"] = [] 
                
                # New charm item
                new_charm = {"key": k, "duration": duration_sec, "name": i["name"]}
                inv["charms"].append(new_charm)
                
                await self.db.update_fishing_data(inter.user.id, inventory=inv)
                
                minutes = duration_sec // 60
                seconds = duration_sec % 60
                await inter.response.send_message(f"✅ Đã mua **{i['emoji']} {i['name']}**!\n⏱️ Thời gian hiệu lực: **{minutes} phút {seconds} giây**.\n(Vào `/inventory` chọn dùng ngay)", ephemeral=True)


            btn.callback = callback
            view.add_item(btn)

        back_btn = discord.ui.Button(label="Trang Chủ", style=discord.ButtonStyle.secondary, emoji="🏠", row=1)
        async def back_callback(inter):
            if inter.user.id != interaction.user.id: return
            view = ShopSelectView(self)
            await inter.response.edit_message(content="🏪 **CHÀO MỪNG ĐẾN CỬA HÀNG!**\nBạn muốn xem loại hàng nào?", embed=None, view=view)
        back_btn.callback = back_callback
        view.add_item(back_btn)
            
        await interaction.response.send_message(embed=embed, view=view)
    async def check_badges(self, user_id, channel):
        data = await self.db.get_fishing_data(user_id)
        stats = data.get("stats", {})
        owned_badges = stats.get("badges", [])
        
        # Metrics
        total_fish = 0
        inv = data.get("inventory", {})
        fish_inv = inv.get("fish", {})
        # Recalculate total caught from current inventory + unsold? 
        # Ideally we track a lifetime stats. 
        # For now, approximate with inventory count + sold count if we tracked it (we don't fully).
        # Improving: "total_caught" in stats.
        total_caught = stats.get("total_caught", 0)
        
        total_money = stats.get("lifetime_money", 0)
        
        owned_rods_count = 0
        rods_list = inv.get("rods", [])
        if rods_list:
            owned_rods_count = len(rods_list)
        elif data.get("rod_type"): 
             owned_rods_count = 1
        
        new_badges = []
        for key, info in BADGES.items():
            if key in owned_badges: continue
            
            req_type = info["req_type"]
            val = info["req_val"]
            awarded = False
            
            if req_type == "total_fish" and total_caught >= val: awarded = True
            elif req_type == "total_earn" and total_money >= val: awarded = True
            elif req_type == "rod_count" and owned_rods_count >= val: awarded = True
            elif req_type == "dragon_balls":
                 uballs = inv.get("dragon_balls", [])
                 if len(uballs) >= 7: awarded = True
            elif req_type == "king_fish_all":
                 # Check if user caught all Fish with very high rate (Kings)
                 # We identify kings by spawn_rate <= 0.02 roughly, or by name match in BIOMES
                 # Let's count distinct kings caught.
                 
                 # Get all King names
                 all_kings = []
                 for _, b_data in BIOMES.items():
                     for f in b_data["fish"]:
                         if f.get("spawn_rate", 100) <= 0.02:
                             all_kings.append(f["name"])
                 
                 caught_kings = 0
                 for k_name in all_kings:
                     if k_name in fish_inv: caught_kings += 1
                 
                 if caught_kings >= len(all_kings) and len(all_kings) > 0: awarded = True
            
            if awarded:
                owned_badges.append(key)
                new_badges.append(info)
        
        if new_badges:
            stats["badges"] = owned_badges
            await self.db.update_fishing_data(user_id, stats=stats)
            if channel:
                desc = "\n".join([f"{b['emoji']} **{b['name']}**\n*{b['desc']}*" for b in new_badges])
                em = discord.Embed(title="🏅 HUY HIỆU MỚI!", description=f"Chúc mừng bạn đã đạt được:\n{desc}", color=discord.Color.orange())
                try:
                    await channel.send(f"<@{user_id}>", embed=em)
                except: pass

    async def process_fishing(self, interaction, biome_name, view=None):
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id
        
        if hasattr(interaction, "channel_id") and interaction.channel_id: channel_id = interaction.channel_id
        else: channel_id = interaction.channel.id
        
        if hasattr(interaction, "guild_id"): guild_id = interaction.guild_id
        elif hasattr(interaction, "guild") and interaction.guild: guild_id = interaction.guild.id
        else: guild_id = 0
        
        # Check channel config
        config_channel = await self.db.get_channel_config(channel_id)
        if config_channel != "cauca":
            msg = "❌ Lệnh `/fish` chỉ hoạt động trong kênh Câu Cá chuyên biệt! Admin hãy dùng `/kenh-cau-ca` để cài đặt."
            await self._respond(interaction, msg, ephemeral=True)
            return

        data = await self.db.get_fishing_data(user_id)
        inventory = data.get("inventory", {})
        stats = data.get("stats", {})

        # === REQUIREMENTS CHECK ===
        user_balance = await self.db.get_player_points(user_id, guild_id)
        owned_rods = inventory.get("rods", [])
        
        # 1. New User: First Rod (Plastic Rod - Free)
        if not owned_rods:
            # Grant free Plastic Rod
            if "rods" not in inventory: inventory["rods"] = []
            if "Plastic Rod" not in inventory["rods"]:
                inventory["rods"].append("Plastic Rod")
            
            # Initialize durability (Plastic Rod is usually infinite/None, but we can set it if needed)
            if "rod_durability" not in inventory: inventory["rod_durability"] = {}
            # RODS["Plastic Rod"]["durability"] is likely None, which means infinite
            
            # Ensure Plastic Rod is active
            await self.db.update_fishing_data(user_id, rod_type="Plastic Rod", inventory=inventory)
            
            try: 
                 if hasattr(interaction, "channel"): await interaction.channel.send(f"🎉 **Chào mừng Newbie!** Hệ thống đã tặng bạn **Cần Nhựa** (Miễn phí) để bắt đầu câu cá!")
                 elif isinstance(interaction, commands.Context): await interaction.send(f"🎉 **Chào mừng Newbie!** Hệ thống đã tặng bạn **Cần Nhựa** (Miễn phí) để bắt đầu câu cá!")
            except: pass
            
            # Refresh data
            data = await self.db.get_fishing_data(user_id)
            stats = data.get("stats", {})
            inventory = data.get("inventory", {})

        # 2. Fishing Cost (10 Coiz)
        if user_balance < 10:
             msg = f"❌ Bạn cần **10 Coiz** {emojis.ANIMATED_EMOJI_COIZ} chi phí cho mỗi lần câu!"
             await self._respond(interaction, msg, ephemeral=True)
             return
             
        await self.db.add_points(user_id, guild_id, -10)
        
        # 3. Bait Check
        if not stats.get("current_bait"):
             # Check if user has any bait in inventory
             baits_inv = inventory.get("baits", {})
             has_bait = any(c > 0 for c in baits_inv.values())
             
             if has_bait:
                 msg = "⚠️ Bạn chưa trang bị mồi câu! Vui lòng chọn mồi bên dưới để bắt đầu:"
                 view_bait = ChangeBaitView(self, user_id, baits_inv, view)
                 await self._respond(interaction, msg, view=view_bait, ephemeral=True)
                 return
             else:
                 # Auto-equip free Worms
                 if "baits" not in inventory: inventory["baits"] = {}
                 inventory["baits"]["Worms"] = 50
                 stats["current_bait"] = "Worms"
                 await self.db.update_fishing_data(user_id, inventory=inventory, stats=stats)
                 
                 msg_auto = f"🪱 **Hết mồi?** Bot đã tự động trang bị **50x Mồi Giun** (Miễn phí) cho <@{user_id}>!"
                 try: 
                     if hasattr(interaction, "channel"): await interaction.channel.send(msg_auto)
                     elif isinstance(interaction, commands.Context): await interaction.send(msg_auto)
                 except: pass
        
        # Get Stats (Power/Luck)
        power, luck, data, current_bait_key, xp_mul = await self.get_stats_multiplier(user_id)
        rod_key = data.get("rod_type", "Plastic Rod")
        
        # === DURABILITY CHECK ===
        durability_map = inventory.get("rod_durability", {})
        if rod_key not in durability_map:
             # Auto-fix missing durability
             max_d = RODS.get(rod_key, {}).get("durability")
             if max_d:
                 durability_map[rod_key] = max_d
             else:
                 # Infinite durability for Plastic/Donator
                 pass
        
        current_durability = durability_map.get(rod_key)
        
        # If rod has durability and it's 0 (should not happen if we check after use, but safety first)
        if current_durability is not None and current_durability <= 0:
             # Remove rod
             if rod_key in inventory.get("rods", []):
                 inventory["rods"].remove(rod_key)
                 if rod_key in durability_map: del durability_map[rod_key]
             
             await self.db.update_fishing_data(user_id, inventory=inventory, rod_type="Plastic Rod")
             msg = f"💥 **CẦN CÂU CỦA BẠN ĐÃ BỊ GÃY!**\nCần **{RODS[rod_key]['name']}** đã hỏng hoàn toàn. Hãy mua cần mới!"
             await self._respond(interaction, msg, ephemeral=True)
             return

        # Bait Consumption Logic
        baits_inv = inventory.get("baits", {})
        sub_bait_key = stats.get("magnet_sub_bait")
        bait_consumed = False
        is_magnet = (current_bait_key == "Magnet")
        loops = 1
        
        if current_durability is not None:
             # Logic change: Durability consumes per CAST (not per fish)
             # But if loops > 1 (Magnet), does it consume more? 
             # Standard: 1 cast = 1 durability, regardless of 1 or 5 fish.
             
             durability_map[rod_key] -= 1
             inventory["rod_durability"] = durability_map
             
             if durability_map[rod_key] <= 0:
                 # ROD BREAKS AFTER THIS CAST
                 # We let the cast finish, then notify break at the end? or check at end?
                 # Let's handle break at the end of function to allow receiving the fish.
                 pass

        if current_bait_key:
             if baits_inv.get(current_bait_key, 0) > 0:
                 baits_inv[current_bait_key] -= 1
                 bait_consumed = True
                 
                 if baits_inv[current_bait_key] <= 0:
                     if current_bait_key in baits_inv: del baits_inv[current_bait_key]
                     stats["current_bait"] = None
                 
                 if is_magnet:
                     loops = random.randint(2, 5) # Magnet: 2-5 fish
             else:
                 stats["current_bait"] = None
                 is_magnet = False

        # Treasure Chance (Capped at 15% max, reduced scaling 0.002)
        # Fixes the issue where high Luck means 100% Treasure rate.
        treasure_chance = min(15, 2 + (luck * 0.002))
        treasure_found = False
        
        result_list = []
        
        total_xp = 0
        total_val = 0
        
        current_biome_data = BIOMES.get(biome_name, BIOMES["River"])
        fish_pool = current_biome_data["fish"]
        
        embed_color = discord.Color.blue()
        
        # Initialize variables for scope safety
        new_rod_type = None
        rod_broken_msg = ""
        
        # TREASURE CHECK
        treasure_chance = min(15, 2 + (luck * 0.002))
        treasure_found = False
        treasure_embed_desc = ""
        
        if random.uniform(0, 100) < treasure_chance:
            treasure_found = True
            chest_idx = min(len(TREASURES)-1, int(random.triangular(0, len(TREASURES)-1, 0 + luck/50)))
            chest = TREASURES[chest_idx]
            
            # Loot Logic
            rewards_list = []
            
            # 1. Coinz (Always)
            amount = int(chest["value"] * random.uniform(2.0, 5.0))
            await self.db.add_points(user_id, guild_id, amount)
            current_lt = stats.get("lifetime_money", 0)
            stats["lifetime_money"] = current_lt + amount
            rewards_list.append(f"• **{amount:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}")
            
            # 2. Fish (50% Chance)
            if random.random() < 0.5:
                weights = [f.get("spawn_rate", 10) for f in fish_pool]
                selected_fish = random.choices(fish_pool, weights=weights, k=1)[0]
                min_qty = 3 + (chest_idx * 2)
                max_qty = 10 + (chest_idx * 5)
                quantity = random.randint(min_qty, max_qty)
                unit_value = int(selected_fish['base_value'] * 1.5)
                total_f_val = unit_value * quantity
                
                if 'fish' not in inventory: inventory['fish'] = {}
                f_name = selected_fish['name']
                if f_name not in inventory['fish']:
                    inventory['fish'][f_name] = {"count": 0, "total_value": 0}
                inventory['fish'][f_name]["count"] += quantity
                inventory['fish'][f_name]["total_value"] += total_f_val
                stats["total_caught"] = stats.get("total_caught", 0) + quantity
                rewards_list.append(f"• **{quantity}x {selected_fish['emoji']} {selected_fish['name']}**")

            # 3. Bait (35% Chance)
            if random.random() < 0.35:
                 bait_keys = list(BAITS.keys())
                 selected_bait_key = random.choice(bait_keys)
                 selected_bait = BAITS[selected_bait_key]
                 min_qty = 5 + (chest_idx * 2)
                 max_qty = 10 + (chest_idx * 5)
                 quantity = random.randint(min_qty, max_qty)
                 if 'baits' not in inventory: inventory['baits'] = {}
                 inventory['baits'][selected_bait_key] = inventory['baits'].get(selected_bait_key, 0) + quantity
                 rewards_list.append(f"• **{quantity}x {selected_bait['emoji']} {selected_bait['name']}**")

            # 4. Charm (15% Chance)
            if random.random() < 0.15:
                charm_keys = list(CHARMS.keys())
                c_key = random.choice(charm_keys)
                c_info = CHARMS[c_key]
                duration_sec = random.randint(c_info["duration_min"] * 60, c_info["duration_max"] * 60)
                minutes = duration_sec // 60
                if "charms" not in inventory: inventory["charms"] = []
                new_charm = {"key": c_key, "duration": duration_sec, "name": c_info["name"]}
                inventory["charms"].append(new_charm)
                rewards_list.append(f"• **{c_info['emoji']} {c_info['name']}** ({minutes}p)")
            
            treasure_embed_desc = f"**{chest['emoji']} {chest['name']}**\n" + "\n".join(rewards_list)

            # DRAGON BALL DROP CHANCE (0.5%)
            if random.random() < 0.005: 
                user_balls = inventory.get("dragon_balls", [])
                missing_balls = [i for i in range(1, 8) if i not in user_balls]
                
                # Smart RNG: 80% to find a New Ball, 20% to find Random (potential duplicate)
                if missing_balls and random.random() < 0.8:
                    ball_num = random.choice(missing_balls)
                else:
                    ball_num = random.randint(1, 7)

                ball_emoji = DRAGON_BALLS[ball_num]["emoji"]

                if ball_num not in user_balls:
                     user_balls.append(ball_num)
                     user_balls.sort()
                     inventory["dragon_balls"] = user_balls
                     
                     treasure_embed_desc += f"\n\n🔥 **HUYỀN THOẠI!** Bạn đã tìm thấy **Ngọc Rồng {ball_num} Sao** {ball_emoji}! ({len(user_balls)}/7)"
                     if len(user_balls) == 7:
                         treasure_embed_desc += f"\n🐲 **BẠN ĐÃ CÓ ĐỦ 7 VIÊN NGỌC RỒNG!** Hãy dùng lệnh `/goi-rong` để triệu hồi Rồng Thần!"
                else:
                     # Duplicate Reward
                     treasure_embed_desc += f"\n\n🔸 Bạn tìm thấy **Ngọc Rồng {ball_num} Sao** {ball_emoji}, nhưng đã sở hữu rồi. (Nhận 100M Coiz an ủi)"
                     await self.db.add_points(user_id, guild_id, 100000000)

        # FISHING LOOP (ALWAYS RUNS)
        desc_lines = []
        if treasure_found:
             desc_lines.append(f"🌟 **---------------- KHO BÁU XUẤT HIỆN ----------------** 🌟")
             desc_lines.append(f"{treasure_embed_desc}")
             desc_lines.append(f"🌟 **-------------------------------------------------------** 🌟\n")
             desc_lines.append(f"🎣 **KẾT QUẢ CÂU:**")

        for _ in range(loops):
            # Calculate current catch stats (handles Magnet Sub-Bait)
            eff_luck = luck
            eff_power = power
            
            # Logic for Sub-Bait (Magnet Only)
            if is_magnet and sub_bait_key:
                # Apply sub-bait stats to THIS catch
                sb_data = BAITS[sub_bait_key]
                eff_luck += sb_data.get("luck", 0)
                eff_power += sb_data.get("power", 0)
                
                # Consume sub-bait?
                # "For each fish caught in a Magnet Bait attempt, consume 1 unit of the chosen secondary bait"
                # Check if available
                if baits_inv.get(sub_bait_key, 0) > 0:
                     baits_inv[sub_bait_key] -= 1
                     if baits_inv[sub_bait_key] <= 0:
                         del baits_inv[sub_bait_key]
                         stats["current_sub_bait"] = None # Reset if out
                         sub_bait_key = None # Stop applying for subsequent loops
                else:
                     sub_bait_key = None

            # MISS CHANCE (Tỉ lệ xảy cá)
            # Base success: 70%. Luck improves it.
            # Formula: 70 + (Luck * 0.2)
            success_chance = 70 + (eff_luck * 0.2)
            if success_chance > 100: success_chance = 100
            
            if random.uniform(0, 100) > success_chance:
                desc_lines.append("💨 **Hụt!** Cá đã trốn thoát...")
                continue

            # Rarity selection
            # Luck/Power affects weights? 
            
            luck_bonus = eff_luck * 0.15
            roll = random.uniform(0, 100) + luck_bonus
            
            rarity = "Common"
            if roll > 120: rarity = "Exotic" # Alien/Secret?
            elif roll > 110: rarity = "Mythical"
            elif roll > 95: rarity = "Legendary"
            elif roll > 80: rarity = "Epic"
            elif roll > 60: rarity = "Rare"
            elif roll > 40: rarity = "Uncommon"
            
            # Pick fish
            # Note: Currently fish_pool is list of dicts. We don't have explicit rarity in fish dicts in BIOMES constant yet?
            # The BIOMES constant has "fish": [{name, base_value, min, max, emoji}...]
            # We need to assign rarity or pick based on value?
            # For now, pick random fish from pool, then apply size multiplier based on power/rarity.
            
            if not fish_pool: break
            
            # Apply weight selection based on 'spawn_rate' modified by Luck
            weights = []
            for f in fish_pool:
                 base_rate = f.get("spawn_rate", 10)
                 
                 if base_rate < 1.0:
                      # BOSS FISH: FIXED RATE (No Luck Influence)
                      # Used to be boosted by luck, now requested to be fixed.
                      # We still need a slight multiplier from base because base_rate (e.g. 0.01) is purely theoretical relative to 100.
                      # If Common is 35, and Boss is 0.01, Boss is 3500x rarer.
                      # Let's keep a small static multiplier to make it distinct but rare.
                      w = base_rate * 5 # Static boost, no luck scaling.
                 elif base_rate <= 20: 
                      # Boost rare fish: +0.2% weight per 1 Luck
                      w = base_rate * (1 + (eff_luck * 0.002))
                 else:
                      # Common fish
                      w = base_rate
                 weights.append(w)
                 
            selected_fish = random.choices(fish_pool, weights=weights, k=1)[0]
            
            # Size calculation
            # Power affects size directly and skews distribution towards Max Size
            min_s = selected_fish['min_size']
            max_s = selected_fish['max_size']
            
            # Calculate "Peak" of the size distribution based on Power
            # Max power for scaling ~ 500 (can go higher but diminishes)
            power_factor = min(1.0, eff_power / 500) 
            
            # If power is high, the "peak" probability moves towards max_s
            # random.triangular(low, high, mode)
            mode_s = min_s + (max_s - min_s) * (0.2 + 0.8 * power_factor) # At 0 power, peak is at 20%. At max, peak is at 100%.
            
            raw_size = random.triangular(min_s, max_s, mode_s)
            
            # "Limit Break": Power allows exceeding max size slightly
            # 0.02% per Power point
            final_size_mul = 1.0 + (eff_power * 0.0002)
            size = round(raw_size * final_size_mul, 2)
            
            min_s = selected_fish['min_size']

            
            # Value calculation
            # Value = Base * (Size / AvgSize) * RarityMul?
            # Simplify: Value = Base + (Size * 2)
            base_v = selected_fish['base_value']
            rarity_mul = RARITIES.get(rarity, {}).get("mul", 1.0)
            val = int((base_v + (size * 5)) * rarity_mul)
            
            # Crit?
            if random.random() < 0.05:
                val *= 2
                size_bonus = "(CRIT!)"
            
            # Add to result
            result_list.append({
                "name": selected_fish['name'], 
                "value": val, 
                "emoji": selected_fish['emoji'],
                "size": size,
                "rarity": rarity
            })
            
            # Update Inventory
            if 'fish' not in inventory: inventory['fish'] = {}
            f_name = selected_fish['name']
            if f_name not in inventory['fish']:
                inventory['fish'][f_name] = {"count": 0, "total_value": 0}
                
            inventory['fish'][f_name]["count"] += 1
            inventory['fish'][f_name]["total_value"] += val
            
            stats["total_caught"] = stats.get("total_caught", 0) + 1
            total_val += val
                
            # XP Calculation: Scales with Value (Size & Rarity included)
            xp_rarity_mul = {
                "Common": 1.0, 
                "Uncommon": 1.2, 
                "Rare": 1.5,
                "Epic": 2.5, 
                "Legendary": 10.0, 
                "Mythical": 50.0,
                "Exotic": 100.0
            }.get(rarity, 1.0)
            
            # Formula: Base XP (Value/50) * RarityXP
            xp_gain = int((val / 50) * xp_rarity_mul) 
            if xp_gain < 10: xp_gain = 10
            
            # Apply XP Charm Multiplier
            xp_gain = int(xp_gain * xp_mul)
            
            total_xp += xp_gain
            
            # Get rarity info
            r_info = RARITIES.get(rarity, {"emoji": "✨", "color": 0xFFFFFF})
            r_emoji = r_info.get("emoji", "✨")
            
            # Translate rarity
            rarity_vi = {
                "Common": "Thường", "Uncommon": "Khá", "Rare": "Hiếm", 
                "Epic": "Sử Thi", "Huyền Thoại": "Huyền Thoại", 
                "Mythical": "Thần Thoại", "Exotic": "Cực Phẩm"
            }.get(rarity, rarity)
            
            is_boss = selected_fish.get("spawn_rate", 10) < 1.0
            
            if is_boss:
                 desc_lines.append(f"\n🌟 **---------------- VUA CÁ XUẤT HIỆN ----------------** 🌟")
                 desc_lines.append(f"👑 {r_emoji} **{rarity_vi}** | {selected_fish['emoji']} **{selected_fish['name']}** ({size}cm) - **BOSS**")
                 desc_lines.append(f"🌟 **-------------------------------------------------------** 🌟\n")
            else:
                 desc_lines.append(f"{r_emoji} **{rarity_vi}** | {selected_fish['emoji']} **{selected_fish['name']}** ({size}cm)")

        # Check Rod Break Status before creating Embed
        rod_broken_msg = ""
        user_dura = inventory.get("rod_durability", {}).get(rod_key)
        new_rod_type = None # Default: No change
        
        if user_dura is not None and user_dura <= 0:
             # Remove rod from inventory
             if "rods" in inventory and rod_key in inventory["rods"]:
                 inventory["rods"].remove(rod_key)
             if "rod_durability" in inventory and rod_key in inventory["rod_durability"]:
                 del inventory["rod_durability"][rod_key]
             
             # Prepare to reset rod to Plastic
             new_rod_type = "Plastic Rod"
             rod_broken_msg = f"\n\n💥 **CẦN CÂU ĐÃ GÃY!**\nCần **{RODS[rod_key]['name']}** của bạn đã hỏng hoàn toàn do hết độ bền. Hãy mua cần mới!"

        title = "🎣 CÂU ĐƯỢC CÁ!"
        if is_magnet: title = f"🧲 NAM CHÂM HÚT ĐƯỢC {len(result_list)} CÁ!"
        if treasure_found: title += " & KHO BÁU!"
        
        embed = discord.Embed(title=title, color=embed_color)
        embed.description = "\n".join(desc_lines)
        embed.add_field(name="Tổng kết", value=f"Exp: +{total_xp} | Giá trị: {total_val:,} Coiz {emojis.ANIMATED_EMOJI_COIZ}{rod_broken_msg}")
        
        dura_info = ""
        if user_dura is not None:
            max_dura = RODS[rod_key]['durability']
            dura_info = f" | Độ bền: {max(0, user_dura)}/{max_dura}"
        
        # Level Up Logic
        current_level = stats.get("level", 1)
        current_xp = stats.get("xp", 0) + total_xp
        
        # Recalculate level
        # Formula: Next Level XP = 1000 * (1.5 ^ (level - 1))
        # Loop incase of multi-level up
        leveled_up = False
        while True:
            req_xp = int(1000 * (1.35 ** (current_level - 1)))
            if current_xp >= req_xp:
                current_xp -= req_xp
                current_level += 1
                leveled_up = True
            else:
                break
        
        stats["xp"] = current_xp
        stats["level"] = current_level
        
        if leveled_up:
            try:
                msg = f"🎉 **LEVEL UP!** Chúc mừng <@{user_id}> đã đạt **Level {current_level}**! Mở khóa các khu vực mới!"
                if hasattr(interaction, "channel"): await interaction.channel.send(msg)
                elif isinstance(interaction, commands.Context): await interaction.send(msg)
            except: pass

        dura_info = ""
        if user_dura is not None:
            max_dura = RODS[rod_key]['durability']
            dura_info = f" | Độ bền: {max(0, user_dura)}/{max_dura}"
            
        req_xp_next = int(1000 * (1.35 ** (current_level - 1)))
        embed.set_footer(text=f"Level: {current_level} | XP: {current_xp}/{req_xp_next}{dura_info}")

        # Save Data
        save_kwargs = {"inventory": inventory, "stats": stats}
        if new_rod_type:
            save_kwargs["rod_type"] = new_rod_type
            
        await self.db.update_fishing_data(user_id, **save_kwargs)

        
        # Check Badges
        await self.check_badges(user_id, interaction.channel)
        
        # UI
        last_catch_data = result_list if result_list else None
        new_view = FishingView(self, user_id, biome_name, last_catch=last_catch_data)
        
        if view:
             view.stop()
             await self._respond(interaction, embed=embed, view=new_view)
        else:
             msg = await self._respond(interaction, embed=embed, view=new_view)
             new_view.message = msg






    async def fish(self, interaction):
        if hasattr(interaction, "response"): # Interaction
            await interaction.response.defer()
        
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id

        data = await self.db.get_fishing_data(user_id)
        current_biome = data.get("stats", {}).get("current_biome", "River") # Default to River now
        
        # Trigger fishing
        await self.process_fishing(interaction, current_biome)

    async def biomes_cmd(self, interaction):
        await self.show_biomes_ui(interaction)

    async def show_biomes_ui(self, interaction):
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id
        
        data = await self.db.get_fishing_data(user_id)
        stats = data.get("stats", {})
        current = stats.get("current_biome", "River")
        unlocked = stats.get("unlocked_biomes", ["River"])
        # Ensure default unlock
        if "River" not in unlocked: 
            unlocked.append("River")
            stats["unlocked_biomes"] = unlocked
            await self.db.update_fishing_data(user_id, stats=stats) # Sync fix if needed
            
        xp = stats.get("xp", 0)
        level = stats.get("level", 1)
        
        curr_info = BIOMES.get(current, BIOMES["River"])
        
        embed = discord.Embed(title="🗺️ BẢN ĐỒ CÂU CÁ", color=discord.Color.teal())
        embed.description = f"Hiện tại đang ở: **{curr_info['emoji']} {curr_info['name']}**\nLevel: **{level}** | XP: **{xp:,}**"
        
        view = discord.ui.View()
        
        async def unlock_or_travel(interaction: discord.Interaction, biome_key: str):
            # Refresh data
            d = await self.db.get_fishing_data(interaction.user.id)
            s = d.get("stats", {})
            u = s.get("unlocked_biomes", ["River"])
            
            if biome_key in u:
                s["current_biome"] = biome_key
                await self.db.update_fishing_data(interaction.user.id, stats=s)
                b_info = BIOMES[biome_key]
                msg = f"✈️ Đã chuyển đến **{b_info['emoji']} {b_info['name']}**!"
                if interaction.response.is_done():
                     await interaction.followup.send(msg, ephemeral=True)
                else:
                     await interaction.response.send_message(msg, ephemeral=True)
            else:
                # Try unlock
                target = BIOMES[biome_key]
                cost = target["req_money"]
                req_level = target["req_level"]
                
                u_bal = await self.db.get_player_points(interaction.user.id, interaction.guild_id)
                curr_level = s.get("level", 1)
                
                if curr_level < req_level:
                    await self._respond(interaction, f"❌ Bạn chưa đủ Level {req_level} để mở khóa!", ephemeral=True)
                    return
                # Show confirmation regardless of money (or check money here too?)
                # User asked: "if level is enough, show confirm button to use money"
                # It's better to verify money first to avoid disappointment, but let's follow logic:
                # Check money inside View or before? 
                # Let's check money here to give immediate feedback if too poor, 
                # BUT request says "confirm to use money", implying the choice happens then.
                # I will show the view if Level is met. The view handles money check.
                
                view_confirm = ConfirmUnlockView(self, interaction.user.id, biome_key, cost)
                msg_txt = f"🔓 **MỞ KHÓA VÙNG MỚI**\nBạn có muốn dùng **{cost:,} Coiz** {emojis.ANIMATED_EMOJI_COIZ} để mở khóa **{target['emoji']} {target['name']}** không?"
                
                if interaction.response.is_done():
                    await interaction.followup.send(msg_txt, view=view_confirm, ephemeral=True)
                else:
                    await interaction.response.send_message(msg_txt, view=view_confirm, ephemeral=True)

        select = discord.ui.Select(placeholder="Chọn khu vực để đi...")
        
        for key, info in BIOMES.items():
            label = info['name']
            is_unlocked = key in unlocked
            desc_s = "Đã mở khóa (Nhấn để đi)" if is_unlocked else f"Yêu cầu: Level {info['req_level']} | {info['req_money']:,} Coiz"
            emoji = info['emoji']
            select.add_option(label=label, value=key, description=desc_s, emoji=emoji)
        
        async def select_callback(inter):
            val = select.values[0]
            await unlock_or_travel(inter, val)
        
        select.callback = select_callback
        view.add_item(select)
        
        await self._respond(interaction, embed=embed, view=view, ephemeral=True)

    async def shop(self, interaction):
        view = ShopSelectView(self)
        await self._respond(interaction, "🏪 **CHÀO MỪNG ĐẾN CỬA HÀNG!**\nBạn muốn xem loại hàng nào?", view=view, ephemeral=True)

    async def bait_shop(self, interaction):
        # 1. Embed listing all baits
        embed = discord.Embed(title="🪱 CỬA HÀNG MỒI CÂU", description="Chọn loại mồi bạn muốn mua bên dưới.", color=discord.Color.dark_green())
        
        for key, info in BAITS.items():

            # User mentioned price for 1 bait
            embed.add_field(
                name=f"{info['emoji']} {info['name']}",
                value=f"💰 Giá: **{info['price']:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}/cái\n💪 Power: +{info['power']} | 🍀 Luck: +{info['luck']}\n*{info['desc']}*",
                inline=False
            )
            
        # 2. View with Buttons for each bait
        view = discord.ui.View()
        
        # Define Modal locally or as a class
        class BaitAmountModal(discord.ui.Modal):
            def __init__(self, bait_key, bait_info, db, parent_view):
                super().__init__(title=f"Mua {bait_info['name']}")
                self.bait_key = bait_key
                self.bait_info = bait_info
                self.db = db
                self.parent_view = parent_view
                
                self.amount = discord.ui.TextInput(
                    label="Số lượng cần mua",
                    placeholder="Ví dụ: 10, 50, 100...",
                    min_length=1,
                    max_length=5,
                    required=True
                )
                self.add_item(self.amount)

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    qty = int(self.amount.value)
                    if qty <= 0: raise ValueError
                except ValueError:
                    await interaction.response.send_message("❌ Số lượng không hợp lệ!", ephemeral=True)
                    return
                
                cost = self.bait_info["price"] * qty
                user_point = await self.db.get_player_points(interaction.user.id, interaction.guild_id)
                
                if user_point < cost:
                    await interaction.response.send_message(f"❌ Bạn không đủ **{cost:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ} để mua {qty}x {self.bait_info['name']}!", ephemeral=True)
                    return
                
                # Proceed Transaction
                await self.db.add_points(interaction.user.id, interaction.guild_id, -cost)
                
                data = await self.db.get_fishing_data(interaction.user.id)
                inv = data.get("inventory", {})
                if "baits" not in inv: inv["baits"] = {}
                
                inv["baits"][self.bait_key] = inv["baits"].get(self.bait_key, 0) + qty
                
                # Auto equip if none
                stats = data.get("stats", {})
                if not stats.get("current_bait"):
                    stats["current_bait"] = self.bait_key
                
                await self.db.update_fishing_data(interaction.user.id, inventory=inv, stats=stats)
                
                await interaction.response.send_message(f"✅ Đã mua thành công **{qty}x {self.bait_info['emoji']} {self.bait_info['name']}** với giá **{cost:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}!", ephemeral=True)

        async def bait_button_callback(interaction: discord.Interaction):
            # Hacky way to get the button that was clicked
            # But we can bind specific callback
            pass

        # Dynamically create buttons
        for key, info in BAITS.items():
            # if info.get("is_special"): continue 
            # Allow Magnet buying? Yes, user asked for magnet earlier.
            
            btn = discord.ui.Button(label=info['name'], emoji=info['emoji'], style=discord.ButtonStyle.secondary)
            
            # Closure to capture key variable
            async def callback(inter, k=key, i=info):
                modal = BaitAmountModal(k, i, self.db, view)
                await inter.response.send_modal(modal)
            
            btn.callback = callback
            view.add_item(btn)

        back_btn = discord.ui.Button(label="Trang Chủ", style=discord.ButtonStyle.secondary, emoji="🏠", row=2)
        async def back_callback(inter):
            if inter.user.id != interaction.user.id: return
            view = ShopSelectView(self)
            await inter.response.edit_message(content="🏪 **CHÀO MỪNG ĐẾN CỬA HÀNG!**\nBạn muốn xem loại hàng nào?", embed=None, view=view)
        back_btn.callback = back_callback
        view.add_item(back_btn)

        await self._respond(interaction, embed=embed, view=view)

    async def rod_shop(self, interaction):
        # 1. Embed listing all rods
        user_id = interaction.user.id
        data = await self.db.get_fishing_data(user_id)
        current_rod_key = data.get("rod_type", "Plastic Rod")
        current_rod_info = RODS.get(current_rod_key, RODS["Plastic Rod"])

        embed = discord.Embed(title="🎣 CỬA HÀNG CẦN CÂU", description=f"Cần câu hiện tại: **{current_rod_info['emoji']} {current_rod_info['name']}**", color=discord.Color.blue())
        
        buyable_rods = []
        for key in ROD_LIST:
            info = RODS[key]
            if info["price"] > 0:
                buyable_rods.append((key, info))
                embed.add_field(
                    name=f"{info['emoji']} {info['name']}",
                    value=f"💰 Giá: **{info['price']:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}\n💪 Power: {info['power']} | 🍀 Luck: {info['luck']} | 🔧 Độ bền: {info['durability']}",
                    inline=False
                )
        
        # 2. View with Buttons
        view = discord.ui.View()
        
        class ConfirmBuyView(discord.ui.View):
            def __init__(self, rod_key, rod_info, db, parent_interaction):
                super().__init__(timeout=60)
                self.rod_key = rod_key
                self.rod_info = rod_info
                self.db = db
                self.value = None
                
            @discord.ui.button(label="Xác nhận mua", style=discord.ButtonStyle.success, emoji="✅")
            async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                # Check prerequisites
                data = await self.db.get_fishing_data(interaction.user.id)
                inv = data.get("inventory", {})
                owned_rods = inv.get("rods", ["Plastic Rod"])
                if not owned_rods: owned_rods = ["Plastic Rod"]

                if self.rod_key in owned_rods:
                     await interaction.response.edit_message(content="❌ Bạn đã sở hữu cần này rồi!", view=None)
                     return

                # Check strict progression
                try:
                    curr_idx = ROD_LIST.index(self.rod_key)
                    if curr_idx > 0:
                        prev_rod = ROD_LIST[curr_idx - 1]
                        if prev_rod not in owned_rods:
                             prev_rod_name = RODS.get(prev_rod, {}).get("name", prev_rod)
                             await interaction.response.edit_message(content=f"❌ Bạn cần sở hữu **{prev_rod_name}** trước khi mua cần này!", view=None)
                             return
                except ValueError:
                    pass # Rod key not in list? Should not happen if data is consistent

                user_point = await self.db.get_player_points(interaction.user.id, interaction.guild_id)
                cost = self.rod_info["price"]
                
                if user_point < cost:
                    await interaction.response.edit_message(content="❌ Bạn không đủ tiền!", view=None)
                    return

                await self.db.add_points(interaction.user.id, interaction.guild_id, -cost)
                
                # Update Inventory and Equip
                if "rods" not in inv: inv["rods"] = owned_rods
                if self.rod_key not in inv["rods"]:
                    inv["rods"].append(self.rod_key)
                    
                # Initialize Durability
                if "rod_durability" not in inv: inv["rod_durability"] = {}
                inv["rod_durability"][self.rod_key] = RODS[self.rod_key]["durability"]
                
                await self.db.update_fishing_data(interaction.user.id, rod_type=self.rod_key, inventory=inv)
                
                await interaction.response.edit_message(content=f"🎉 Chúc mừng! Bạn đã sở hữu **{self.rod_info['emoji']} {self.rod_info['name']}**!", view=None)
                self.value = True
                self.stop()

            @discord.ui.button(label="Hủy bỏ", style=discord.ButtonStyle.danger, emoji="❌")
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.edit_message(content="Đã hủy giao dịch.", view=None)
                self.value = False
                self.stop()

        for key, info in buyable_rods:
            # Button for each rod
            # Style update: highlight if current? discord buttons don't support custom css.
            style = discord.ButtonStyle.primary if key == current_rod_key else discord.ButtonStyle.secondary
            if key == current_rod_key:
                # Add durability info to label if possible
                dura = data.get("inventory", {}).get("rod_durability", {}).get(key)
                max_dura = info.get("durability")
                d_str = ""
                if dura is not None and max_dura:
                    d_str = f" [{dura}/{max_dura}]"
                label = f"{info['name']} (Đang dùng){d_str}"
                disabled = True
            else:
                label = info['name']
                disabled = False
                
            btn = discord.ui.Button(label=label, emoji=info['emoji'], style=style, disabled=disabled)
            
            async def callback(inter, k=key, i=info):
                # Trigger Confirmation
                confirm_view = ConfirmBuyView(k, i, self.db, inter)
                await inter.response.send_message(
                    f"Bạn có chắc muốn mua **{i['emoji']} {i['name']}** với giá **{i['price']:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ} không?",
                    view=confirm_view,
                    ephemeral=True
                )
            
            btn.callback = callback
            view.add_item(btn)

        back_btn = discord.ui.Button(label="Trang Chủ", style=discord.ButtonStyle.secondary, emoji="🏠", row=4)
        async def back_callback(inter):
            if inter.user.id != interaction.user.id: return
            view = ShopSelectView(self)
            await inter.response.edit_message(content="🏪 **CHÀO MỪNG ĐẾN CỬA HÀNG!**\nBạn muốn xem loại hàng nào?", embed=None, view=view)
        back_btn.callback = back_callback
        view.add_item(back_btn)

        await interaction.response.send_message(embed=embed, view=view)

    async def inventory(self, interaction):
        data = await self.db.get_fishing_data(interaction.user.id)
        current_rod = data.get("rod_type", "Plastic Rod")
        
        # Default view shows current rod or summary?
        # Let's show Rods by default or just the menu with instruction
        
        embed = discord.Embed(title=f"🎒 TÚI ĐỒ CỦA {interaction.user.display_name.upper()}", description="Chọn danh mục bên dưới để xem chi tiết.", color=discord.Color.gold())
        
        view = InventoryView(self, interaction.user.id, data)
        await self._respond(interaction, embed=embed, view=view, ephemeral=True)

    async def fish_stats_cmd(self, interaction):
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id
        power, luck, data, bait_key, xp_mul = await self.get_stats_multiplier(user_id)
        stats = data.get("stats", {})
        
        level = stats.get("level", 1)
        xp = stats.get("xp", 0)
        req_xp = int(1000 * (1.35 ** (level - 1)))
        
        # Calculate Rank
        rank = await self.db.get_fishing_rank(user_id)
        
        # Progress Bar
        pct = min(1.0, xp / max(1, req_xp))
        bar_len = 10
        filled = int(pct * bar_len)
        bar = "🟦" * filled + "⬜" * (bar_len - filled)
        
        embed = discord.Embed(title=f"📊 THÔNG SỐ CẦN THỦ: {interaction.user.display_name}", color=discord.Color.purple())
        
        embed.add_field(name="🏅 Xếp Hạng", value=f"TOP **#{rank}**", inline=True)
        embed.add_field(name="⭐ Cấp Độ", value=f"**Level {level}**\n{bar}\n({xp}/{req_xp} XP)", inline=True)
        
        # Buff Details
        rod_key = data.get("rod_type", "Plastic Rod")
        rod_info = RODS.get(rod_key, {})
        
        bait_info = BAITS.get(bait_key, {"power": 0, "luck": 0}) if bait_key else {"power": 0, "luck": 0}
        
        active_charms = stats.get("active_charms", {})
        charm_power = power - rod_info.get("power",0) - bait_info.get("power",0)
        charm_luck = luck - rod_info.get("luck",0) - bait_info.get("luck",0)

        buff_desc = (
            f"⚔️ **POWER: {power}** (Rod: {rod_info.get('power',0)} + Bait: {bait_info.get('power',0)} + Charm: {charm_power})\n"
            f"🍀 **LUCK: {luck}** (Rod: {rod_info.get('luck',0)} + Bait: {bait_info.get('luck',0)} + Charm: {charm_luck})"
        )
        embed.add_field(name="💪 Chỉ Số Sức Mạnh", value=buff_desc, inline=False)
        
        await self._respond(interaction, embed=embed)

    async def summon_shenron(self, interaction):
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id

        data = await self.db.get_fishing_data(user_id)
        inv = data.get("inventory", {})
        user_balls = inv.get("dragon_balls", [])
        
        if len(user_balls) < 7:
            await self._respond(interaction, f"❌ Bạn chưa đủ 7 viên ngọc rồng! Hiện có: {len(user_balls)}/7", ephemeral=True)
            return

        # Modal to make wish
        class WishModal(discord.ui.Modal):
            def __init__(self, db, parent_cog):
                super().__init__(title="🐲 ĐIỀU ƯỚC CỦA RỒNG THẦN")
                self.db = db
                self.parent_cog = parent_cog
                
                self.wish_amount = discord.ui.TextInput(
                    label="Nhập số tiền bạn muốn (Tối đa 5 Tỷ)",
                    placeholder="Ví dụ: 5000000000",
                    min_length=1,
                    max_length=15, # 5B is 10 digits
                    required=True
                )
                self.add_item(self.wish_amount)

            async def on_submit(self, inter: discord.Interaction):
                try:
                    amount_req = int(self.wish_amount.value.replace(".", "").replace(",", "")) # Handle basic formatting
                    if amount_req <= 0: raise ValueError
                    if amount_req > 5_000_000_000:
                        await inter.response.send_message("❌ Rồng Thần bảo: 'Tham thì thâm! Ta chỉ cho tối đa 5 Tỷ thôi!'", ephemeral=True)
                        return
                        
                    # Grant wish
                    await self.db.add_points(inter.user.id, inter.guild_id, amount_req)
                    
                    # Consume balls
                    d = await self.db.get_fishing_data(inter.user.id)
                    inventory = d.get("inventory", {})
                    inventory["dragon_balls"] = [] # Clear balls
                    await self.db.update_fishing_data(inter.user.id, inventory=inventory)
                    
                    # Announcement Embed
                    embed = discord.Embed(title="🐲 RỒNG THẦN ĐÃ XUẤT HIỆN!", description=f"**{inter.user.name}** đã tập hợp đủ 7 viên ngọc rồng và triệu hồi Rồng Thần!\n\n🌌 **ĐIỀU ƯỚC ĐÃ ĐƯỢC THỰC HIỆN:**\nNgười chơi nhận được **{amount_req:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}!", color=discord.Color.dark_green())
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1305556786304127097/1451098687999578224/tenor.gif?ex=6944f077&is=69439ef7&hm=e0b76ba5377dbe0153382c5fde7b02c008ab0f5631fb0d7a46366e38dbf6ceea&") # Shenron GIF placeholder or emoji
                    embed.set_thumbnail(url=inter.user.avatar.url if inter.user.avatar else None)
                    
                    # Ping everyone as requested
                    # Using send_message limits us to current channel properties.
                    # We send a standard message.
                    await inter.response.send_message(content="@everyone", embed=embed)
                    
                except ValueError:
                    await inter.response.send_message("❌ Số tiền không hợp lệ!", ephemeral=True)

        if hasattr(interaction, "response"):
            await interaction.response.send_modal(WishModal(self.db, self))
        else:
             await interaction.send("🐉 Vui lòng dùng lệnh `/fish goi-rong` để thực hiện điều ước!")

    async def sell(self, interaction):
        if hasattr(interaction, "response"): await interaction.response.defer(ephemeral=False)
        
        if hasattr(interaction, "user"): user_id = interaction.user.id
        else: user_id = interaction.author.id
        
        if hasattr(interaction, "guild_id"): guild_id = interaction.guild_id
        elif hasattr(interaction, "guild") and interaction.guild: guild_id = interaction.guild.id
        else: guild_id = 0
        
        data = await self.db.get_fishing_data(user_id)
        inv = data.get("inventory", {})
        fish_inv = inv.get("fish", {})
        
        if not fish_inv:
             await self._respond(interaction, "🎒 Không có cá để bán!", ephemeral=True)
             return

        # Separate Normal and Boss Fish
        normal_fish_to_sell = []
        boss_fish_hold = []
        
        # Helper to identify boss
        fish_meta = {}
        for b_val in BIOMES.values():
            for f in b_val["fish"]:
                fish_meta[f["name"]] = f

        for name, info in fish_inv.items():
            count = info.get("count", 0)
            if count <= 0: continue
            
            meta = fish_meta.get(name, {"spawn_rate": 10})
            is_boss = meta.get("spawn_rate", 10) < 1.0
            
            if is_boss:
                boss_fish_hold.append(name)
            else:
                normal_fish_to_sell.append(name)

        total_sold_val = 0
        sold_count = 0
        
        # 1. Auto-Sell Normal Fish
        stats = data.get("stats", {})
        
        for name in normal_fish_to_sell:
            info = fish_inv[name]
            val = info["total_value"]
            count = info["count"]
            
            total_sold_val += val
            sold_count += count
            
            # Remove from inv
            del fish_inv[name]
            
        if total_sold_val > 0:
            stats["lifetime_money"] = stats.get("lifetime_money", 0) + total_sold_val
            await self.db.update_fishing_data(user_id, inventory=inv, stats=stats)
            await self.db.add_points(user_id, guild_id, total_sold_val)
            await self.check_badges(user_id, interaction.channel)

        msg = ""
        if sold_count > 0:
            msg = f"✅ Đã tự động bán **{sold_count}** con cá thường với giá **{total_sold_val:,}** Coiz {emojis.ANIMATED_EMOJI_COIZ}."
        else:
            msg = "🎒 Không có cá thường để bán."

        # 2. Check Boss Fish
        if not boss_fish_hold:
            await self._respond(interaction, msg)
            return

        # Prompt for Boss Fish
        msg += f"\n👑 Bạn đang sở hữu **{len(boss_fish_hold)} loại Boss cá**! Bạn có muốn bán chúng luôn không?"

        class SellBossView(discord.ui.View):
            def __init__(self, cog, user_id, boss_list, db, parent_inv):
                super().__init__(timeout=60)
                self.cog = cog
                self.user_id = user_id
                self.boss_list = boss_list
                self.db = db
                self.parent_inv = parent_inv

            @discord.ui.button(label="Có, muốn bán Boss", style=discord.ButtonStyle.danger, emoji="💰")
            async def yes_sell_boss(self, inter: discord.Interaction, button: discord.ui.Button):
                if inter.user.id != self.user_id: return
                
                # Show Boss Selection View
                view = BossSelectionView(self.cog, self.user_id, self.boss_list, self.db, self.parent_inv)
                await inter.response.edit_message(content="👇 **Chọn loại Boss muốn bán:**", view=view)

            @discord.ui.button(label="Không, giữ lại", style=discord.ButtonStyle.secondary, emoji="🛡️")
            async def no_sell_boss(self, inter: discord.Interaction, button: discord.ui.Button):
                if inter.user.id != self.user_id: return
                await inter.response.edit_message(content=f"{msg}\n✅ Đã giữ lại các Boss cá.", view=None)

        class BossSelectionView(discord.ui.View):
            def __init__(self, cog, user_id, boss_list, db, parent_inv):
                super().__init__(timeout=120)
                self.cog = cog
                self.user_id = user_id
                self.boss_list = boss_list
                self.db = db
                self.parent_inv = parent_inv
                
                # Create button for each boss
                fish_meta = {}
                for b_val in BIOMES.values():
                    for f in b_val["fish"]:
                        fish_meta[f["name"]] = f

                for b_name in boss_list:
                    # Get current count
                    c_info = self.parent_inv.get("fish", {}).get(b_name, {})
                    cnt = c_info.get("count", 0)
                    if cnt <= 0: continue
                    
                    b_meta = fish_meta.get(b_name, {"emoji": "👑"})
                    emoji = b_meta.get("emoji", "👑")
                    
                    btn = discord.ui.Button(label=f"{b_name} (x{cnt})", emoji=emoji, style=discord.ButtonStyle.danger)
                    
                    async def callback(inter, name=b_name, count=cnt):
                        modal = SellBossAmountModal(name, count, self.db, self.cog)
                        await inter.response.send_modal(modal)
                        
                    btn.callback = callback
                    self.add_item(btn)

        class SellBossAmountModal(discord.ui.Modal):
            def __init__(self, boss_name, max_count, db, cog):
                super().__init__(title=f"Bán {boss_name}")
                self.boss_name = boss_name
                self.max_count = max_count
                self.db = db
                self.cog = cog
                
                self.amount = discord.ui.TextInput(
                    label=f"Nhập số lượng (Có sẵn: {max_count})",
                    placeholder="Ví dụ: 1",
                    min_length=1,
                    max_length=5,
                    required=True
                )
                self.add_item(self.amount)

            async def on_submit(self, inter: discord.Interaction):
                try:
                    qty = int(self.amount.value)
                    if qty <= 0 or qty > self.max_count: raise ValueError
                except ValueError:
                    await inter.response.send_message("❌ Số lượng không hợp lệ!", ephemeral=True)
                    return
                
                # Fetch fresh data to ensure transaction safety
                d = await self.db.get_fishing_data(inter.user.id)
                inv = d.get("inventory", {})
                f_inv = inv.get("fish", {})
                
                if self.boss_name not in f_inv or f_inv[self.boss_name]["count"] < qty:
                    await inter.response.send_message("❌ Số lượng không đủ hoặc đã thay đổi!", ephemeral=True)
                    return
                
                # Calculate value (Average val * qty)
                # Or just proportional?
                # info["total_value"] is total value of all items. 
                # Avg value = total / count.
                total_v = f_inv[self.boss_name]["total_value"]
                curr_c = f_inv[self.boss_name]["count"]
                avg_val = total_v // curr_c
                
                sell_val = avg_val * qty
                
                # Update
                f_inv[self.boss_name]["count"] -= qty
                f_inv[self.boss_name]["total_value"] -= sell_val
                if f_inv[self.boss_name]["count"] <= 0:
                    del f_inv[self.boss_name]
                    
                s = d.get("stats", {})
                s["lifetime_money"] = s.get("lifetime_money", 0) + sell_val
                
                await self.db.update_fishing_data(inter.user.id, inventory=inv, stats=s)
                await self.db.add_points(inter.user.id, inter.guild_id, sell_val)
                
                await inter.response.send_message(f"✅ Đã bán **{qty}x {self.boss_name}** với giá **{sell_val:,}** Coiz!", ephemeral=True)

        view = SellBossView(self, user_id, boss_fish_hold, self.db, inv)
        await self._respond(interaction, msg, view=view)

# Setup removed
