from pathlib import Path

import imagehash
from PIL import Image


class PHashLeakageAnalyzer:

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff",
    }

    def calculate_hash(self, image_path):
        with Image.open(image_path) as image:
            return imagehash.phash(image)

    def calculate_folder_hashes(self, image_folder):
        image_folder = Path(image_folder)

        image_hashes = {}

        for image_path in image_folder.iterdir():
            if (
                image_path.is_file()
                and image_path.suffix.lower()
                in self.SUPPORTED_IMAGE_EXTENSIONS
            ):
                try:
                    image_hashes[image_path] = self.calculate_hash(
                        image_path
                    )
                except Exception:
                    continue

        return image_hashes

    def find_leakage_pairs(
        self,
        train_hashes,
        test_hashes,
        threshold,
    ):
        leakage_pairs = []

        for train_path, train_hash in train_hashes.items():
            for test_path, test_hash in test_hashes.items():
                distance = train_hash - test_hash

                if distance <= threshold:
                    leakage_pairs.append(
                        {
                            "train": train_path,
                            "test": test_path,
                            "distance": distance,
                        }
                    )

        return leakage_pairs

    def build_leakage_groups(self, leakage_pairs):
        adjacency = {}

        for pair in leakage_pairs:
            train_node = ("train", pair["train"])
            test_node = ("test", pair["test"])

            adjacency.setdefault(train_node, set()).add(test_node)
            adjacency.setdefault(test_node, set()).add(train_node)

        visited = set()
        leakage_groups = []

        for start_node in adjacency:
            if start_node in visited:
                continue

            stack = [start_node]
            visited.add(start_node)

            train_images = []
            test_images = []

            while stack:
                dataset_name, image_path = stack.pop()

                if dataset_name == "train":
                    train_images.append(image_path)
                else:
                    test_images.append(image_path)

                for neighbor in adjacency.get(
                    (dataset_name, image_path),
                    set(),
                ):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)

            leakage_groups.append(
                {
                    "train": sorted(
                        train_images,
                        key=lambda path: path.name,
                    ),
                    "test": sorted(
                        test_images,
                        key=lambda path: path.name,
                    ),
                }
            )

        return leakage_groups

    def analyze(
        self,
        train_image_folder,
        test_image_folder,
        threshold=5,
    ):
        train_hashes = self.calculate_folder_hashes(
            train_image_folder
        )
        test_hashes = self.calculate_folder_hashes(
            test_image_folder
        )

        leakage_pairs = self.find_leakage_pairs(
            train_hashes=train_hashes,
            test_hashes=test_hashes,
            threshold=threshold,
        )

        leakage_groups = self.build_leakage_groups(
            leakage_pairs
        )

        return {
            "train_image_count": len(train_hashes),
            "test_image_count": len(test_hashes),
            "threshold": threshold,
            "leakage_pair_count": len(leakage_pairs),
            "leakage_group_count": len(leakage_groups),
            "leakage_pairs": leakage_pairs,
            "leakage_groups": leakage_groups,
        }