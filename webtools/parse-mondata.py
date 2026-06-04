import re
import json

INPUT_FILE = "./armips/data/mondata.s"
OUTPUT_FILE = "./website/webdata/pokemon.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

pokemon_list = []
current = None


def build_sprite_key(raw_name: str):
    """
    Converts SPECIES_RAICHU_ALOLAN → raichu_alolan
    Converts SPECIES_BULBASAUR → bulbasaur
    """

    name = raw_name.replace("SPECIES_", "").lower()
    parts = name.split("_")

    base = parts[0]
    form = "_".join(parts[1:]) if len(parts) > 1 else None

    if form:
        return f"{base}_{form}"
    return base


for line in lines:
    line = line.strip()

    # -------------------------
    # START POKEMON BLOCK
    # -------------------------
    if line.startswith("mondata"):
        match = re.search(r'mondata\s+(\w+),\s*"(.+?)"', line)

        if match:
            raw_name = match.group(1)
            display_name = match.group(2)

            current = {
                "id": raw_name,
                "name": display_name,
                "spriteKey": build_sprite_key(raw_name),
                "type": [],
                "ability1": None,
                "ability2": None,
                "hiddenAbility": None
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
        parts = line.replace("types", "").strip().split(",")
        current["type"] = [p.strip() for p in parts if p.strip()]

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
    # END BLOCK
    # -------------------------
    elif line == "" and current and "hp" in current:
        pokemon_list.append(current)
        current = None


# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pokemon_list, f, indent=2)

print(f"Exported {len(pokemon_list)} Pokémon to {OUTPUT_FILE}")