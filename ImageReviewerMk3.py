import sys
import os
import json
from collections import OrderedDict
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QCheckBox, QPushButton, QScrollArea, QMessageBox, QMainWindow
)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QFont
from PyQt6.QtCore import Qt
from PIL import Image


def format_file_size(bytes_size):
    """Convert bytes to a human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


class ImagePanel(QWidget):
    """Widget showing one image, info, and selection checkbox."""
    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
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

        # Enable mouse interaction on the whole panel
        self.setMouseTracking(True)
        self.image_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Give a small border for visibility
        self.setStyleSheet("""
            QWidget {
                border: 2px solid transparent;
                border-radius: 8px;
            }
        """)

        """
            QWidget {
                border: 2px solid transparent;
                border-radius: 8px;
            }
            QWidget:hover {
                border: 2px solid #0078d7;
            }
        """

        self.update_display()

    def update_display(self):
        """Refresh the image and its metadata."""
        if not os.path.exists(self.image_path):
            self.image_label.setText("❌ Image deleted")
            self.info_label.setText("")
            return

        pixmap = QPixmap(self.image_path)
        if pixmap.width() > 800:
            pixmap = pixmap.scaledToWidth(800, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

        try:
            file_size = os.path.getsize(self.image_path)
            readable_size = format_file_size(file_size)
        except Exception:
            readable_size = "Unknown"

        try:
            from PIL import Image
            with Image.open(self.image_path) as img:
                size = img.size
                dpi = img.info.get("dpi", ("N/A", "N/A"))
        except Exception:
            size, dpi = ("Error", "Error")

        info_text = (
            f"Size: {size[0]}x{size[1]} px\n"
            f"DPI: {dpi[0]}x{dpi[1]}\n"
            f"File Size: {readable_size}\n"
            f"Path: {self.image_path}"
        )
        self.info_label.setText(info_text)
        font = QFont()
        font.setPointSize(14)
        self.info_label.setFont(font)

    def is_selected(self):
        return self.checkbox.isChecked()

    def delete_image(self):
        if os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
                self.update_display()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete {self.image_path}\n{e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            new_state = not self.checkbox.isChecked()
            self.checkbox.setChecked(new_state)
            if new_state:
                self.setStyleSheet("QWidget { border: 2px solid #00cc66; border-radius: 8px; }")
            else:
                self.setStyleSheet("QWidget { border: 2px solid transparent; border-radius: 8px; }")
        super().mousePressEvent(event)



class MainWindow(QMainWindow):
    """Main window managing image groups and user actions."""
    def __init__(self, json_path):
        super().__init__()
        self.setWindowTitle("Image Review Tool")
        self.setMinimumSize(1200, 600)

        # Load JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        self.image_groups = list(data.values())
        self.total_groups = len(self.image_groups)
        self.current_group_index = 0

        # --- Layout setup ---
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Scrollable container for image panels
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.hbox = QHBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.hbox)
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        # Control buttons
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("⬅ Previous Group")
        self.prev_button.clicked.connect(self.prev_group)
        self.delete_button = QPushButton("🗑 Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.next_button = QPushButton("Next Group ➡")
        self.next_button.clicked.connect(self.next_group)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.next_button)
        self.layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        # --- Keyboard Shortcuts ---
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, activated=self.prev_group)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, activated=self.next_group)
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, activated=self.delete_selected)

        # Load first group
        self.panels = []
        self.load_group(self.current_group_index)

    def clear_group(self):
        """Remove all image panels."""
        for i in reversed(range(self.hbox.count())):
            widget = self.hbox.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.panels.clear()

    def load_group(self, index):
        """Load images for the specified group index."""
        self.clear_group()
        image_list = self.image_groups[index]

        for path in image_list:
            panel = ImagePanel(path)
            self.hbox.addWidget(panel)
            self.panels.append(panel)

        self.update_status()
        self.update_button_states()

    def delete_selected(self):
        """Delete selected images from the current group."""
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

    def next_group(self):
        """Move to the next group."""
        if self.current_group_index + 1 < self.total_groups:
            self.current_group_index += 1
            self.load_group(self.current_group_index)
        else:
            QMessageBox.information(self, "End", "No more groups left.")

    def prev_group(self):
        """Move to the previous group."""
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.load_group(self.current_group_index)
        else:
            QMessageBox.information(self, "Info", "Already at the first group.")

    def update_status(self):
        """Update window title and bottom label."""
        self.setWindowTitle(f"Image Review Tool - Group {self.current_group_index + 1}/{self.total_groups}")
        self.status_label.setText(
            f"Viewing Group {self.current_group_index + 1} of {self.total_groups} "
            "(←: Prev | →: Next | Del: Delete Selected)"
        )

    def update_button_states(self):
        """Enable/disable navigation buttons appropriately."""
        self.prev_button.setEnabled(self.current_group_index > 0)
        self.next_button.setEnabled(self.current_group_index < self.total_groups - 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    json_path = r"duplicates.json"  # ✅ update this to your JSON file
    window = MainWindow(json_path)
    #window.show()
    window.showMaximized()
    sys.exit(app.exec())
