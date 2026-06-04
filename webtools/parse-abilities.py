import re
import json

INPUT_ABILITIES = "./asm/include/abilities.inc"
INPUT_TEXT = "./data/text/722.txt"
INPUT_POKEMON = "./website/webdata/pokemon.json"
OUTPUT_FILE = "./website/webdata/abilities.json"

abilities = {}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def extract_int(line):
    match = re.search(r"-?\d+", line)
    return int(match.group()) if match else None


def clean_token(line):
    parts = line.split(",")[0].strip()
    parts = parts.replace(".equ", "").strip()
    parts = parts.replace("ABILITY_", "")
    return parts


# -------------------------------------------------
# LOAD ABILITY DESCRIPTIONS (722.txt FIXED)
# -------------------------------------------------

def load_descriptions():
    with open("data/text/722.txt", "r", encoding="utf-8") as f:
        raw_lines = [line.strip() for line in f if line.strip() != ""]

    cleaned = []
    for line in raw_lines:
        line = line.replace("\\n", " ")   # real newline escapes in file
        line = line.replace("\\\\", " ")  # literal "\" used in script text
        line = " ".join(line.split())     # normalize whitespace
        cleaned.append(line)

    return cleaned


descriptions = load_descriptions()

# -------------------------------------------------
# PARSE ABILITIES (abilities.inc)
# -------------------------------------------------

with open(INPUT_ABILITIES, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()

    if not line.startswith(".equ ABILITY_"):
        continue

    match = re.match(r"\.equ\s+ABILITY_(\w+),\s*(\d+)", line)

    if not match:
        continue

    name = match.group(1)
    ability_id = int(match.group(2))

    abilities[ability_id] = {
        "id": ability_id,
        "name": name.replace("_", " ").title(),
        "description": "",
        "pokemon": []
    }


# -------------------------------------------------
# ASSIGN DESCRIPTIONS (FIXED ALIGNMENT)
# -------------------------------------------------

for ability_id, ability in abilities.items():

    if ability_id < len(descriptions):
        ability["description"] = descriptions[ability_id]
    else:
        ability["description"] = ""

# -------------------------------------------------
# LOAD POKEMON & CROSS-REFERENCE ABILITIES
# -------------------------------------------------

with open(INPUT_POKEMON, "r", encoding="utf-8") as f:
    pokemon_data = json.load(f)


for mon in pokemon_data:

    for field in ["ability1", "ability2", "hiddenAbility"]:

        ability_key = mon.get(field)

        if not ability_key:
            continue

        ability_key = ability_key.replace("ABILITY_", "")

        for ability in abilities.values():
            if ability["name"].replace(" ", "_").upper() == ability_key:
                abilities[ability["id"]]["pokemon"].append(mon["name"])


# -------------------------------------------------
# FINAL CLEANUP
# -------------------------------------------------

# remove duplicates in pokemon lists
for ability in abilities.values():
    ability["pokemon"] = sorted(list(set(ability["pokemon"])))


# -------------------------------------------------
# EXPORT
# -------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(list(abilities.values()), f, indent=2)

print(f"Exported {len(abilities)} abilities to {OUTPUT_FILE}")