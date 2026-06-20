import re
import json

ENCOUNTERS_FILE = "./armips/data/encounters.s"
HEADBUTT_FILE = "./armips/data/headbutt.s"

OUTPUT_FILE = "./website/webdata/encounters.json"

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

WALK_RATES = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]

ROCK_SMASH_RATES = [90, 10]

ROD_RATES = [40, 40, 15, 4, 1]

HEADBUTT_SLOT_RATES = [50, 15, 15, 10, 5, 5]

def aggregate_headbutt(slots):
    species_map = {}
    for i, slot in enumerate(slots):
        species = slot["species"]
        if species == "NONE":
            continue
        
        rate = HEADBUTT_SLOT_RATES[i] # Uses the 6-slot rates array correctly now
        
        if species not in species_map:
            species_map[species] = {
                "species": species,
                "rate": 0,
                "level": slot["level"]
            }
        species_map[species]["rate"] += rate
    return list(species_map.values())


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def normalize_name(name):
    name = name.lower()

    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace(",", "")

    name = " ".join(name.split())

    return name


def clean_species(species):
    return species.replace("SPECIES_", "")


def add_species_rates(slots, rates):
    result = {}

    for species, rate, level in zip(slots, rates, slots_levels(slots)):
        if species == "NONE":
            continue

        if species not in result:
            result[species] = {
                "species": species,
                "rate": 0,
                "level": level
            }

        result[species]["rate"] += rate

    return list(result.values())


def collapse_encounters(entries):
    result = {}

    for entry in entries:

        species = entry["species"]

        if species == "NONE":
            continue

        if species not in result:
            result[species] = {
                "species": species,
                "rate": 0,
                "level": entry["level"]
            }

        result[species]["rate"] += entry["rate"]

    return sorted(
        result.values(),
        key=lambda x: (-x["rate"], x["species"])
    )


def slots_levels(slot_list):
    return [x["level"] for x in slot_list]


# --------------------------------------------------
# LOCATION STORAGE
# --------------------------------------------------

locations = {}

def get_location(name):

    key = normalize_name(name)

    if key not in locations:

        locations[key] = {
            "name": name,

            "walk_rate": 0,
            "rock_smash_rate": 0,
            "old_rod_rate": 0,
            "good_rod_rate": 0,
            "super_rod_rate": 0,

            "walk_day": [],
            "walk_night": [],

            "hoenn_radio": [],
            "sinnoh_radio": [],

            "rock_smash": [],

            "old_rod": [],
            "good_rod": [],
            "super_rod": [],

            "swarms": {},

            "headbutt": []
        }

    return locations[key]

# --------------------------------------------------
# PARSE ENCOUNTERS.S
# --------------------------------------------------

with open(ENCOUNTERS_FILE, "r", encoding="latin-1") as f:
    text = f.read()

blocks = re.findall(
    r"encounterdata\s+\d+\s+//\s*(.*?)\n(.*?)\.close",
    text,
    re.S
)

