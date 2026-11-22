import csv
import pandas as pd
from pathlib import Path
from parsers.dataset_parser import DatasetParser
from PIL import Image
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
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
    QToolButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QGridLayout,
    QApplication,
)

class ClassDistributionChart(QWidget):
    def __init__(
        self,
        distribution,
        parent=None,
        bar_color="#4F81BD",
        horizontal=False,
    ):
        super().__init__(parent)

        self.distribution = distribution
        self.bar_color = bar_color
        self.horizontal = horizontal
        self.setMinimumHeight(180)

    def paintEvent(self, event):
        super().paintEvent(event)

        if not self.distribution:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        labels = list(self.distribution.keys())
        counts = list(self.distribution.values())

        max_count = max(counts)

        if self.horizontal:
            left_margin = 80
            right_margin = 70
            top_margin = 20
            bar_height = 45
            bar_spacing = 25

            available_width = (
                self.width() - left_margin - right_margin
            )

            for index, (label, count) in enumerate(
                zip(labels, counts)
            ):
                width = (
                    count / max_count
                ) * available_width

                y = top_margin + index * (
                    bar_height + bar_spacing
                )

                painter.fillRect(
                    left_margin,
                    int(y),
                    int(width),
                    bar_height,
                    QColor(self.bar_color),
                )

                painter.drawText(
                    0,
                    int(y),
                    left_margin - 10,
                    bar_height,
                    Qt.AlignRight | Qt.AlignVCenter,
                    str(label),
                )

                painter.drawText(
                    left_margin + int(width) + 10,
                    int(y),
                    60,
                    bar_height,
                    Qt.AlignLeft | Qt.AlignVCenter,
                    str(count),
                )

            painter.end()
            return

        left_margin = 50
        right_margin = 60
        top_margin = 20
        bottom_margin = 50

        chart_width = self.width() - left_margin - right_margin
        chart_height = self.height() - top_margin - bottom_margin

        bar_spacing = 8
        bar_width = (
            chart_width - bar_spacing * (len(labels) - 1)
        ) / len(labels)

        for index, (label, count) in enumerate(
            zip(labels, counts)
        ):
            bar_height = (
                count / max_count
            ) * chart_height

            x = left_margin + index * (
                bar_width + bar_spacing
            )
            y = top_margin + chart_height - bar_height

            painter.fillRect(
                int(x),
                int(y),
                int(bar_width),
                int(bar_height),
                QColor(self.bar_color),
            )

            painter.drawText(
                int(x),
                int(top_margin + chart_height + 8),
                int(bar_width),
                25,
                Qt.AlignCenter,
                str(label),
            )

            painter.drawText(
                int(x),
                int(y - 22),
                int(bar_width),
                20,
                Qt.AlignCenter,
                str(count),
            )

        painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VisionAudit")
        self.resize(1200, 780)
        self.setMinimumSize(1000, 700)

        self.settings = QSettings(
            "VisionAudit",
            "VisionAudit",
        )

        self._build_ui()
        self._load_saved_paths()
        self._connect_signals()

    def _load_saved_paths(self):
        self.train_image_folder_input.setText(
            self.settings.value("train_image_folder", "")
        )
        self.train_csv_input.setText(
            self.settings.value("train_csv_file", "")
        )
        self.test_image_folder_input.setText(
            self.settings.value("test_image_folder", "")
        )
        self.test_csv_input.setText(
            self.settings.value("test_csv_file", "")
        )

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
        self.export_train_csv_button = QPushButton(
            "Export Train Duplicates CSV"
        )
        self.export_test_csv_button = QPushButton(
            "Export Test Duplicates CSV"
        )

        self.export_leakage_csv_button = QPushButton(
            "Export Leakage CSV"
        )

        self.export_html_button.setEnabled(False)
        self.export_train_csv_button.setEnabled(False)
        self.export_test_csv_button.setEnabled(False)
        self.export_leakage_csv_button.setEnabled(False)

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
        layout.addWidget(self.export_train_csv_button)
        layout.addWidget(self.export_test_csv_button)
        layout.addWidget(self.export_leakage_csv_button)

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

        self.summary_tab = QWidget()

        summary_layout = QVBoxLayout(self.summary_tab)

        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)

        self.summary_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.summary_content = QWidget()
        self.summary_content_layout = QVBoxLayout(
            self.summary_content
        )

        self.summary_placeholder = QLabel(
            "Dataset summary will appear here."
        )
        self.summary_placeholder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.summary_placeholder.setStyleSheet(
            "color: #777777; font-size: 15px;"
        )

        self.summary_content_layout.addWidget(
            self.summary_placeholder
        )

        self.summary_scroll.setWidget(
            self.summary_content
        )

        summary_layout.addWidget(
            self.summary_scroll
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

        self.export_train_csv_button.clicked.connect(
            self._export_train_csv_results
        )

        self.export_test_csv_button.clicked.connect(
            self._export_test_csv_results
        )

        self.export_leakage_csv_button.clicked.connect(
            self._export_leakage_csv_results
        )

        self.export_html_button.clicked.connect(
            self._export_html_report
        )

    def _select_train_image_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Train Image Folder",
        )

        if folder_path:
            self.train_image_folder_input.setText(folder_path)
            self.settings.setValue(
                "train_image_folder",
                folder_path,
            )

    def _select_train_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Train CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.train_csv_input.setText(file_path)
            self.settings.setValue(
                "train_csv_file",
                file_path,
            )

    def _select_test_image_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Test Image Folder",
        )

        if folder_path:
            self.test_image_folder_input.setText(folder_path)
            self.settings.setValue(
                "test_image_folder",
                folder_path,
            )

    def _select_test_csv_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Test CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )

        if file_path:
            self.test_csv_input.setText(file_path)
            self.settings.setValue(
                "test_csv_file",
                file_path,
            )

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

    def _update_analysis_status(self, message):
        self.run_button.setText(message)
        self.run_button.repaint()
        QApplication.processEvents()
    
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
                status_callback=self._update_analysis_status,
            )

            try:
                result = parser.parse()
            except Exception as error:
                self._show_summary_text(
                    f"Analysis could not start.\n\n{error}"
                )
                return
            
            self.analysis_result = result

            test_image_count = (
                result["test"]["num_rows"]
                if result["test"] is not None
                else 0
            )

            test_duplicate_group_count = (
                result["test"]["duplicates"]["duplicate_group_count"]
                if result["test"] is not None
                else 0
            )

            leakage_group_count = (
                result["leakage"]["leakage_group_count"]
                if result["leakage"] is not None
                else 0
            )

            summary_lines = [
                "Dataset Audit Overview",
                "",
                f"Train images: {result['train']['num_rows']}",
                f"Test images: {test_image_count}",
                f"Train duplicate groups: "
                f"{result['train']['duplicates']['duplicate_group_count']}",
                f"Test duplicate groups: {test_duplicate_group_count}",
                f"Train-test leakage groups: {leakage_group_count}",
                "",
                "----------------------------------------",
                "",
                "Dataset Details",
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
                f"Class imbalance ratio: "
                f"{result['train']['statistics']['imbalance_ratio']:.2f}",
                f"Class balance: "
                f"{result['train']['statistics']['imbalance_status']}"
                + (
                    " — highly imbalanced class distribution"
                    if result["train"]["statistics"]["imbalance_status"]
                    == "Warning"
                    else ""
                ),
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
                        "",
                        "Detected Columns",
                        f"Image: {result['test']['detected_columns']['image'] or 'Not detected'}",
                        f"Label: {result['test']['detected_columns']['label'] or 'Not detected'}",
                        f"Valence: {result['test']['detected_columns']['valence'] or 'Not detected'}",
                        f"Arousal: {result['test']['detected_columns']['arousal'] or 'Not detected'}",
                        "",
                        "Image Consistency",
                        f"Images in folder: {result['test']['image_check']['folder_image_count']}",
                        f"Images referenced in CSV: {result['test']['image_check']['csv_image_count']}",
                        f"Missing images: {len(result['test']['image_check']['missing_images'])}",
                        f"Unused images: {len(result['test']['image_check']['unused_images'])}",
                        f"Status: {result['test']['image_check']['status']}",
                        "",
                        "Dataset Statistics",
                        f"Number of classes: {result['test']['statistics']['num_classes']}",
                        f"Class imbalance ratio: "
                        f"{result['test']['statistics']['imbalance_ratio']:.2f}",
                        f"Class balance: "
                        f"{result['test']['statistics']['imbalance_status']}"
                        + (
                            " — highly imbalanced class distribution"
                            if result["test"]["statistics"]["imbalance_status"]
                            == "Warning"
                            else ""
                        ),
                        "",
                        "Class Distribution",
                    ]
                )

                for label, count in (
                    result["test"]["statistics"]["class_distribution"].items()
                ):
                    summary_lines.append(f"{label}: {count}")

            else:
                summary_lines.extend(
                    [
                        "",
                        "TEST",
                        "No test dataset selected.",
                    ]
                )

            self._show_summary_text("\n".join(summary_lines))

            train_distribution = (
                result["train"]["statistics"]["class_distribution"]
            )

            train_chart_title = QLabel(
                "Train Class Distribution"
            )
            train_chart_title.setStyleSheet(
                "font-size: 16px; font-weight: bold;"
            )

            train_chart = ClassDistributionChart(
                train_distribution
            )

            self.summary_content_layout.addWidget(
                train_chart_title
            )
            self.summary_content_layout.addWidget(
                train_chart
            )

            if result["test"] is not None:
                test_distribution = (
                    result["test"]["statistics"]["class_distribution"]
                )

                test_chart_title = QLabel(
                    "Test Class Distribution"
                )
                test_chart_title.setStyleSheet(
                    "font-size: 16px; font-weight: bold;"
                )

                test_chart = ClassDistributionChart(
                    test_distribution
                )

                self.summary_content_layout.addWidget(
                    test_chart_title
                )
                self.summary_content_layout.addWidget(
                    test_chart
                )

            if result["test"] is not None:
                dataset_size_title = QLabel(
                    "Train vs Test Dataset Size"
                )
                dataset_size_title.setStyleSheet(
                    "font-size: 16px; font-weight: bold;"
                )

                dataset_size_distribution = {
                    "Train": result["train"]["num_rows"],
                    "Test": result["test"]["num_rows"],
                }

                dataset_size_chart = ClassDistributionChart(
                    dataset_size_distribution,
                    bar_color="#C8A2E8",
                    horizontal=True,
                )

                self.summary_content_layout.addWidget(
                    dataset_size_title
                )
                self.summary_content_layout.addWidget(
                    dataset_size_chart
                )

            self.train_dataframe = result["train"]["dataframe"]
            self.train_image_column = result["train"][
                "detected_columns"
            ]["image"]

            if result["test"] is not None:
                self.test_dataframe = result["test"]["dataframe"]
                self.test_image_column = result["test"][
                    "detected_columns"
                ]["image"]

            train_duplicate_result = result["train"]["duplicates"]

            test_duplicate_result = None

            if result["test"] is not None:
                test_duplicate_result = result["test"]["duplicates"]

            self._show_duplicate_groups(
                train_duplicate_result,
                test_duplicate_result,
            )

            if result["leakage"] is not None:
                self._show_leakage_groups(
                    result["leakage"]
                )

            self.export_html_button.setEnabled(True)

            self.export_train_csv_button.setEnabled(True)

            self.export_test_csv_button.setEnabled(
                result["test"] is not None
            )
    
            self.export_leakage_csv_button.setEnabled(
                result["leakage"] is not None
            )

        finally:

            self.run_button.setEnabled(True)
            self.run_button.setText("Run Analysis")

    def _show_summary_text(self, text):
        layout = self.summary_content_layout

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

        summary_text.setMinimumHeight(520)

        layout.addWidget(summary_text)

        self.result_tabs.setCurrentWidget(self.summary_tab)

    def _format_csv_value(self, value):
        if pd.isna(value):
            return ""

        if isinstance(value, float) and value.is_integer():
            return int(value)

        return value

    def _export_html_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export HTML Report",
            "visionaudit_report.html",
            "HTML Files (*.html)",
        )

        if not file_path:
            return

        result = self.analysis_result

        test_details_html = ""

        test_distribution_html = ""

        test_imbalance_html = ""

        test_duplicate_summary_html = ""

        leakage_summary_html = ""

        if result["leakage"] is not None:
            confirmed_leakage = sum(
                1
                for review in self.leakage_review_state.values()
                if review["checkbox"].isChecked()
            )

            leakage_summary_html = f"""
    <hr>

    <h3>Train–Test Leakage Summary</h3>

    <p>
        Detected leakage groups:
        {result["leakage"]["leakage_group_count"]}
    </p>

    <p>
        Included leakage groups after review:
        {confirmed_leakage}
    </p>
"""

        if result["test"] is not None:
            test_details_html = f"""
    <hr>

    <h3>Test Dataset Details</h3>

    <p>Rows: {result["test"]["num_rows"]}</p>

    <p>
        Detected image column:
        {result["test"]["detected_columns"]["image"] or "Not detected"}
    </p>

    <p>
        Detected label column:
        {result["test"]["detected_columns"]["label"] or "Not detected"}
    </p>

    <p>
        Images in folder:
        {result["test"]["image_check"]["folder_image_count"]}
    </p>

    <p>
        Images referenced in CSV:
        {result["test"]["image_check"]["csv_image_count"]}
    </p>

    <p>
        Missing images:
        {len(result["test"]["image_check"]["missing_images"])}
    </p>

    <p>
        Unused images:
        {len(result["test"]["image_check"]["unused_images"])}
    </p>

    <p>
        Image consistency status:
        {result["test"]["image_check"]["status"]}
    </p>

    <p>
        Number of classes:
        {result["test"]["statistics"]["num_classes"]}
    </p>
"""
    
            test_distribution = result["test"][
                "statistics"
            ]["class_distribution"]

            test_distribution_rows = ""

            for label, count in test_distribution.items():
                test_distribution_rows += (
                    f"<tr>"
                    f"<td>{label}</td>"
                    f"<td>{count}</td>"
                    f"</tr>"
                )

            test_distribution_html = f"""
    <hr>

    <h3>Test Class Distribution</h3>

    <table>
        <thead>
            <tr>
                <th>Class</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            {test_distribution_rows}
        </tbody>
    </table>
"""
            
            test_statistics = result["test"]["statistics"]

            test_imbalance_ratio = test_statistics["imbalance_ratio"]

            test_imbalance_text = (
                f"{test_imbalance_ratio:.2f}"
                if test_imbalance_ratio is not None
                else "Not applicable"
            )

            test_imbalance_status = test_statistics["imbalance_status"]

            test_imbalance_html = f"""
    <hr>

    <h3>Test Class Imbalance</h3>

    <p>Imbalance ratio: {test_imbalance_text}</p>
    <p>Class balance: {test_imbalance_status}</p>
"""
            
            test_confirmed_duplicates = sum(
                1
                for review in self.duplicate_review_state["test"].values()
                if review["checkbox"].isChecked()
            )

            test_duplicate_summary_html = f"""
    <hr>

    <h3>Test Duplicate Summary</h3>

    <p>
        Detected duplicate groups:
        {result["test"]["duplicates"]["duplicate_group_count"]}
    </p>

    <p>
        Included duplicate groups after review:
        {test_confirmed_duplicates}
    </p>
"""
            
        train_distribution = result["train"][
            "statistics"
        ]["class_distribution"]

        train_distribution_rows = ""

        for label, count in train_distribution.items():
            train_distribution_rows += (
                f"<tr>"
                f"<td>{label}</td>"
                f"<td>{count}</td>"
                f"</tr>"
            )

        train_distribution_html = f"""
    <hr>

    <h3>Train Class Distribution</h3>

    <table>
        <thead>
            <tr>
                <th>Class</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            {train_distribution_rows}
        </tbody>
    </table>
"""

        train_statistics = result["train"]["statistics"]

        train_imbalance_ratio = train_statistics["imbalance_ratio"]

        train_imbalance_text = (
            f"{train_imbalance_ratio:.2f}"
            if train_imbalance_ratio is not None
            else "Not applicable"
        )

        train_imbalance_status = train_statistics["imbalance_status"]

        train_imbalance_html = f"""
    <hr>

    <h3>Train Class Imbalance</h3>

    <p>Imbalance ratio: {train_imbalance_text}</p>
    <p>Class balance: {train_imbalance_status}</p>
"""

        train_confirmed_duplicates = sum(
            1
            for review in self.duplicate_review_state["train"].values()
            if review["checkbox"].isChecked()
        )

        train_duplicate_summary_html = f"""
    <hr>

    <h3>Train Duplicate Summary</h3>

    <p>
        Detected duplicate groups:
        {result["train"]["duplicates"]["duplicate_group_count"]}
    </p>

    <p>
        Included duplicate groups after review:
        {train_confirmed_duplicates}
    </p>
"""

        train_image_count = result["train"]["num_rows"]

        test_image_count = (
            result["test"]["num_rows"]
            if result["test"] is not None
            else 0
        )

        train_duplicate_count = result["train"][
            "duplicates"
        ]["duplicate_group_count"]

        test_duplicate_count = (
            result["test"]["duplicates"]["duplicate_group_count"]
            if result["test"] is not None
            else 0
        )

        leakage_count = (
            result["leakage"]["leakage_group_count"]
            if result["leakage"] is not None
            else 0
        )

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VisionAudit Dataset Audit Report</title>

    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background-color: #f5f7fb;
            color: #253047;
            line-height: 1.6;
            max-width: 960px;
            margin: 40px auto;
            padding: 32px;
        }}

        h1 {{
            color: #263b70;
            font-size: 30px;
            margin-bottom: 8px;
        }}

        h2, h3 {{
            color: #344b80;
            margin-top: 28px;
            margin-bottom: 12px;
        }}

        p {{
            margin: 8px 0;
        }}

        hr {{
            border: none;
            border-top: 1px solid #dce2ec;
            margin: 28px 0;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: #ffffff;
            margin-top: 12px;
            margin-bottom: 24px;
        }}

        th, td {{
            padding: 11px 14px;
            text-align: left;
            border-bottom: 1px solid #e5e9f0;
        }}

        th {{
            background-color: #e9eef9;
            color: #263b70;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #f8faff;
        }}
    </style>

