from pathlib import Path

import imagehash
from PIL import Image


class PHashDuplicateAnalyzer:

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
        image_path = Path(image_path)

        with Image.open(image_path) as image:
            return imagehash.phash(image)
        
    def calculate_folder_hashes(self, image_folder):
        image_folder = Path(image_folder)

        hashes = {}

        for image_path in image_folder.iterdir():
            if (
                image_path.suffix.lower()
                not in self.SUPPORTED_IMAGE_EXTENSIONS
            ):
                continue

            hashes[image_path] = self.calculate_hash(image_path)

        return hashes
    
    def calculate_hamming_distance(
        self,
        hash1,
        hash2,
    ):
        return hash1 - hash2
    
    def find_duplicate_pairs(
        self,
        hashes,
        threshold=5,
    ):
        image_paths = list(hashes.keys())
        duplicate_pairs = []

        for first_index in range(len(image_paths)):
            for second_index in range(
                first_index + 1,
                len(image_paths),
            ):
                first_path = image_paths[first_index]
                second_path = image_paths[second_index]

                distance = self.calculate_hamming_distance(
                    hashes[first_path],
                    hashes[second_path],
                )

                if distance <= threshold:
                    duplicate_pairs.append(
                        {
                            "image_1": first_path,
                            "image_2": second_path,
                            "hamming_distance": distance,
                        }
                    )

        return duplicate_pairs
    
    def build_duplicate_groups(self, duplicate_pairs):
        adjacency = {}

        for pair in duplicate_pairs:
            first_path = pair["image_1"]
            second_path = pair["image_2"]

            adjacency.setdefault(first_path, set()).add(second_path)
            adjacency.setdefault(second_path, set()).add(first_path)

        visited = set()
        duplicate_groups = []

        for image_path in adjacency:
            if image_path in visited:
                continue

            stack = [image_path]
            group = []

            while stack:
                current_path = stack.pop()

                if current_path in visited:
                    continue

                visited.add(current_path)
                group.append(current_path)

                stack.extend(
                    adjacency.get(current_path, set()) - visited
                )

            if len(group) > 1:
                duplicate_groups.append(
                    sorted(group, key=lambda path: path.name)
                )

        return duplicate_groups
    
    def analyze(
        self,
        image_folder,
        threshold=5,
    ):
        hashes = self.calculate_folder_hashes(image_folder)

        duplicate_pairs = self.find_duplicate_pairs(
            hashes=hashes,
            threshold=threshold,
        )

        duplicate_groups = self.build_duplicate_groups(
            duplicate_pairs
        )

        return {
            "image_count": len(hashes),
            "threshold": threshold,
            "duplicate_pair_count": len(duplicate_pairs),
            "duplicate_group_count": len(duplicate_groups),
            "duplicate_groups": duplicate_groups,
            "duplicate_pairs": duplicate_pairs,
        }