import os
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import imagehash
import shutil

def organize_desktop(n_clusters=5):
    # Define the desktop path and retrieve the file list.
    desktop = os.path.expanduser('~\\Desktop')
    all_files = os.listdir(desktop)

    image_files = []
    features = []

    # Process files: Build a list of image files and their feature vectors
    for file in all_files:
        full_path = os.path.join(desktop, file)
        # Skip directories
        if os.path.isdir(full_path):
            continue
        # Check for image file extension (case-insensitive)
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                with Image.open(full_path) as img:
                    # Compute average hash
                    img_hash = imagehash.average_hash(img)
                    # Convert hash to numpy vector (flattened array of bits)
                    vector = np.array(img_hash.hash, dtype=np.uint8).flatten()
                    features.append(vector)
                    image_files.append(file)
            except Exception as e:
                print(f"Error processing {file}: {e}")
        else:
            # Move non-image file to "Other" folder
            other_folder = os.path.join(desktop, "Other")
            os.makedirs(other_folder, exist_ok=True)
            try:
                shutil.move(full_path, os.path.join(other_folder, file))
                print(f"Moved non-image file {file} to Other folder")
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # If no images were found, exit.
    if not image_files:
        print("No image files found on Desktop.")
        return

    # Convert features to a numpy array
    X = np.array(features)

    # Cluster image feature vectors using KMeans
    print("Clustering images...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    # Create cluster folders and move images accordingly.
    for file, label in zip(image_files, labels):
        src = os.path.join(desktop, file)
        group_folder = os.path.join(desktop, f"Group {label}")
        os.makedirs(group_folder, exist_ok=True)
        try:
            shutil.move(src, os.path.join(group_folder, file))
            print(f"Moved {file} to {group_folder}")
        except Exception as e:
            print(f"Error moving {file}: {e}")

if __name__ == "__main__":
    organize_desktop(n_clusters=5)
