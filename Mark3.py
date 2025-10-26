import os
import csv
import json
import imagehash
from PIL import Image
from tqdm import tqdm
from collections import defaultdict
from multiprocessing import Pool, cpu_count

# --- CONFIGURATION ---
IMAGE_DIR = "E:/Pictures"
#IMAGE_DIR = "test-data"
HASH_FUNC = imagehash.phash  # options: average_hash, phash, dhash, whash
HASH_SIZE = 16               # 8 or 16 is common
HAMMING_TOLERANCE = 0        # 0 = exact, 1–3 for near-duplicates
#N_PROCESSES = max(1, cpu_count() - 1)
N_PROCESSES = 20
HASH_CACHE_FILE = "image_hashes.json"
#DUPLICATES_CSV_FILE = "duplicates.csv"
DUPLICATES_FILE = "duplicates.json"

# --- FUNCTION TO COMPUTE HASH ---
def compute_hash(image_path):
    try:
        with Image.open(image_path) as img:
            img_hash = HASH_FUNC(img, hash_size=HASH_SIZE)
            #print (img_hash)
        return (image_path, str(img_hash))
    except Exception:
        return (image_path, None)

def load_cached_hashes():
    if os.path.exists(HASH_CACHE_FILE):
        with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cached_hashes(cache):
    with open(HASH_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def main():
    # Gather all images
    valid_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp', '.heic'}
    image_paths = [
        os.path.join(dp, f)
        for dp, _, files in os.walk(IMAGE_DIR)
        for f in files
        if os.path.splitext(f.lower())[1] in valid_exts
    ]

    print(f"Found {len(image_paths)} image files. Checking for cached hashes...")
    #print(f"Found {len(image_paths)} images. Computing hashes using {N_PROCESSES} cores...")

    # Step 2. Load previously cached hashes
    cached_hashes = load_cached_hashes()

    # Only process new/unseen images
    new_images = [p for p in image_paths if p not in cached_hashes]
    print(f"{len(new_images)} new images to hash, using {N_PROCESSES} cores...")

    # Step 3. Compute hashes in parallel for new images
    if new_images:
        with Pool(processes=N_PROCESSES) as pool:
            new_results = list(tqdm(pool.imap_unordered(compute_hash, new_images), total=len(new_images)))
        for path, h in new_results:
            if h:
                cached_hashes[path] = h

        # Save updated cache
        save_cached_hashes(cached_hashes)

    # Parallel hash computation
    #with Pool(processes=N_PROCESSES) as pool:
        #results = list(tqdm(pool.imap_unordered(compute_hash, image_paths), total=len(image_paths)))

    # Group by hash
    hash_dict = defaultdict(list)
    for path, h in cached_hashes.items():
        if h:
            hash_dict[h].append(path)

    # Detect exact duplicates
    duplicates = {h: paths for h, paths in hash_dict.items() if len(paths) > 1}

    """
    # --- Output results ---
    print("\nDuplicate groups found:")
    for h, paths in duplicates.items():
        print(f"\nHash: {h}")
        for p in paths:
            print("   ", p)

    print(f"\nTotal duplicate groups: {len(duplicates)}")
    """

    # Step 6. Save duplicates report to CSV
    if duplicates:

        #with open(DUPLICATES_CSV_FILE, "w", newline='', encoding="utf-8") as csvfile:
            #writer = csv.writer(csvfile)
            #writer.writerow(["Group_Hash", "File_Path"])
            #for h, paths in duplicates.items():
                #for p in paths:
                    #writer.writerow([h, p])
        with open(DUPLICATES_FILE, "w", encoding="utf-8") as f:
            json.dump(duplicates, f, indent=2)

        print(f"\nDuplicate report saved to: {DUPLICATES_FILE}")
    else:
        print("\nNo duplicates found.")


if __name__ == "__main__":
    main()