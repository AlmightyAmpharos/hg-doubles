import re
import json

INPUT_FILE = "./data/itemdata/itemdata.c"

DESCRIPTION_FILES = [
"./data/text/830.txt",
"./data/text/834.txt",
"./data/text/838.txt",
"./data/text/842.txt",
"./data/text/846.txt",
"./data/text/850.txt"
]

OUTPUT_FILE = "./website/webdata/items.json"

# --------------------------------------------------

# POCKETS

# --------------------------------------------------

POCKET_MAP = {
    "POCKET_MEDICINE": "Medicine",
    "POCKET_BALLS": "Poké Balls",
    "POCKET_BATTLE_ITEMS": "Battle Items",
    "POCKET_ITEMS": "Items",
    "POCKET_BERRIES": "Berries",
    "POCKET_MAIL": "Mail",
    "POCKET_KEY_ITEMS": "Key Items",
    "POCKET_TMHMS": "TMs"
}

# --------------------------------------------------

# HELPERS

# --------------------------------------------------

def format_name(item_id):
    return (
        item_id
        .replace("ITEM_", "")
        .replace("_", " ")
        .title()
)

def sprite_name(item_id):
    return (
        item_id
        .replace("ITEM_", "")
        .lower()
        + ".png"
)

def extract_int(text):
    match = re.search(r"-?\d+", text)
    return int(match.group()) if match else 0

# --------------------------------------------------

# DESCRIPTIONS

# --------------------------------------------------

def load_descriptions():

    descriptions = []

    for file in DESCRIPTION_FILES:

        with open(file, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                descriptions.append(
                    line.replace("\\n", " ")
                )

    return descriptions
# --------------------------------------------------

# EFFECT GENERATION

# --------------------------------------------------

def build_effect(item):

    effects = []

    hp_restore = item.get("hp_restore_param", 0)

    if hp_restore > 0:
        effects.append(f"Restores {hp_restore} HP")

    if item.get("revive"):
        effects.append("Revives a fainted Pokémon")

    if item.get("revive_all"):
        effects.append("Revives all fainted Pokémon")

    if item.get("level_up"):
        effects.append("Raises a Pokémon's level by 1")

    if item.get("evolve"):
        effects.append("Causes evolution")

    if item.get("pp_restore"):
        effects.append("Restores PP")

    if item.get("pp_restore_all"):
        effects.append("Restores all PP")

    if item.get("pp_up"):
        effects.append("Raises a move's PP")

    if item.get("pp_max"):
        effects.append("Maximizes a move's PP")

    status = []

    if item.get("slp_heal"):
        status.append("Sleep")

    if item.get("psn_heal"):
        status.append("Poison")

    if item.get("brn_heal"):
        status.append("Burn")

    if item.get("frz_heal"):
        status.append("Freeze")

    if item.get("prz_heal"):
        status.append("Paralysis")

    if item.get("cfs_heal"):
        status.append("Confusion")

    if status:
        effects.append(
            "Cures " + ", ".join(status)
        )

    friendship_penalty = (
        item.get("friendship_mod_lo_param", 0) < 0 or
        item.get("friendship_mod_med_param", 0) < 0 or
        item.get("friendship_mod_hi_param", 0) < 0
    )

    if friendship_penalty:
        effects.append("Lowers friendship")

    return "; ".join(effects) if effects else "No special effect"

# --------------------------------------------------

# PARSE ITEMDATA.C

# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

    items = []

    current = None

    for line in lines:

        stripped = line.strip()

        start = re.match(r"\[(ITEM_[A-Z0-9_]+)\]", stripped)

        if start:

            if current:
                items.append(current)

            item_id = start.group(1)

            current = {
                "id": item_id,
                "name": format_name(item_id),
                "sprite": sprite_name(item_id),

                "price": 0,
                "pocket": "Items",

                "slp_heal": False,
                "psn_heal": False,
                "brn_heal": False,
                "frz_heal": False,
                "prz_heal": False,
                "cfs_heal": False,

                "revive": False,
                "revive_all": False,

                "level_up": False,
                "evolve": False,

                "pp_restore": False,
                "pp_restore_all": False,

                "pp_up": False,
                "pp_max": False,

                "hp_restore_param": 0,

                "friendship_mod_lo_param": 0,
                "friendship_mod_med_param": 0,
                "friendship_mod_hi_param": 0
            }

            continue

        if not current:
            continue

        if "ITEM_PRICE(" in stripped:
            current["price"] = extract_int(stripped)

        elif ".fieldPocket" in stripped:

            for raw, clean in POCKET_MAP.items():

                if raw in stripped:
                    current["pocket"] = clean
                    break

        bool_fields = [
            "slp_heal",
            "psn_heal",
            "brn_heal",
            "frz_heal",
            "prz_heal",
            "cfs_heal",

            "revive",
            "revive_all",

            "level_up",
            "evolve",

            "pp_restore",
            "pp_restore_all",

            "pp_up",
            "pp_max"
        ]

        for field in bool_fields:

            if f".{field}" in stripped:

                current[field] = (
                    "TRUE" in stripped or
                    "= 1" in stripped
                )

        numeric_fields = [
            "hp_restore_param",

            "friendship_mod_lo_param",
            "friendship_mod_med_param",
            "friendship_mod_hi_param"
        ]

        for field in numeric_fields:

            if f".{field}" in stripped:
                current[field] = extract_int(stripped)

    if current:
        items.append(current)

# --------------------------------------------------

# ATTACH DESCRIPTIONS

# --------------------------------------------------

descriptions = load_descriptions()

for i, item in enumerate(items):

    if i < len(descriptions):
        item["description"] = descriptions[i]
    else:
        item["description"] = ""

    item["effect"] = build_effect(item)

# --------------------------------------------------

# REMOVE ITEM_NONE

# --------------------------------------------------

items = [
item
for item in items
if item["id"] != "ITEM_NONE"
]

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

import os

SPRITE_FOLDER = "./website/webimages/items"

clean_items = []

for item in items:

    sprite_path = os.path.join(
        SPRITE_FOLDER,
        item["sprite"]
    )

    # Skip items whose sprite was not exported
    if not os.path.exists(sprite_path):
        continue

    clean_items.append({
        "id": item["id"],
        "name": item["name"],
        "sprite": item["sprite"],
        "pocket": item["pocket"],
        "price": item["price"],
        "description": item["description"],
        "effect": item["effect"]
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(clean_items, f, indent=2)

print(f"Exported {len(clean_items)} items to {OUTPUT_FILE}")
