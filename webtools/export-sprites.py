from pathlib import Path
from PIL import Image, UnidentifiedImageError

SOURCE = Path("data/graphics/sprites")
DEST = Path("website/webimages/sprites")

DEST.mkdir(parents=True, exist_ok=True)


def build_sprite_key(path: Path):
    """
    Converts sprite path → consistent filename key

    Examples:
    - pikachu/male/front.png → pikachu.png
    - raichu/alolan/male/front.png → raichu_alolan.png
    - meowstic/female/front.png → meowstic_female.png
    """

    parts = path.parts

    # Find key folders more safely (no fragile indexing)
    pokemon = parts[-4].lower()
    form = parts[-3].lower()
    gender = parts[-2].lower()

    # Case 1: no special form folder (just male/female)
    if form in ["male", "female"]:
        if gender == "female":
            return f"{pokemon}_female"
        return pokemon

    # Case 2: form exists (alolan, mega, regional, etc.)
    if form not in ["male", "female"]:
        if gender == "female":
            return f"{pokemon}_{form}_female"
        return f"{pokemon}_{form}"

    return pokemon


count = 0
skipped = 0

for front_sprite in SOURCE.rglob("front.png"):

    # Only valid sprite folders
    if "male" not in front_sprite.parts and "female" not in front_sprite.parts:
        continue

    try:
        img = Image.open(front_sprite)
        img.load()

        # crop first frame (80x80 left side)
        first_frame = img.crop((0, 0, 80, 80))

        sprite_key = build_sprite_key(front_sprite)
        output_file = DEST / f"{sprite_key}.png"

        first_frame.save(output_file)

        print(f"Exported {sprite_key}")
        count += 1

    except (UnidentifiedImageError, OSError):
        print(f"SKIPPED: {front_sprite}")
        skipped += 1

print(f"\nDONE. Exported: {count}, Skipped: {skipped}")