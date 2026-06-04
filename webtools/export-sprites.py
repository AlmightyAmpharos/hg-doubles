from pathlib import Path
from PIL import Image, UnidentifiedImageError

SOURCE = Path("data/graphics/sprites")
DEST = Path("website/webimages/sprites")

DEST.mkdir(parents=True, exist_ok=True)


def build_sprite_key(path: Path):
    """
    Converts sprite path → consistent filename key

    Examples:
    - bulbasaur/male/front.png → bulbasaur.png
    - jynx/female/front.png → jynx_female.png
    """

    pokemon = path.parent.parent.name.lower()
    gender = path.parent.name.lower()

    if gender == "female":
        return f"{pokemon}_female"

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