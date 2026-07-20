import sys

from PySide6.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)

label = QLabel("VisionAudit")
label.resize(500, 300)
label.show()

sys.exit(app.exec())