import json

POKEMON_FILE = "./webdata/pokemon.json"
HIDDEN_FILE = "./webdata/hiddenAbilities.json"
OUTPUT_FILE = "./webdata/pokemon.json"  # overwrite final output

# Load data
with open(POKEMON_FILE, "r", encoding="utf-8") as f:
    pokemon_list = json.load(f)

with open(HIDDEN_FILE, "r", encoding="utf-8") as f:
    hidden_map = json.load(f)

# Merge
for mon in pokemon_list:
    species_id = mon["id"]

    if species_id in hidden_map:
        mon["hiddenAbility"] = hidden_map[species_id]
    else:
        mon["hiddenAbility"] = "ABILITY_NONE"

# Save back
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(pokemon_list, f, indent=2)

print(f"Merged hidden abilities into {len(pokemon_list)} Pokémon")