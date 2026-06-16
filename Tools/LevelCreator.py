import json
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QImage, QAction, QKeySequence
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (
    QApplication,
    QMenu,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSpinBox,
    QMessageBox,
)
from pathlib import Path

def resolve_path(folder, name):
    return str(Path(folder) / name)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
}

#This is the imported folders Image's object
class ThumbnailLabel(QLabel):
    def __init__(self, image_path, main_window):
        super().__init__()

        self.image_path = image_path
        self.main_window = main_window

        pix = QPixmap(image_path)
        pix = pix.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(pix)
        self.setFixedSize(110, 110)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.main_window.select_thumbnail(self)
        super().mousePressEvent(event)

#This is the grid's image object
class ImageCell(QLabel):
    def __init__(self, main_window):
        super().__init__()

        self.image_path = None
        self.setMouseTracking(True)
        self.main_window = main_window

        self.setAcceptDrops(True)
        self.setFixedSize(32, 32)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            QLabel {
                border: 1px solid #999;
                background: white;
            }
        """)

    def set_image(self, path):
        if not path:
            return
        self.image_path = path
        self.refresh_pixmap()

    def clear_image(self):
        self.image_path = None
        self.clear()

    def refresh_pixmap(self, size=32):
        if not self.image_path:
            self.clear()
            return

        pix = QPixmap(self.image_path)
        pix = pix.scaled(
            size,
            size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.setPixmap(pix)

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)
        self.musicFile = "TenseSynthPad.wav"
        self.musicFilePath = str(Path("..") / "Assets" / "Music" / self.musicFile)
        self.player.setSource(QUrl.fromLocalFile(self.musicFilePath))
        self.audio_output.setVolume(0.5)  # 0.0 - 1.0

        button = QPushButton("Play Music")
        button.clicked.connect(self.player.play)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.player.stop)

        select_btn = QPushButton("Select Song")
        select_btn.clicked.connect(self.select_music_file)

        self.label = QLabel("Default music selected")

        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(stop_btn)
        layout.addWidget(select_btn)
        self.setLayout(layout)

    def select_music_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Music File",
            str(Path("..") / "Assets" / "Music" ),
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;All Files (*)"
        )

        if file_path:
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.label.setText(f"Selected: {file_path.split('/')[-1]}")
            self.load_music(file_path.split('/')[-1])

        return None
    def load_music(self, music_file):
        self.musicFile = music_file
        self.musicFilePath = str(Path("..") / "Assets" / "Music" / self.musicFile)
        self.player.setSource(QUrl.fromLocalFile(self.musicFilePath))

#This is the Program's Window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Drag-and-Drop Image Grid")
        self.resize(1200, 800)

        self.zoom = 1.0
        self.selected_image = None
        self.selected_thumbnail = None

        self.painting = False
        self.painting_mode = None

        main_layout = QVBoxLayout(self)

        controls = QHBoxLayout()

        self.load_button = QPushButton("Load Folder")
        self.load_button.clicked.connect(self.load_folder)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 999)
        self.rows_spin.setValue(64)

        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 999)
        self.cols_spin.setValue(64)

        rebuild_button = QPushButton("Rebuild Grid")
        rebuild_button.clicked.connect(self.rebuild_grid_confirmed)

        export_button = QPushButton("Export Grid")
        export_button.clicked.connect(self.save_json_grid)

        import_button = QPushButton("Import Grid")
        import_button.clicked.connect(self.load_json_grid)

        self.grid_visible = True
        self.toggle_grid_btn = QPushButton("Hide Grid")
        self.toggle_grid_btn.clicked.connect(self.toggle_grid)

        controls.addWidget(self.toggle_grid_btn)

        controls.addWidget(self.load_button)
        controls.addWidget(QLabel("Rows"))
        controls.addWidget(self.rows_spin)
        controls.addWidget(QLabel("Columns"))
        controls.addWidget(self.cols_spin)
        controls.addWidget(rebuild_button)
        controls.addWidget(export_button)
        controls.addWidget(import_button)
        self.music_player = MusicPlayer()
        controls.addWidget(self.music_player)
        controls.addStretch()

        main_layout.addLayout(controls)

        body = QHBoxLayout()
        main_layout.addLayout(body)

        # Thumbnail panel
        thumb_scroll = QScrollArea()
        thumb_scroll.setWidgetResizable(True)

        self.thumb_container = QWidget()
        self.thumb_layout = QVBoxLayout(self.thumb_container)

        thumb_scroll.setWidget(self.thumb_container)

        body.addWidget(thumb_scroll, 1)

        # Grid panel
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)

        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setWidget(self.grid_container)

        body.addWidget(grid_scroll, 3)

        self.cells = []

        self.build_grid()
        self.load_folder()
    #Zoom on Grid
    def apply_zoom(self):
        size = int(32 * self.zoom)

        for cell in self.cells:
            cell.setFixedSize(size, size)
            cell.refresh_pixmap(size)
    #When mouse wheel and ctrl(Mac key on mac) zoom on grid
    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()

            if delta > 0:
                self.zoom *= 1.1
            else:
                self.zoom *= 0.9

            self.zoom = max(0.2, min(5.0, self.zoom))

            self.apply_zoom()

            event.accept()
            return

        super().wheelEvent(event)
    #Click on thumbnail, allows you to "paint" with it later on the grid
    def select_thumbnail(self, thumbnail):
        if self.selected_thumbnail:
            self.selected_thumbnail.setStyleSheet("")

        self.selected_thumbnail = thumbnail
        self.selected_image = thumbnail.image_path

        thumbnail.setStyleSheet("""
            QLabel {
                border: 2px solid blue;
            }
        """)
    #Init grid rows and columns
    def build_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cells.clear()

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        for r in range(rows):
            for c in range(cols):
                cell = ImageCell(self)

                self.grid_layout.addWidget(cell, r, c)

                self.cells.append(cell)
    #load Folder button function
    #Imports all images in folder
    def load_folder(self):

        while self.thumb_layout.count():
            item = self.thumb_layout.takeAt(0)

            widget = item.widget()
            if widget:
                widget.deleteLater()

        folder = str(Path("..")/"Assets"/"Art"/"")

        paths = sorted(Path(folder).iterdir())

        count = 0

        for path in paths:
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            thumb = ThumbnailLabel(str(path), self)
            self.thumb_layout.addWidget(thumb)
            count += 1

        self.thumb_layout.addStretch()

    #Turn grid lines on/off
    def toggle_grid(self):
            self.grid_visible = not self.grid_visible

            if self.grid_visible:
                style = """
                    QLabel {
                        border: 1px solid #d0d0d0;
                        background: white;
                    }
                """
                self.toggle_grid_btn.setText("Hide Grid")
            else:
                style = """
                    QLabel {
                        border: none;
                        background: white;
                    }
                """
                self.toggle_grid_btn.setText("Show Grid")

            for cell in self.cells:
                cell.setStyleSheet(style)
    #Internal Function to control painting
    def stop_painting(self):
        self.painting = False
        self.painting_mode = None

    #internal function to paint on grid
    def paint_at(self, pos):
        cell = self.cell_at_pos(pos)
        if not cell:
            return

        if self.painting_mode == "erase":
            cell.clear_image()

        elif self.painting_mode == "paint":
            if self.selected_image:
                cell.set_image(self.selected_image)
    #Grid Helper Function to get cell at current mouse position
    def cell_at_pos(self, pos):
        grid_pos = self.grid_container.mapFrom(self, pos)
        widget = self.grid_container.childAt(grid_pos)

        if isinstance(widget, ImageCell):
            return widget

        return None
    #Paint or erase on grid when mouse is pressed
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selected_image:
            self.painting = True
            self.painting_mode = "paint"
            self.paint_at(event.pos())

        elif event.button() == Qt.MouseButton.RightButton:
            self.painting = True
            self.painting_mode = "erase"
            self.paint_at(event.pos())

        event.accept()
    #Paint or erase on grid when mouse is moved
    def mouseMoveEvent(self, event):
        if self.painting:
            self.paint_at(event.pos())
            event.accept()
            return

        super().mouseMoveEvent(event)
    #Stop painting when mouse is released
    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.painting = False
            self.painting_mode = None
            event.accept()
            return

        super().mouseReleaseEvent(event)
    #Export grid to JSON file
    def export_grid(self):
        populated = [c for c in self.cells if c.image_path]

        if not populated:
            QMessageBox.warning(
                self,
                "Nothing to Export",
                "No images have been placed."
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Grid",
            "",
            "PNG (*.png)"
        )

        if not save_path:
            return

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        cell_w = 300
        cell_h = 300

        canvas = QImage(
            cols * cell_w,
            rows * cell_h,
            QImage.Format.Format_RGB32
        )

        canvas.fill(Qt.GlobalColor.white)

        painter = QPainter(canvas)

        for index, cell in enumerate(self.cells):
            if not cell.image_path:
                continue

            row = index // cols
            col = index % cols

            x = col * cell_w
            y = row * cell_h

            pix = QPixmap(cell.image_path)

            scaled = pix.scaled(
                cell_w,
                cell_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            px = x + (cell_w - scaled.width()) // 2
            py = y + (cell_h - scaled.height()) // 2

            painter.drawPixmap(px, py, scaled)

        painter.end()

        canvas.save(save_path)

        QMessageBox.information(
            self,
            "Export Complete",
            f"Saved:\n{save_path}"
        )
    #Remake grid with new dimensions
    def rebuild_grid_confirmed(self):
        reply = QMessageBox.warning(
            self,
            "Rebuild Grid",
            "Rebuilding the grid will rearrange layout.\n"
            "Images will be preserved if possible.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        self.rebuild_grid()
    #Helper function to rebuild grid with new dimensions
    def rebuild_grid(self):
        old_images = []

        # save current layout
        for cell in self.cells:
            old_images.append(cell.image_path)

        # build new grid
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        new_cells = []

        for r in range(rows):
            for c in range(cols):
                cell = ImageCell(self)
                new_cells.append(cell)

        # remap images
        for i in range(min(len(old_images), len(new_cells))):
            if old_images[i]:
                new_cells[i].set_image(old_images[i])

        # replace grid UI
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cells = new_cells

        # re-add widgets
        for i, cell in enumerate(self.cells):
            r = i // cols
            c = i % cols
            self.grid_layout.addWidget(cell, r, c)
    #Save grid to JSON file
    def save_json_grid(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Grid",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        cols = self.cols_spin.value()

        grid = []

        for r in range(self.rows_spin.value()):
            row = []

            for c in range(cols):
                index = r * cols + c
                cell = self.cells[index]

                if cell.image_path:
                    name = Path(cell.image_path).name
                else:
                    name = None

                row.append(name)

            grid.append(row)
        data = {
            "music": self.music_player.musicFile,
            "grid": grid
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    #Load grid from JSON file
    def load_json_grid(self):
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Load Grid",
                    "",
                    "JSON Files (*.json)"
                )

                if not file_path:
                    return

                with open(file_path, "r") as f:
                    data = json.load(f)

                #folder = data["folder"]
                folder = str(Path("..")/"Assets"/"Art"/"")
                grid = data["grid"]
                music = data["music"]
                self.music_player.load_music(music)

                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 0

                self.rows_spin.setValue(rows)
                self.cols_spin.setValue(cols)

                self.build_grid()

                for r, row in enumerate(grid):
                    for c, name in enumerate(row):

                        if not name:
                            continue

                        index = r * cols + c

                        if 0 <= index < len(self.cells):
                            path = resolve_path(folder, name)
                            self.cells[index].set_image(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
