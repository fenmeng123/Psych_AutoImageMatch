import os
import cv2
import numpy as np
import csv
import shutil

REFERENCE_DIR = "D:/refernece_images/"
TARGET_DIR = 'D:/merged_images/'
OUTPUT_COUNT = 280
OUTPUT_CSV = 'similarity_results.csv'
SELECTED_DIR = 'D:/selected_images/'


def get_image_features(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)

    (l, a, b) = cv2.split(lab)
    ra = np.mean(a)
    rb = np.mean(b)
    stda = np.std(a)
    stdb = np.std(b)
    colorfulness = (stda + stdb + (ra - rb)) / np.sqrt(l.shape[0] * l.shape[1])

    brightness = np.mean(image)
    contrast = np.std(image)

    return colorfulness, brightness, contrast


def compute_similarity(target_features, ref_features):
    colorfulness_diff = abs(target_features[0] - ref_features[0])
    brightness_diff = abs(target_features[1] - ref_features[1])
    contrast_diff = abs(target_features[2] - ref_features[2])
    weighted_diff = 0.5*colorfulness_diff + 0.25*brightness_diff + 0.25*contrast_diff
    return colorfulness_diff, brightness_diff, contrast_diff, weighted_diff


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ref_features = []
    for ref_image in os.listdir(REFERENCE_DIR):
        ref_path = os.path.join(REFERENCE_DIR, ref_image)
        ref_features.append(get_image_features(ref_path))

    csv_data = []
    for target_image in os.listdir(TARGET_DIR):
        target_path = os.path.join(TARGET_DIR, target_image)
        target_features = get_image_features(target_path)

        total_diffs = [compute_similarity(target_features, r) for r in ref_features]
        avg_colorfulness, avg_brightness, avg_contrast, avg_diff = zip(*total_diffs)
        avg_colorfulness = sum(avg_colorfulness) / len(ref_features)
        avg_brightness = sum(avg_brightness) / len(ref_features)
        avg_contrast = sum(avg_contrast) / len(ref_features)
        avg_diff = sum(avg_diff) / len(ref_features)

        csv_data.append([target_image, avg_colorfulness, avg_brightness, avg_contrast, avg_diff])

    with open(OUTPUT_CSV, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Image Name", "Colorfulness Difference", "Brightness Difference", "Contrast Difference",
                         "Weighted Difference"])
        writer.writerows(csv_data)

    print(f"Similarity results saved to {OUTPUT_CSV}")

    # Select top 240 most similar images
    selected_images = sorted(csv_data, key=lambda x: x[-1])[:OUTPUT_COUNT]

    # Create output directory if not exists
    if not os.path.exists(SELECTED_DIR):
        os.makedirs(SELECTED_DIR)

    # Copy and rename selected images to new directory
    for idx, (image_name, _, _, _, _) in enumerate(selected_images, 1):
        original_path = os.path.join(TARGET_DIR, image_name)
        new_name = f"HealthActivity_{idx}.jpg"
        target_path = os.path.join(SELECTED_DIR, new_name)
        shutil.copy(original_path, target_path)

    print(f"Selected {OUTPUT_COUNT} most similar images and copied to {SELECTED_DIR}")


if __name__ == "__main__":
    main()
