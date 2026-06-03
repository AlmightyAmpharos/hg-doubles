import re
import json

INPUT_FILE = "./armips/data/mondata.s"
OUTPUT_FILE = "./webdata/pokemon.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

pokemon_list = []
current = None

for line in lines:
    line = line.strip()

    # Start of a Pokémon block
    if line.startswith("mondata"):
        match = re.search(r'mondata\s+(\w+),\s*"(.+?)"', line)
        if match:
            current = {
                "id": match.group(1),
                "name": match.group(2),
                "type": [],
                "ability1": None,
                "ability2": None,
                "hiddenAbility": None
            }

    # Base stats
    elif line.startswith("basestats") and current:
        stats = list(map(int, re.findall(r"\d+", line)))
        current["hp"] = stats[0]
        current["attack"] = stats[1]
        current["defense"] = stats[2]
        current["speed"] = stats[3]
        current["spAttack"] = stats[4]
        current["spDefense"] = stats[5]

    # Types
    elif line.startswith("types") and current:
        parts = line.replace("types", "").strip().split(",")
        current["type"] = [p.strip() for p in parts]

    # Abilities
    elif line.startswith("abilities") and current:
        parts = line.replace("abilities", "").strip().split(",")

        if len(parts) > 0:
            current["ability1"] = parts[0].strip()
        if len(parts) > 1:
            current["ability2"] = parts[1].strip()
        if len(parts) > 2:
            current["hiddenAbility"] = parts[2].strip()

    # End of block detection
    elif line == "" and current and "hp" in current:
        pokemon_list.append(current)
        current = None

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pokemon_list, f, indent=2)

print(f"Exported {len(pokemon_list)} Pokémon to {OUTPUT_FILE}")