for name, block in blocks:

    location = get_location(name.strip())

    def get_rate(label):

        match = re.search(
            rf"{label}\s+(\d+)",
            block
        )

        return int(match.group(1)) if match else 0

    location["walk_rate"] = get_rate("walkrate")
    location["rock_smash_rate"] = get_rate("rocksmashrate")
    location["old_rod_rate"] = get_rate("oldrodrate")
    location["good_rod_rate"] = get_rate("goodrodrate")
    location["super_rod_rate"] = get_rate("superrodrate")

    walk_levels_match = re.search(
        r"walklevels\s+([^\n]+)",
        block
    )

    walk_levels = [0] * 12

    if walk_levels_match:

        walk_levels = [
            int(x.strip())
            for x in walk_levels_match.group(1).split(",")
        ]

    # -------------------------
    # WALK ENCOUNTERS
    # -------------------------

    pokemon_lines = re.findall(
        r"pokemon\s+SPECIES_([A-Z0-9_]+)",
        block
    )

    if len(pokemon_lines) >= 40:

        day_slots = pokemon_lines[12:24]
        night_slots = pokemon_lines[24:36]

        day_entries = []

        for species, rate, level in zip(
            day_slots,
            WALK_RATES,
            walk_levels
        ):
            day_entries.append({
                "species": species,
                "rate": rate,
                "level": level
            })

        night_entries = []

        for species, rate, level in zip(
            night_slots,
            WALK_RATES,
            walk_levels
        ):
            night_entries.append({
                "species": species,
                "rate": rate,
                "level": level
            })

        location["walk_day"] = collapse_encounters(day_entries)
        location["walk_night"] = collapse_encounters(night_entries)

        location["hoenn_radio"] = [
            clean_species(pokemon_lines[36]),
            clean_species(pokemon_lines[37])
        ]

        location["sinnoh_radio"] = [
            clean_species(pokemon_lines[38]),
            clean_species(pokemon_lines[39])
        ]

    # -------------------------
    # SPECIAL ENCOUNTERS
    # -------------------------

    encounter_lines = re.findall(
        r"encounter\s+SPECIES_([A-Z0-9_]+),\s*(\d+),\s*(\d+)",
        block
    )

    def parse_section(start, count, rates):

        section = []

        for i in range(count):

            species, level, _ = encounter_lines[start + i]

            section.append({
                "species": clean_species(species),
                "rate": rates[i],
                "level": int(level)
            })

        return collapse_encounters(section)

    if len(encounter_lines) >= 22:

        location["rock_smash"] = parse_section(
            5,
            2,
            ROCK_SMASH_RATES
        )

        location["old_rod"] = parse_section(
            7,
            5,
            ROD_RATES
        )

        location["good_rod"] = parse_section(
            12,
            5,
            ROD_RATES
        )

        location["super_rod"] = parse_section(
            17,
            5,
            ROD_RATES
        )

    # -------------------------
    # SWARMS
    # -------------------------

    if len(pokemon_lines) >= 44:

        location["swarms"] = {
            "grass": clean_species(pokemon_lines[40]),
            "surf": clean_species(pokemon_lines[41]),
            "good_rod": clean_species(pokemon_lines[42]),
            "super_rod": clean_species(pokemon_lines[43])
        }

# --------------------------------------------------
# PARSE HEADBUTT.S
# --------------------------------------------------

with open(HEADBUTT_FILE, "r", encoding="latin-1") as f:
    text = f.read()

blocks = re.findall(
    r"headbuttheader.*?//\s*(.*?)\n(.*?)\.close", text, re.S
)

for name, block in blocks:
    location = get_location(name.strip())
    encounters = re.findall(
        r"headbuttencounter\s+SPECIES_([A-Z0-9_]+),\s*(\d+),\s*(\d+)", block
    )
    
    if len(encounters) < 12:
        continue
    
    # 1. Create the normal_slots array with raw data (without pre-baked rates)
    normal_slots = []
    for i in range(12):
        species, level, _ = encounters[i]
        normal_slots.append({
            "species": clean_species(species),
            "level": int(level)
        })
    
    # 2. Split and aggregate using your new instruction logic
    group_a_slots = normal_slots[:6]
    group_b_slots = normal_slots[6:12]

    group_a = aggregate_headbutt(group_a_slots)
    group_b = aggregate_headbutt(group_b_slots)

    location["headbutt"] = {
        "group_a": group_a,
        "group_b": group_b
    }


# --------------------------------------------------
# REMOVE EMPTY LOCATIONS
# --------------------------------------------------

clean_locations = []

for location in locations.values():

    has_data = any([
        location["walk_day"],
        location["walk_night"],
        location["rock_smash"],
        location["old_rod"],
        location["good_rod"],
        location["super_rod"],
        location["headbutt"]
    ])

    if has_data:
        clean_locations.append(location)

clean_locations.sort(
    key=lambda x: x["name"]
)

# --------------------------------------------------
# EXPORT
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        clean_locations,
        f,
        indent=2
    )

print(
    f"Exported {len(clean_locations)} locations to {OUTPUT_FILE}"
)