import re
import json

INPUT_FILE = "./armips/data/mondata.s"
OUTPUT_FILE = "./website/webdata/pokemon.json"

SPRITE_KEY_OVERRIDES = {
    "SPECIES_MIMEJR": "mime_jr"
}


def build_display_name(species_id, raw_name):
    if raw_name != "-----":
        return raw_name

    parts = species_id.replace("SPECIES_", "").split("_")
    return " ".join(word.capitalize() for word in parts)


def clean_dex_entry(text):
    if not text:
        return ""

    return (
        text
        .replace("\\n", " ")   # game line breaks → space
        .replace("\n", " ")
        .strip()
    )


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

pokemon_list = []
current = None

for line in lines:
    line = line.strip()

    # -------------------------
    # START POKEMON
    # -------------------------
    if line.startswith("mondata"):
        match = re.search(r'mondata\s+(\w+),\s*"(.+?)"', line)

        if match:
            species_id = match.group(1)
            raw_name = match.group(2)

            display_name = build_display_name(species_id, raw_name)

            sprite_key = SPRITE_KEY_OVERRIDES.get(
                species_id,
                species_id.replace("SPECIES_", "").lower()
            )

            current = {
                "id": species_id,
                "name": display_name,
                "spriteKey": sprite_key,
                "type": [],
                "ability1": None,
                "ability2": None,
                "hiddenAbility": None,
                "genderRatio": None,
                "dexEntry": ""
            }

    # -------------------------
    # BASE STATS
    # -------------------------
    elif line.startswith("basestats") and current:
        stats = list(map(int, re.findall(r"\d+", line)))

        current["hp"] = stats[0]
        current["attack"] = stats[1]
        current["defense"] = stats[2]
        current["speed"] = stats[3]
        current["spAttack"] = stats[4]
        current["spDefense"] = stats[5]

    # -------------------------
    # TYPES
    # -------------------------
    elif line.startswith("types") and current:

        # Extract ALL TYPE_* tokens anywhere in the line
        matches = re.findall(r"TYPE_[A-Z]+", line)

        # Remove duplicates while preserving order
        seen = set()
        cleaned = []
        for t in matches:
            if t not in seen:
                seen.add(t)
                cleaned.append(t)

        current["type"] = cleaned

    # -------------------------
    # ABILITIES
    # -------------------------
    elif line.startswith("abilities") and current:
        parts = line.replace("abilities", "").strip().split(",")

        if len(parts) > 0:
            current["ability1"] = parts[0].strip()
        if len(parts) > 1:
            current["ability2"] = parts[1].strip()
        if len(parts) > 2:
            current["hiddenAbility"] = parts[2].strip()

    # -------------------------
    # GENDER RATIO
    # -------------------------
    elif line.startswith("genderratio") and current:
        value = re.findall(r"\d+", line)
        if value:
            current["genderRatio"] = int(value[0])

    # -------------------------
    # DEX ENTRY
    # -------------------------
    elif line.startswith("mondexentry") and current:
        match = re.search(r'mondexentry\s+\w+,\s*"(.+?)"', line)

        if match:
            raw_text = match.group(1)
            current["dexEntry"] = clean_dex_entry(raw_text)

    # -------------------------
    # END POKEMON BLOCK
    # -------------------------
    elif line == "" and current and "hp" in current:
        pokemon_list.append(current)
        current = None

# catch last entry
if current and "hp" in current:
    pokemon_list.append(current)

# -------------------------
# SAVE
# -------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pokemon_list, f, indent=2)

print(f"Exported {len(pokemon_list)} Pokémon to {OUTPUT_FILE}")