import os

from PIL import Image, ImageChops

"""
# Open the images
image1 = Image.open("test-data/acm/IMG_20170417_113034.jpg")
image2 = Image.open("test-data/ACM Photos/IMG_20170417_113034.jpg")
#image2 = Image.open("test-data/ACM Photos/IMG_20170417_113301.jpg")

# Calculate the pixel-by-pixel difference
diff = ImageChops.difference(image1, image2)

# Check if there are any differences
print(diff.getbbox())
if diff.getbbox():
    print("Images are different.")
    # You can save or display the difference image
    diff.save("difference.png")
else:
    print("Images are identical.")
"""

def get_images():
    image_paths = []
    for root, dir, files in os.walk("E:/Pictures"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')):
                image_paths.append(os.path.join(root, file))
    return image_paths

"""
def add_Image_path(similar_images, key, image_paths):
    if (similar_images.)"""

def main():
    similar_images = {}
    image_paths = get_images()
    for i in range(0, len(image_paths)):
        image_list = []
        print(f"Processing {i +1} of {len(image_paths)} : {image_paths[i]}")
        for j in range(i + 1, len(image_paths)):
            image1 = Image.open(image_paths[i])
            image2 = Image.open(image_paths[j])
            diff = ImageChops.difference(image1, image2)

            if not diff.getbbox():
                image_list.append(image_paths[j])
        if len(image_list) > 0:
            similar_images[image_paths[i]] = image_list

    print("\nThe following images are similar:")
    for image_path in similar_images:
        print(f"{image_path} -> {similar_images[image_path]}")

if __name__ == "__main__":
    main()