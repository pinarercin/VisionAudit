import csv
from pathlib import Path
from parsers.dataset_parser import DatasetParser
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QGridLayout,
    QApplication,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VisionAudit")
        self.resize(1200, 780)
        self.setMinimumSize(1000, 700)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)

    def _create_left_panel(self):
        panel = QFrame()
        panel.setFixedWidth(340)
        panel.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("VisionAudit")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")

        subtitle = QLabel("Image Classification Dataset Auditor")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #666666;")

        dataset_heading = QLabel("Dataset")
        dataset_heading.setStyleSheet(
            "font-size: 16px; font-weight: 600; margin-top: 10px;"
        )

        train_heading = QLabel("Train Dataset")
        train_heading.setStyleSheet(
            "font-size: 14px; font-weight: 600; margin-top: 4px;"
        )

        self.train_image_folder_input = QLineEdit()
        self.train_image_folder_input.setPlaceholderText(
            "Select train image folder"
        )

        self.train_image_folder_button = QPushButton(
            "Browse Train Image Folder"
        )

        self.train_csv_input = QLineEdit()
        self.train_csv_input.setPlaceholderText("Select train CSV file")

        self.train_csv_button = QPushButton("Browse Train CSV")

        test_heading = QLabel("Test Dataset (Optional)")
        test_heading.setStyleSheet(
            "font-size: 14px; font-weight: 600; margin-top: 8px;"
        )

        self.test_image_folder_input = QLineEdit()
        self.test_image_folder_input.setPlaceholderText(
            "Select test image folder"
        )

        self.test_image_folder_button = QPushButton(
            "Browse Test Image Folder"
        )

        self.test_csv_input = QLineEdit()
        self.test_csv_input.setPlaceholderText("Select test CSV file")

        self.test_csv_button = QPushButton("Browse Test CSV")

        analyses_heading = QLabel("Analyses")
        analyses_heading.setStyleSheet(
            "font-size: 16px; font-weight: 600; margin-top: 10px;"
        )

        self.summary_checkbox = QCheckBox("Dataset Summary")
        self.summary_checkbox.setChecked(True)

        self.duplicate_checkbox = QCheckBox("Duplicate Detection")
        self.duplicate_checkbox.setChecked(True)

        self.phash_threshold_input = QSpinBox()
        self.phash_threshold_input.setRange(0, 20)
        self.phash_threshold_input.setValue(5)
        self.phash_threshold_input.setPrefix("pHash Threshold: ")

        self.leakage_checkbox = QCheckBox("Train-Test Leakage")
        self.leakage_checkbox.setChecked(True)
        self.leakage_checkbox.setEnabled(False)

        self.run_button = QPushButton("Run Analysis")
        self.run_button.setMinimumHeight(42)
        self.run_button.setStyleSheet("font-weight: 600;")

        export_heading = QLabel("Export")
        export_heading.setStyleSheet(
            "font-size: 16px; font-weight: 600; margin-top: 10px;"
        )

        self.export_html_button = QPushButton("Export HTML Report")
        self.export_csv_button = QPushButton("Export CSV Results")

        self.export_html_button.setEnabled(False)
        self.export_csv_button.setEnabled(False)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(dataset_heading)

        layout.addWidget(train_heading)
        layout.addWidget(self.train_image_folder_input)
        layout.addWidget(self.train_image_folder_button)
        layout.addWidget(self.train_csv_input)
        layout.addWidget(self.train_csv_button)

        layout.addWidget(test_heading)
        layout.addWidget(self.test_image_folder_input)
        layout.addWidget(self.test_image_folder_button)
        layout.addWidget(self.test_csv_input)
        layout.addWidget(self.test_csv_button)

        layout.addWidget(analyses_heading)
        layout.addWidget(self.summary_checkbox)
        layout.addWidget(self.duplicate_checkbox)
        layout.addWidget(self.phash_threshold_input)
        layout.addWidget(self.leakage_checkbox)
        layout.addWidget(self.run_button)

        layout.addWidget(export_heading)
        layout.addWidget(self.export_html_button)
        layout.addWidget(self.export_csv_button)

        layout.addStretch()

        return panel

    def _create_right_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        heading = QLabel("Results")
        heading.setStyleSheet("font-size: 22px; font-weight: 700;")

        self.result_tabs = QTabWidget()

        self.summary_tab = self._create_placeholder_tab(
            "Dataset summary will appear here."
        )
        self.duplicates_tab = self._create_placeholder_tab(
            "Duplicate detection results will appear here."
        )
        self.leakage_tab = self._create_placeholder_tab(
            "Train-test leakage results will appear here."
        )
        self.logs_tab = self._create_placeholder_tab(
            "Application logs will appear here."
        )

        self.result_tabs.addTab(self.summary_tab, "Summary")
        self.result_tabs.addTab(self.duplicates_tab, "Duplicates")
        self.result_tabs.addTab(self.leakage_tab, "Leakage")
        self.result_tabs.addTab(self.logs_tab, "Logs")

        layout.addWidget(heading)
        layout.addWidget(self.result_tabs)

        return panel

    def _create_placeholder_tab(self, text):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #777777; font-size: 15px;")

        layout.addWidget(label)

        return tab

    def _connect_signals(self):
        self.train_image_folder_button.clicked.connect(
            self._select_train_image_folder
        )
        self.train_csv_button.clicked.connect(
            self._select_train_csv_file
        )
        self.test_image_folder_button.clicked.connect(
            self._select_test_image_folder
        )
        self.test_csv_button.clicked.connect(
            self._select_test_csv_file
        )

        self.test_image_folder_input.textChanged.connect(
            self._update_leakage_availability
        )
        self.test_csv_input.textChanged.connect(
            self._update_leakage_availability
        )

        self.run_button.clicked.connect(self._run_analysis)

        self.export_csv_button.clicked.connect(
            self._export_csv_results
        )

    def _select_train_image_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Train Image Folder",
        )

        if folder_path:
            self.train_image_folder_input.setText(folder_path)

    def _select_train_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Train CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.train_csv_input.setText(file_path)

    def _select_test_image_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Test Image Folder",
        )

        if folder_path:
            self.test_image_folder_input.setText(folder_path)

    def _select_test_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Test CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.test_csv_input.setText(file_path)

    def _update_leakage_availability(self):
        test_folder_selected = bool(
            self.test_image_folder_input.text().strip()
        )
        test_csv_selected = bool(
            self.test_csv_input.text().strip()
        )

        test_dataset_complete = (
            test_folder_selected and test_csv_selected
        )

        self.leakage_checkbox.setEnabled(test_dataset_complete)

        if not test_dataset_complete:
            self.leakage_checkbox.setChecked(False)
        else:
            self.leakage_checkbox.setChecked(True)

    
    def _run_analysis(self):

        self.run_button.setText("Analyzing...")
        self.run_button.setEnabled(False)
        self.run_button.repaint()

        QApplication.processEvents()

        try:

            parser = DatasetParser(
                train_image_folder=self.train_image_folder_input.text().strip(),
                train_csv_file=self.train_csv_input.text().strip(),
                test_image_folder=self.test_image_folder_input.text().strip(),
                test_csv_file=self.test_csv_input.text().strip(),
                phash_threshold=self.phash_threshold_input.value(),
            )

            try:
                result = parser.parse()
            except Exception as error:
                self._show_summary_text(
                    f"Analysis could not start.\n\n{error}"
                )
                return

            summary_lines = [
                "Dataset Summary",
                "",
                "TRAIN",
                f"Rows: {result['train']['num_rows']}",
                f"Columns: {', '.join(result['train']['columns'])}",
                f"Image folder: {result['train']['image_folder']}",
                f"CSV file: {result['train']['csv_file']}",
                "",
                "Detected Columns",
                f"Image: {result['train']['detected_columns']['image'] or 'Not detected'}",
                f"Label: {result['train']['detected_columns']['label'] or 'Not detected'}",
                f"Valence: {result['train']['detected_columns']['valence'] or 'Not detected'}",
                f"Arousal: {result['train']['detected_columns']['arousal'] or 'Not detected'}",
                "",
                "Image Consistency",
                f"Images in folder: {result['train']['image_check']['folder_image_count']}",
                f"Images referenced in CSV: {result['train']['image_check']['csv_image_count']}",
                f"Missing images: {len(result['train']['image_check']['missing_images'])}",
                f"Unused images: {len(result['train']['image_check']['unused_images'])}",
                f"Status: {result['train']['image_check']['status']}",

                "",
                "Dataset Statistics",
                f"Number of classes: {result['train']['statistics']['num_classes']}",
                "",
                "Class Distribution",

            ]
            
            for label, count in (
                result["train"]["statistics"]["class_distribution"].items()
            ):
                summary_lines.append(f"{label}: {count}")

            if result["test"] is not None:
                summary_lines.extend(
                    [
                        "",
                        "TEST",
                        f"Rows: {result['test']['num_rows']}",
                        f"Columns: {', '.join(result['test']['columns'])}",
                        f"Image folder: {result['test']['image_folder']}",
                        f"CSV file: {result['test']['csv_file']}",
                    ]
                )
            else:
                summary_lines.extend(
                    [
                        "",
                        "TEST",
                        "No test dataset selected.",
                    ]
                )

            self._show_summary_text("\n".join(summary_lines))

            self.train_dataframe = result["train"]["dataframe"]
            self.train_image_column = result["train"][
                "detected_columns"
            ]["image"]

            duplicate_result = result["train"]["duplicates"]

            self._show_duplicate_groups(duplicate_result)

            self.export_csv_button.setEnabled(True)

        finally:

            self.run_button.setEnabled(True)
            self.run_button.setText("Run Analysis")

    def _show_summary_text(self, text):
        layout = self.summary_tab.layout()

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        summary_text = QPlainTextEdit()
        summary_text.setPlainText(text)
        summary_text.setReadOnly(True)
        summary_text.setStyleSheet(
            "font-size: 14px; padding: 12px;"
        )

        layout.addWidget(summary_text)

        self.result_tabs.setCurrentWidget(self.summary_tab)

    def _export_csv_results(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Duplicate Results",
            "duplicate_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        original_columns = list(self.train_dataframe.columns)

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(
                [
                    "group_id",
                    "image_name",
                    *original_columns,
                ]
            )

            for group_id, review in (
                self.duplicate_review_state.items()
            ):
                if not review["checkbox"].isChecked():
                    continue

                for image_path in review["group"]:
                    image_stem = image_path.stem

                    matched_rows = self.train_dataframe[
                        self.train_dataframe[
                            self.train_image_column
                        ]
                        .astype(str)
                        .apply(
                            lambda value: Path(value).stem
                        )
                        == image_stem
                    ]

                    if matched_rows.empty:
                        writer.writerow(
                            [
                                group_id,
                                image_path.name,
                                *([""] * len(original_columns)),
                            ]
                        )
                        continue

                    row = matched_rows.iloc[0]

                    writer.writerow(
                        [
                            group_id,
                            image_path.name,
                            *[
                                row[column]
                                for column in original_columns
                            ],
                        ]
                    )

    def _show_duplicate_groups(self, duplicate_result):
        layout = self.duplicates_tab.layout()
        self.duplicate_review_state = {}

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(18)

        summary_label = QLabel(
            "Duplicate Detection\n\n"
            f"Images analyzed: {duplicate_result['image_count']}\n"
            f"Threshold: {duplicate_result['threshold']}\n"
            f"Duplicate groups: "
            f"{duplicate_result['duplicate_group_count']}\n"
            f"Duplicate pairs: "
            f"{duplicate_result['duplicate_pair_count']}"
        )
        summary_label.setStyleSheet(
            "font-size: 14px; padding: 8px;"
        )

        container_layout.addWidget(summary_label)

        for group_index, group in enumerate(
            duplicate_result["duplicate_groups"],
            start=1,
        ):
            group_frame = QFrame()
            group_frame.setFrameShape(QFrame.Shape.StyledPanel)

            group_layout = QVBoxLayout(group_frame)
            group_layout.setSpacing(10)

            group_title = QLabel(
                f"Group {group_index} ({len(group)} images)"
            )
            group_title.setStyleSheet(
                "font-size: 15px; font-weight: 600;"
            )

            duplicate_checkbox = QCheckBox(
                "Include as duplicate"
            )
            duplicate_checkbox.setChecked(True)

            self.duplicate_review_state[group_index] = {
                "group": group,
                "checkbox": duplicate_checkbox,
            }

            thumbnail_grid = QGridLayout()
            thumbnail_grid.setSpacing(14)

            for image_index, image_path in enumerate(group):
                image_widget = QWidget()
                image_layout = QVBoxLayout(image_widget)
                image_layout.setContentsMargins(0, 0, 0, 0)

                thumbnail_label = QLabel()
                thumbnail_label.setFixedSize(150, 150)
                thumbnail_label.setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                thumbnail_label.setStyleSheet(
                    "border: 1px solid #999999;"
                )

                pixmap = QPixmap(str(image_path))

                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        140,
                        140,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    thumbnail_label.setPixmap(scaled_pixmap)
                else:
                    thumbnail_label.setText(
                        "Image could not be loaded"
                    )

                filename_label = QLabel(image_path.name)
                filename_label.setAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )
                filename_label.setWordWrap(True)
                filename_label.setMaximumWidth(150)

                image_layout.addWidget(thumbnail_label)
                image_layout.addWidget(filename_label)

                row = image_index // 4
                column = image_index % 4

                thumbnail_grid.addWidget(
                    image_widget,
                    row,
                    column,
                )

            group_layout.addWidget(group_title)
            group_layout.addWidget(duplicate_checkbox)
            group_layout.addLayout(thumbnail_grid)

            container_layout.addWidget(group_frame)

        container_layout.addStretch()

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

        self.result_tabs.setCurrentWidget(
            self.duplicates_tab
        )