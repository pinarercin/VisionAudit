from pathlib import Path

import pandas as pd

from analysis.phash_duplicate_analyzer import (
    PHashDuplicateAnalyzer,
)

class DatasetParser:

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
        ".tif",
        ".tiff",
    }
    
    IMAGE_COLUMN_CANDIDATES = [
        "image_id",
        "image",
        "image_name",
        "filename",
        "file_name",
        "filepath",
        "file_path",
        "img",
        "img_path",
    ]

    LABEL_COLUMN_CANDIDATES = [
        "expression",
        "label",
        "class",
        "class_name",
        "category",
        "target",
        "emotion",
    ]

    VALENCE_COLUMN_CANDIDATES = [
        "valence",
        "val",
    ]

    AROUSAL_COLUMN_CANDIDATES = [
        "arousal",
        "aro",
    ]
    
    
    def __init__(
        self,
        train_image_folder: str,
        train_csv_file: str,
        test_image_folder: str = "",
        test_csv_file: str = "",
        phash_threshold: int = 5,
    ):
        self.train_image_folder = Path(train_image_folder)
        self.train_csv_file = Path(train_csv_file)
        self.phash_threshold = phash_threshold

        self.test_image_folder = (
            Path(test_image_folder) if test_image_folder else None
        )
        self.test_csv_file = (
            Path(test_csv_file) if test_csv_file else None
        )

    def parse(self):
        self._validate_train_inputs()
        self._validate_test_inputs()

        train_df = pd.read_csv(self.train_csv_file)

        train_detected_columns = self._detect_columns(train_df)

        train_statistics = self._calculate_dataset_statistics(
            dataframe=train_df,
            label_column=train_detected_columns["label"],
        )

        train_image_check = self._check_image_consistency(
            dataframe=train_df,
            image_folder=self.train_image_folder,
            image_column=train_detected_columns["image"],
        )

        train_duplicate_analysis = (
            PHashDuplicateAnalyzer().analyze(
                image_folder=self.train_image_folder,
                threshold=self.phash_threshold,
            )
        )

        result = {
            "train": {
                "num_rows": len(train_df),
                "columns": list(train_df.columns),
                "image_folder": str(self.train_image_folder),
                "csv_file": str(self.train_csv_file),
                "detected_columns": train_detected_columns,
                "statistics": train_statistics,
                "image_check": train_image_check,
                "duplicates": train_duplicate_analysis,
                "dataframe": train_df,
            },
            "test": None,
        }

        if self.test_image_folder and self.test_csv_file:
            test_df = pd.read_csv(self.test_csv_file)

            test_detected_columns = self._detect_columns(test_df)

            test_statistics = self._calculate_dataset_statistics(
                dataframe=test_df,
                label_column=test_detected_columns["label"],
            )

            test_image_check = self._check_image_consistency(
                dataframe=test_df,
                image_folder=self.test_image_folder,
                image_column=test_detected_columns["image"],
            )

            result["test"] = {
                "num_rows": len(test_df),
                "columns": list(test_df.columns),
                "image_folder": str(self.test_image_folder),
                "csv_file": str(self.test_csv_file),
                "detected_columns": test_detected_columns,
                "statistics": test_statistics,
                "image_check": test_image_check,
            }

        return result

    def _validate_train_inputs(self):
        if not self.train_image_folder.exists():
            raise FileNotFoundError(
                f"Train image folder not found:\n"
                f"{self.train_image_folder}"
            )

        if not self.train_csv_file.exists():
            raise FileNotFoundError(
                f"Train CSV file not found:\n"
                f"{self.train_csv_file}"
            )

    def _validate_test_inputs(self):
        test_folder_given = self.test_image_folder is not None
        test_csv_given = self.test_csv_file is not None

        if test_folder_given != test_csv_given:
            raise ValueError(
                "Test image folder and test CSV must be selected together."
            )

        if test_folder_given:
            if not self.test_image_folder.exists():
                raise FileNotFoundError(
                    f"Test image folder not found:\n"
                    f"{self.test_image_folder}"
                )

            if not self.test_csv_file.exists():
                raise FileNotFoundError(
                    f"Test CSV file not found:\n"
                    f"{self.test_csv_file}"
                )
            
    def _detect_columns(self, dataframe):
        return {
            "image": self._find_column(
                dataframe,
                self.IMAGE_COLUMN_CANDIDATES,
            ),
            "label": self._find_column(
                dataframe,
                self.LABEL_COLUMN_CANDIDATES,
            ),
            "valence": self._find_column(
                dataframe,
                self.VALENCE_COLUMN_CANDIDATES,
            ),
            "arousal": self._find_column(
                dataframe,
                self.AROUSAL_COLUMN_CANDIDATES,
            ),
        }
    
    def _find_column(self, dataframe, candidates):
        normalized_columns = {
            str(column).strip().lower(): column
            for column in dataframe.columns
        }

        for candidate in candidates:
            if candidate in normalized_columns:
                return normalized_columns[candidate]

        return None
    
    def _collect_image_files(self, image_folder):
        image_files = {}

        for file_path in image_folder.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower()
                in self.SUPPORTED_IMAGE_EXTENSIONS
            ):
                image_files[file_path.name] = file_path

        return image_files
    

    def _check_image_consistency(
        self,
        dataframe,
        image_folder,
        image_column,
    ):
        if image_column is None:
            return {
                "folder_image_count": 0,
                "csv_image_count": 0,
                "missing_images": [],
                "unused_images": [],
                "status": "Image column not detected",
            }

        image_files = self._collect_image_files(image_folder)

        folder_image_names = set(image_files.keys())

        folder_base_names = {
            Path(name).stem: name
            for name in folder_image_names
        }

        csv_image_names = set()

        for value in dataframe[image_column].dropna():
            csv_name = Path(str(value)).name

            if Path(csv_name).suffix:
                csv_image_names.add(csv_name)
            else:
                matched_name = folder_base_names.get(csv_name)

                if matched_name is not None:
                    csv_image_names.add(matched_name)
                else:
                    csv_image_names.add(csv_name)

        missing_images = sorted(
            csv_image_names - folder_image_names
        )

        unused_images = sorted(
            folder_image_names - csv_image_names
        )

        status = (
            "OK"
            if not missing_images and not unused_images
            else "Warning"
        )

        return {
            "folder_image_count": len(folder_image_names),
            "csv_image_count": len(csv_image_names),
            "missing_images": missing_images,
            "unused_images": unused_images,
            "status": status,
        }
    

    def _calculate_dataset_statistics(
        self,
        dataframe,
        label_column,
    ):
        if label_column is None:
            return {
                "num_classes": 0,
                "class_distribution": {},
                "status": "Label column not detected",
            }

        label_counts = (
            dataframe[label_column]
            .dropna()
            .value_counts()
        )

        class_distribution = {
            str(label): int(count)
            for label, count in label_counts.items()
        }

        return {
            "num_classes": len(class_distribution),
            "class_distribution": class_distribution,
            "status": "OK",
        }