import re
import json

INPUT_FILE = "./armips/data/moves.s"
OUTPUT_FILE = "./website/webdata/moves.json"

moves = {}

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def extract_int(line):
    match = re.search(r"-?\d+", line)
    return int(match.group()) if match else None


def extract_token(line, prefix):
    parts = line.split()
    if len(parts) < 2:
        return None
    return parts[1].replace(prefix, "")


def clean_flags(line):
    return [
        f.replace("FLAG_", "")
        for f in line.split()
        if f.startswith("FLAG_")
    ]


def clean_generic_prefix(value, prefix):
    if not value:
        return None
    return value.replace(prefix, "")


def format_pss(value):
    if value == "SPLIT_PHYSICAL":
        return "Physical"
    if value == "SPLIT_SPECIAL":
        return "Special"
    return "Status"

# -------------------------------------------------
# TARGET FORMATTING
# -------------------------------------------------

TARGET_MAP = {
    "SINGLE_TARGET": "Single",
    "USER": "User",
    "ADJACENT_OPPONENTS": "Adjacent Opponents",
    "ALL_ADJACENT": "All Adjacent",
    "ALLY": "Ally",
    "FIELD": "Field",
    "OPPONENT_SIDE": "Opponent Side",
    "RANDOM_OPPONENT": "Random Opponent",
    "SINGLE_SPECIAL": "Single Special",
    "USER_SIDE": "User Side"
}


def format_target(raw):
    return TARGET_MAP.get(
        raw,
        raw.replace("_", " ").title()
    )


# -------------------------------------------------
# FLAG FORMATTING
# -------------------------------------------------

FLAG_MAP = {
    "CONTACT": "Contact",
    "PROTECT": "Protect",
    "MAGIC_COAT": "Magic Coat",
    "SNATCH": "Snatch",
    "MIRROR_MOVE": "Mirror Move",
    "KINGS_ROCK": "King's Rock"
}


def clean_flags(line):

    flags = []

    for token in line.split():

        if not token.startswith("FLAG_"):
            continue

        raw = token.replace("FLAG_", "")

        flags.append(
            FLAG_MAP.get(
                raw,
                raw.replace("_", " ").title()
            )
        )

    return flags


# -------------------------------------------------
# NORMALIZATION (NEW UI RULES MOVED HERE)
# -------------------------------------------------

def normalize_move(move):
    """
    Converts raw engine values into UI-ready values.
    """

    # POWER
    if move.get("basepower") == 0:
        move["basepower"] = "-"

    # ACCURACY
    acc = move.get("accuracy")

    if acc == 0:
        if move.get("pss") == "Status":
            move["accuracy"] = "-"
        else:
            move["accuracy"] = "∞"

    elif isinstance(acc, int):
        move["accuracy"] = f"{acc}%"


# -------------------------------------------------
# PARSE FILE
# -------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

current = None

for line in lines:
    line = line.strip()

    if not line:
        continue

    # -------------------------------------------------
    # START MOVE BLOCK
    # -------------------------------------------------
    if line.startswith("movedata"):

        match = re.search(r'movedata\s+(\w+),\s*"(.+?)"', line)

        if match:
            move_id = match.group(1)
            move_name = match.group(2)

            current = {
                "id": move_id,
                "name": move_name,

                "battleeffect": None,
                "pss": None,
                "basepower": None,
                "type": None,
                "accuracy": None,
                "pp": None,
                "effectchance": None,
                "target": None,
                "priority": None,

                "flags": [],
                "appeal": None,
                "contesttype": None,

                "description": None
            }

            moves[move_id] = current
        continue

    # -------------------------------------------------
    # BATTLE EFFECT
    # -------------------------------------------------
    if line.startswith("battleeffect") and current:
        current["battleeffect"] = clean_generic_prefix(
            extract_token(line, "MOVE_EFFECT_"),
            ""
        )

    # -------------------------------------------------
    # PSS CATEGORY
    # -------------------------------------------------
    elif line.startswith("pss") and current:
        current["pss"] = format_pss(extract_token(line, ""))

    # -------------------------------------------------
    # TYPE
    # -------------------------------------------------
    elif line.startswith("type") and current:

        raw = line.split(" ", 1)[1].strip()

        chosen = raw

        if "?" in raw and ":" in raw:
            parts = raw.split("?")
            true_false = parts[1].split(":")

            true_branch = true_false[0].strip()
            false_branch = true_false[1].strip()

            chosen = true_branch if "FAIRY" in true_branch else false_branch

        chosen = chosen.replace("TYPE_", "")
        chosen = chosen.replace("(", "").replace(")", "")

        type_parts = [t.strip() for t in chosen.split(",") if t.strip()]

        formatted_types = []

        for t in type_parts:
            formatted_types.append(t.lower().capitalize())

        current["type"] = formatted_types[0] if len(formatted_types) == 1 else formatted_types

    # -------------------------------------------------
    # TARGET
    # -------------------------------------------------
    elif line.startswith("target") and current:

        raw_target = clean_generic_prefix(
            extract_token(line, "RANGE_"),
            ""
        )

        current["target"] = format_target(raw_target)


    # -------------------------------------------------
    # FLAGS
    # -------------------------------------------------
    elif line.startswith("flags") and current:
        current["flags"] = clean_flags(line)

    # -------------------------------------------------
    # INT FIELDS
    # -------------------------------------------------
    elif line.startswith("basepower") and current:
        current["basepower"] = extract_int(line)

    elif line.startswith("accuracy") and current:
        current["accuracy"] = extract_int(line)

    elif line.startswith("pp") and current:
        current["pp"] = extract_int(line)

    elif line.startswith("effectchance") and current:
        current["effectchance"] = extract_int(line)

    elif line.startswith("priority") and current:
        current["priority"] = extract_int(line)

    # -------------------------------------------------
    # APPEAL
    # -------------------------------------------------
    elif line.startswith("appeal") and current:
        current["appeal"] = clean_generic_prefix(
            extract_token(line, "APPEAL_"),
            ""
        )

    # -------------------------------------------------
    # CONTEST TYPE
    # -------------------------------------------------
    elif line.startswith("contesttype") and current:
        current["contesttype"] = clean_generic_prefix(
            extract_token(line, "CONTEST_"),
            ""
        )

    # -------------------------------------------------
    # DESCRIPTION
    # -------------------------------------------------
    elif line.startswith("movedescription") and current:

        match = re.search(r'movedescription\s+(\w+),\s*"(.*)"', line)

        if match:
            move_id = match.group(1)
            text = match.group(2)

            text = text.replace("\\n", " ")
            text = re.sub(r"\s+", " ", text).strip()

            if move_id in moves:
                moves[move_id]["description"] = text


# -------------------------------------------------
# FINAL NORMALIZATION PASS (IMPORTANT)
# -------------------------------------------------

for move in moves.values():
    normalize_move(move)


# -------------------------------------------------
# EXPORT
# -------------------------------------------------

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(list(moves.values()), f, indent=2)

print(f"Exported {len(moves)} moves to {OUTPUT_FILE}")