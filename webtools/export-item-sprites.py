import os
import shutil
import hashlib

# -------------------------------------------------
# PATHS
# -------------------------------------------------

SPRITE_SOURCE = "./data/graphics/item"
TM_SOURCE = "./data/graphics/item/base"

SPRITE_DEST = "./website/webimages/items"

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


# -------------------------------------------------
# SETUP
# -------------------------------------------------

os.makedirs(SPRITE_DEST, exist_ok=True)

# -------------------------------------------------
# FIND PLACEHOLDER SPRITE
# -------------------------------------------------

PLACEHOLDER_HASH = file_hash(
    "./data/graphics/item/aur1577.png"
)

# -------------------------------------------------
# COPY NORMAL ITEM SPRITES
# -------------------------------------------------

copied = 0
skipped = 0

for filename in os.listdir(SPRITE_SOURCE):

    if not filename.endswith(".png"):
        continue

    src = os.path.join(SPRITE_SOURCE, filename)

    if os.path.isdir(src):
        continue

    sprite_hash = file_hash(src)

    if sprite_hash == PLACEHOLDER_HASH:
        skipped += 1
        continue

    dst = os.path.join(SPRITE_DEST, filename)

    shutil.copy2(src, dst)
    copied += 1

# -------------------------------------------------
# COPY TM/HM/TR TYPE ICONS
# -------------------------------------------------

tm_icons = 0

if os.path.exists(TM_SOURCE):

    for filename in os.listdir(TM_SOURCE):

        if not filename.endswith(".png"):
            continue

        src = os.path.join(TM_SOURCE, filename)
        dst = os.path.join(SPRITE_DEST, filename)

        shutil.copy2(src, dst)
        tm_icons += 1

# -------------------------------------------------
# FINISHED
# -------------------------------------------------

print()
print(f"Copied item sprites: {copied}")
print(f"Skipped placeholders: {skipped}")
print(f"Copied TM type icons: {tm_icons}")
print(f"Output folder: {SPRITE_DEST}")