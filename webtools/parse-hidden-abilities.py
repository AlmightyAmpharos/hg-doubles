import re
import json

INPUT_FILE = "./data/HiddenAbilityTable.c"
OUTPUT_FILE = "./website/webdata/hiddenAbilities.json"

hidden_map = {}

pattern = re.compile(
    r"\[\s*(SPECIES_[A-Z0-9_]+)\s*\]\s*=\s*(ABILITY_[A-Z0-9_]+)"
)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.search(line)
        if match:
            species = match.group(1)
            ability = match.group(2)
            hidden_map[species] = ability

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(hidden_map, f, indent=2)

print(f"Exported {len(hidden_map)} hidden abilities")