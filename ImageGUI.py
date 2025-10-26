import os
import sys
from PIL import Image
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QPushButton, QMessageBox,
    QCheckBox, QLabel)


class ImagePanel(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.deleted = False

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.checkbox = QCheckBox("Select")
        self.layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.update_display()

    def update_display(self):
        if not os.path.exists(self.image_path):
            self.image_label.setText("❌ Image deleted")
            self.info_label.setText("")
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.width() > 300:
            pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

        try:
            with Image.open(self.image_path) as img:
                size = img.size  # (width, height)
                dpi = img.info.get("dpi", ("N/A", "N/A"))
                image_file_size = os.path.getsize(self.image_path) / (1024 * 1024)

        except Exception as e:
            size, dpi, image_file_size = ("Error", "Error", "Error")

        info_text = (
            f"File Size: {image_file_size:.2f} MB\n"
            f"Size: {size[0]}x{size[1]} px\n"
            f"DPI: {dpi[0]}x{dpi[1]}\n"
            f"Path: {self.image_path}"
        )
        self.info_label.setText(info_text)

    def is_selected(self):
        return self.checkbox.isChecked()

    def delete_image(self):
        if os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
                self.deleted = True
                self.update_display()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete {self.image_path}\n{e}")


class MainWindow(QMainWindow):
    def __init__(self, image_paths):
        super().__init__()
        self.setWindowTitle("Image Manager")
        self.image_paths = image_paths

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Scrollable area for image panels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.hbox = QHBoxLayout(scroll_content)
        scroll_content.setLayout(self.hbox)
        scroll.setWidget(scroll_content)
        self.layout.addWidget(scroll)

        self.panels = []
        for path in self.image_paths:
            panel = ImagePanel(path)
            self.hbox.addWidget(panel)
            self.panels.append(panel)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.layout.addWidget(self.delete_button)

    def delete_selected(self):
        selected_panels = [p for p in self.panels if p.is_selected()]
        if not selected_panels:
            QMessageBox.information(self, "Info", "No images selected.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected_panels)} selected image(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            for panel in selected_panels:
                panel.delete_image()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    image_files = [
        "E:/Pictures/AEM Jammu Team Outing 22112018/IMG_20181122_124838.jpg",
        "E:/Pictures/phone pics/Phone Photos 21122019/Camera/IMG_20181122_124838.jpg",
        "E:/Pictures/Phone Pics V9 part 1/IMG_20181122_124838.jpg"
    ]

    window = MainWindow(image_files)
    window.resize(1200, 600)
    window.show()
    sys.exit(app.exec())