</head>
<body>
    <h1>VisionAudit</h1>
    <h2>Dataset Audit Report</h2>

    <h3>Dataset Audit Overview</h3>

    <p>Train images: {train_image_count}</p>
    <p>Test images: {test_image_count}</p>
    <p>Train duplicate groups: {train_duplicate_count}</p>
    <p>Test duplicate groups: {test_duplicate_count}</p>
    <p>Train-test leakage groups: {leakage_count}</p>

    <hr>

    <h3>Train Dataset Details</h3>

    <p>Rows: {result["train"]["num_rows"]}</p>

    <p>
        Detected image column:
        {result["train"]["detected_columns"]["image"] or "Not detected"}
    </p>

    <p>
        Detected label column:
        {result["train"]["detected_columns"]["label"] or "Not detected"}
    </p>

    <p>
        Images in folder:
        {result["train"]["image_check"]["folder_image_count"]}
    </p>

    <p>
        Images referenced in CSV:
        {result["train"]["image_check"]["csv_image_count"]}
    </p>

    <p>
        Missing images:
        {len(result["train"]["image_check"]["missing_images"])}
    </p>

    <p>
        Unused images:
        {len(result["train"]["image_check"]["unused_images"])}
    </p>

    <p>
        Image consistency status:
        {result["train"]["image_check"]["status"]}
    </p>

    <p>
        Number of classes:
        {result["train"]["statistics"]["num_classes"]}
    </p>

    {test_details_html}

    {train_distribution_html}

    {test_distribution_html}

    {train_imbalance_html}

    {test_imbalance_html}

    {train_duplicate_summary_html}

    {test_duplicate_summary_html}

    {leakage_summary_html}

</body>
</html>
"""

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as html_file:
            html_file.write(html_content)


    def _export_train_csv_results(self):
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
                self.duplicate_review_state["train"].items()
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
                                self._format_csv_value(row[column])
                                for column in original_columns
                            ],
                        ]
                    )

    def _export_test_csv_results(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Test Duplicate Results",
            "test_duplicate_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        original_columns = list(self.test_dataframe.columns)

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
                self.duplicate_review_state["test"].items()
            ):
                if not review["checkbox"].isChecked():
                    continue

                for image_path in review["group"]:
                    image_stem = image_path.stem

                    matched_rows = self.test_dataframe[
                        self.test_dataframe[
                            self.test_image_column
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
                                self._format_csv_value(row[column])
                                for column in original_columns
                            ],
                        ]
                    )

    def _export_leakage_csv_results(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Leakage Results",
            "leakage_results.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        train_columns = list(self.train_dataframe.columns)
        test_columns = list(self.test_dataframe.columns)

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
                    "train_image_name",
                    "test_image_name",
                    *[
                        f"train_{column}"
                        for column in train_columns
                    ],
                    *[
                        f"test_{column}"
                        for column in test_columns
                    ],
                ]
            )

            for group_id, review in (
                self.leakage_review_state.items()
            ):
                if not review["checkbox"].isChecked():
                    continue

                group = review["group"]

                for train_image_path in group["train"]:
                    train_stem = train_image_path.stem

                    train_matches = self.train_dataframe[
                        self.train_dataframe[
                            self.train_image_column
                        ]
                        .astype(str)
                        .apply(
                            lambda value: Path(value).stem
                        )
                        == train_stem
                    ]

                    train_values = (
                        train_matches.iloc[0]
                        if not train_matches.empty
                        else None
                    )

                    for test_image_path in group["test"]:
                        test_stem = test_image_path.stem

                        test_matches = self.test_dataframe[
                            self.test_dataframe[
                                self.test_image_column
                            ]
                            .astype(str)
                            .apply(
                                lambda value: Path(value).stem
                            )
                            == test_stem
                        ]

                        test_values = (
                            test_matches.iloc[0]
                            if not test_matches.empty
                            else None
                        )

                        writer.writerow(
                            [
                                group_id,
                                train_image_path.name,
                                test_image_path.name,
                                *[
                                    (
                                        self._format_csv_value(
                                            train_values[column]
                                        )
                                        if train_values is not None
                                        else ""
                                    )
                                    for column in train_columns
                                ],
                                *[
                                    (
                                        self._format_csv_value(
                                            test_values[column]
                                        )
                                        if test_values is not None
                                        else ""
                                    )
                                    for column in test_columns
                                ],
                            ]
                        )

    def _add_duplicate_group_widgets(
        self,
        container_layout,
        duplicate_result,
        dataset_name,
    ):
        for group_index, group in enumerate(
            duplicate_result["duplicate_groups"],
            start=1,
        ):
            group_frame = QFrame()
            group_frame.setFrameShape(
                QFrame.Shape.StyledPanel
            )

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

            self.duplicate_review_state[dataset_name][
                group_index
            ] = {
                "group": group,
                "checkbox": duplicate_checkbox,
            }

            thumbnail_grid = QGridLayout()
            thumbnail_grid.setSpacing(14)

            for image_index, image_path in enumerate(group):
                image_widget = QWidget()
                image_layout = QVBoxLayout(image_widget)
                image_layout.setContentsMargins(
                    0,
                    0,
                    0,
                    0,
                )

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
                    thumbnail_label.setPixmap(
                        scaled_pixmap
                    )
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

    def _show_duplicate_groups(
        self,
        train_duplicate_result,
        test_duplicate_result=None,
    ):
        layout = self.duplicates_tab.layout()

        self.duplicate_review_state = {
            "train": {},
            "test": {},
        }

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
            "TRAIN DUPLICATES\n\n"
            f"Images analyzed: "
            f"{train_duplicate_result['image_count']}\n"
            f"Threshold: "
            f"{train_duplicate_result['threshold']}\n"
            f"Duplicate groups: "
            f"{train_duplicate_result['duplicate_group_count']}\n"
            f"Duplicate pairs: "
            f"{train_duplicate_result['duplicate_pair_count']}"
        )
        summary_label.setStyleSheet(
            "font-size: 14px; padding: 8px;"
        )

        container_layout.addWidget(summary_label)

        self._add_duplicate_group_widgets(
            container_layout=container_layout,
            duplicate_result=train_duplicate_result,
            dataset_name="train",
        )

        if test_duplicate_result is not None:
            test_summary_label = QLabel(
                "TEST DUPLICATES\n\n"
                f"Images analyzed: "
                f"{test_duplicate_result['image_count']}\n"
                f"Threshold: "
                f"{test_duplicate_result['threshold']}\n"
                f"Duplicate groups: "
                f"{test_duplicate_result['duplicate_group_count']}\n"
                f"Duplicate pairs: "
                f"{test_duplicate_result['duplicate_pair_count']}"
            )
            test_summary_label.setStyleSheet(
                "font-size: 14px; padding: 8px; margin-top: 20px;"
            )

            container_layout.addWidget(test_summary_label)

            self._add_duplicate_group_widgets(
                container_layout=container_layout,
                duplicate_result=test_duplicate_result,
                dataset_name="test",
            )

        container_layout.addStretch()

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)

        self.result_tabs.setCurrentWidget(
            self.duplicates_tab
        )

    def _show_leakage_groups(self, leakage_result):
        layout = self.leakage_tab.layout()

        self.leakage_review_state = {}

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
            "TRAIN ↔ TEST LEAKAGE\n\n"
            f"Train images analyzed: "
            f"{leakage_result['train_image_count']}\n"
            f"Test images analyzed: "
            f"{leakage_result['test_image_count']}\n"
            f"Threshold: "
            f"{leakage_result['threshold']}\n"
            f"Leakage groups: "
            f"{leakage_result['leakage_group_count']}\n"
            f"Leakage pairs: "
            f"{leakage_result['leakage_pair_count']}"
        )
        summary_label.setStyleSheet(
            "font-size: 14px; padding: 8px;"
        )

        container_layout.addWidget(summary_label)

        for group_index, group in enumerate(
            leakage_result["leakage_groups"],
            start=1,
        ):
            group_frame = QFrame()
            group_frame.setFrameShape(
                QFrame.Shape.StyledPanel
            )

            group_layout = QVBoxLayout(group_frame)
            group_layout.setSpacing(10)

            group_title = QLabel(
                f"Leakage Group {group_index}"
            )
            group_title.setStyleSheet(
                "font-size: 15px; font-weight: 600;"
            )

            leakage_checkbox = QCheckBox(
                "Include as leakage"
            )
            leakage_checkbox.setChecked(True)

            self.leakage_review_state[group_index] = {
                "group": group,
                "checkbox": leakage_checkbox,
            }

            group_layout.addWidget(group_title)
            group_layout.addWidget(leakage_checkbox)

            for dataset_name in ("train", "test"):
                dataset_label = QLabel(
                    dataset_name.upper()
                )
                dataset_label.setStyleSheet(
                    "font-weight: 600;"
                )
                group_layout.addWidget(dataset_label)

                thumbnail_grid = QGridLayout()
                thumbnail_grid.setSpacing(14)

                for image_index, image_path in enumerate(
                    group[dataset_name]
                ):
                    image_widget = QWidget()
                    image_layout = QVBoxLayout(image_widget)
                    image_layout.setContentsMargins(
                        0,
                        0,
                        0,
                        0,
                    )

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
                        thumbnail_label.setPixmap(
                            scaled_pixmap
                        )
                    else:
                        thumbnail_label.setText(
                            "Image could not be loaded"
                        )

                    filename_label = QLabel(
                        image_path.name
                    )
                    filename_label.setAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )
                    filename_label.setWordWrap(True)
                    filename_label.setMaximumWidth(150)

                    image_layout.addWidget(
                        thumbnail_label
                    )
                    image_layout.addWidget(
                        filename_label
                    )

                    row = image_index // 4
                    column = image_index % 4

                    thumbnail_grid.addWidget(
                        image_widget,
                        row,
                        column,
                    )

                group_layout.addLayout(thumbnail_grid)

            container_layout.addWidget(group_frame)

        container_layout.addStretch()

        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)