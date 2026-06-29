import json
import sys
from pathlib import Path
from PyQt6.QtCore import Qt, QMimeData, QUrl
from PyQt6.QtGui import QPixmap, QDrag, QPainter, QImage, QAction, QKeySequence, QTransform
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
    QStackedLayout,
    QSpinBox,
    QMessageBox, QDoubleSpinBox, QLineEdit, QFormLayout,
)

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
class PlacedAsset(QLabel):
    def __init__(self, image_path, parent):
        super().__init__(parent)

        self.image_path = image_path

        self.attributes = {
            "name": Path(image_path).stem,
            "type": "object",
            "x": 0,
            "y": 0,
            "scale": 1.0,
            "rotation": 0,
        }

        self.original_pixmap = QPixmap(image_path)
        self.base_size = self.original_pixmap.size()

        #self.update_transform()
        self.setPixmap(QPixmap(self.image_path))

        self.dragging = False
        self.drag_offset = None

    def update_transform(self, zoom=1.0):

        scale = self.attributes["scale"] * zoom
        angle = self.attributes["rotation"]

        # Keep current center
        center_x = self.x() + self.width() / 2
        center_y = self.y() + self.height() / 2

        pix = self.original_pixmap

        new_width = int(pix.width() * scale)
        new_height = int(pix.height() * scale)

        pix = pix.scaled(
            new_width,
            new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        transform = QTransform()
        transform.rotate(angle)

        pix = pix.transformed(
            transform,
            Qt.TransformationMode.SmoothTransformation
        )

        self.setPixmap(pix)
        self.setFixedSize(pix.size())

        # restore center
        self.move(
            int(center_x - self.width() / 2),
            int(center_y - self.height() / 2)
        )

    def update_pixmap(self, size):
        pix = QPixmap(self.image_path)

        self.setPixmap(
            pix.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        self.setFixedSize(size, size)

    def mouseMoveEvent(self, event):
        if not self.dragging:
            return

        new_pos = self.pos() + event.pos() - self.drag_offset

        self.move(new_pos)

        zoom = self.parent().main_window.zoom

        self.attributes["x"] = (self.x() + self.width() / 2
                               ) / zoom

        self.attributes["y"] = (self.y() + self.height() / 2
                               ) / zoom

        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.delete_asset()
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.parent().main_window.select_placed_asset(self)

            self.dragging = True
            self.drag_offset = event.pos()

            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        event.accept()

    def delete_asset(self):
        canvas = self.parent()

        if self in canvas.assets:
            canvas.assets.remove(self)

        if canvas.main_window.selected_asset is self:
            canvas.main_window.clear_asset_selection()

        self.deleteLater()

    def reposition(self, zoom):
        self.move(
            int(self.attributes["x"] * zoom - self.width() / 2),
            int(self.attributes["y"] * zoom - self.height() / 2)
        )

#Attributes for objects
class AssetProperties(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.asset = None

        layout = QFormLayout()

        self.name = QLineEdit()

        self.type = QLineEdit()

        self.scale = QDoubleSpinBox()
        self.scale.setRange(0.1, 10)
        self.scale.setSingleStep(0.1)

        self.rotation = QDoubleSpinBox()
        self.rotation.setRange(0, 360)

        layout.addRow("Name", self.name)
        layout.addRow("Type", self.type)
        layout.addRow("Scale", self.scale)
        layout.addRow("Rotation", self.rotation)

        self.setLayout(layout)

        self.name.editingFinished.connect(self.update_asset)
        self.type.editingFinished.connect(self.update_asset)
        self.scale.valueChanged.connect(self.update_asset)
        self.rotation.valueChanged.connect(self.update_asset)

    def show_asset(self, asset):
        self.asset = asset

        self.name.setText(asset.attributes["name"])
        self.type.setText(asset.attributes["type"])

        self.scale.blockSignals(True)
        self.rotation.blockSignals(True)

        self.scale.setValue(asset.attributes["scale"])
        self.rotation.setValue(asset.attributes["rotation"])

        self.scale.blockSignals(False)
        self.rotation.blockSignals(False)


    def update_asset(self):

        if not self.asset:
            return

        self.asset.attributes["name"] = self.name.text()
        self.asset.attributes["type"] = self.type.text()

        self.asset.attributes["scale"] = self.scale.value()
        self.asset.attributes["rotation"] = self.rotation.value()

        x = self.asset.x()
        y = self.asset.y()

        self.asset.update_transform(self.main_window.zoom)

        self.asset.move(x, y)
#Where the assets are placed
class AssetCanvas(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window

        self.setAcceptDrops(True)

        self.setStyleSheet("""
            background: transparent;
        """)

        self.assets = []
        self.setMouseTracking(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        path = event.mimeData().text()

        asset = PlacedAsset(path, self)

        # Convert drop position to canvas coordinates
        pos = event.position().toPoint()

        zoom = self.main_window.zoom

        x = pos.x()
        y = pos.y()

        asset.update_transform(self.main_window.zoom)

        asset.attributes["x"] = x / zoom
        asset.attributes["y"] = y / zoom

        asset.move(
            int(x - asset.width() / 2),
            int(y - asset.height() / 2)
        )

        asset.show()

        self.assets.append(asset)

        event.acceptProposedAction()


#This is the asset object list
class AssetLabel(QLabel):
    def __init__(self, image_path, main_window):
        super().__init__()

        self.image_path = image_path
        self.main_window = main_window

        pix = QPixmap(image_path)
        pix = QPixmap(image_path)

        if pix.isNull():
            print("FAILED:", image_path)
        else:
            print("SUCCESS:", image_path)
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

        self.main_window.select_asset(self)
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        drag = QDrag(self)

        mime = QMimeData()
        mime.setText(self.image_path)

        drag.setMimeData(mime)

        if self.pixmap():
            drag.setPixmap(self.pixmap())

        drag.exec()

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

    def set_asset(self, path):
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
        self.selected_tile = None
        self.selected_asset_image = None
        self.selected_thumbnail = None
        self.selected_asset = None

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
        self.asset_layer_visible = True

        self.toggle_asset_layer_btn = QPushButton(
            "Hide Asset Layer"
        )

        self.toggle_asset_layer_btn.clicked.connect(
            self.toggle_asset_layer
        )

        controls.addWidget(self.toggle_asset_layer_btn)
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

        self.asset_scroll = QScrollArea()
        self.asset_scroll.setWidgetResizable(True)

        self.asset_container = QWidget()
        self.asset_layout = QVBoxLayout(self.asset_container)

        self.asset_scroll.setWidget(self.asset_container)

        body.addWidget(self.asset_scroll, 1)

        # Grid panel
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)

        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)

        self.asset_canvas = AssetCanvas(self)

        self.grid_stack = QWidget()

        stack = QStackedLayout(self.grid_stack)
        stack.setStackingMode(QStackedLayout.StackingMode.StackAll)

        stack.addWidget(self.grid_container)
        stack.addWidget(self.asset_canvas)

        grid_scroll.setWidget(self.grid_stack)

        body.addWidget(grid_scroll, 3)

        self.asset_canvas.raise_()

        self.asset_properties = AssetProperties(self)

        body.addWidget(
            self.asset_properties,
            1
        )

        self.asset_properties.hide()

        self.cells = []

        self.build_grid()
        self.load_folder()

    def select_placed_asset(self, asset):

        if self.selected_asset and self.selected_asset is not asset:
            try:
                self.selected_asset.setStyleSheet("")
            except RuntimeError:
                self.selected_asset = None

        self.selected_asset = asset

        asset.setStyleSheet("""
            QLabel {
                border: 2px solid yellow;
            }
        """)

        self.asset_properties.show()
        self.asset_properties.show_asset(asset)

    def toggle_asset_layer(self):
        self.asset_layer_visible = not self.asset_layer_visible

        # Hide/show placed objects
        self.asset_canvas.setVisible(self.asset_layer_visible)

        # Hide/show asset selection panel
        self.asset_scroll.setVisible(self.asset_layer_visible)

        self.toggle_asset_layer_btn.setText(
            "Hide Asset Layer"
            if self.asset_layer_visible
            else "Show Asset Layer"
        )

    def clear_asset_selection(self):
        self.selected_asset = None
        self.asset_properties.asset = None
        self.asset_properties.hide()
    #Zoom on Grid
    def apply_zoom(self):
        size = int(32 * self.zoom)

        for cell in self.cells:
            cell.setFixedSize(size, size)
            cell.refresh_pixmap(size)

        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        self.asset_canvas.resize(
            cols * size,
            rows * size
        )

        # Scale placed assets


        for asset in self.asset_canvas.assets:
            asset.update_transform(self.zoom)
            asset.reposition(self.zoom)


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
    #Click on assets, allows you to "paint" with it later on the grid
    def select_asset(self, asset):
        if self.selected_asset:
            self.selected_asset.setStyleSheet("")

        self.selected_asset = asset
        self.selected_asset_image = asset.image_path

        asset.setStyleSheet("""
            QLabel {
                border: 2px solid blue;
            }
        """)

    #Click on thumbnail, allows you to "paint" with it later on the grid
    def select_thumbnail(self, thumbnail):
        if self.selected_thumbnail:
            self.selected_thumbnail.setStyleSheet("")

        self.selected_thumbnail = thumbnail
        self.selected_tile = thumbnail.image_path

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
        rows = self.rows_spin.value()
        cols = self.cols_spin.value()

        size = int(32 * self.zoom)

        self.asset_canvas.resize(
            cols * size,
            rows * size
        )
    #load Folder button function
    #Imports all images in folder
    def load_folder(self):

        while self.thumb_layout.count():
            item = self.thumb_layout.takeAt(0)

            widget = item.widget()
            if widget:
                widget.deleteLater()

        folder = str(Path("..")/"Assets"/"Art"/"Tile")

        paths = sorted(Path(folder).iterdir())

        count = 0

        for path in paths:
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            thumb = ThumbnailLabel(str(path), self)
            self.thumb_layout.addWidget(thumb)
            count += 1

        asset_folder = str(Path("..") / "Assets" / "Art" / "LevelAssets")
        paths = sorted(Path(asset_folder).iterdir())

        for path in paths:
            if path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            thumb = AssetLabel(str(path), self)
            self.asset_layout.addWidget(thumb)



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
            if self.selected_tile:
                cell.set_image(self.selected_tile)
            # if self.selected_asset_image:
            #     cell.set_asset(self.selected_asset_image)
    #Grid Helper Function to get cell at current mouse position
    def cell_at_pos(self, pos):
        grid_pos = self.grid_container.mapFrom(self, pos)
        widget = self.grid_container.childAt(grid_pos)

        if isinstance(widget, ImageCell):
            return widget

        return None
    #Paint or erase on grid when mouse is pressed
    def mousePressEvent(self, event):

        widget = self.childAt(event.pos())

        if isinstance(widget, PlacedAsset):
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.painting = True
            self.painting_mode = "paint"
            self.paint_at(event.pos())

        elif event.button() == Qt.MouseButton.RightButton:
            self.painting = True
            self.painting_mode = "erase"
            self.paint_at(event.pos())
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

        asset_data = []

        for asset in self.asset_canvas.assets:
            asset.attributes["x"] = (
                                            asset.x() + asset.width() / 2
                                    ) / self.zoom

            asset.attributes["y"] = (
                                            asset.y() + asset.height() / 2
                                    ) / self.zoom

            asset_data.append({
                "image": Path(asset.image_path).name,
                "attributes": asset.attributes.copy()
            })


        data = {
            "music": self.music_player.musicFile,
            #"spawn": [["level": "level1.json", "x": 0, "y": 0]],
            "grid": grid,
            "assets": asset_data
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
                # Load placed assets
                assets = data.get("assets", [])


                self.music_player.load_music(music)

                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 0

                self.rows_spin.setValue(rows)
                self.cols_spin.setValue(cols)

                self.build_grid()

                # Remove existing placed assets
                for asset in self.asset_canvas.assets:
                    asset.deleteLater()

                self.asset_canvas.assets.clear()

                asset_folder = Path("..") / "Assets" / "Art" / "LevelAssets"

                for info in assets:
                    image_path = str(asset_folder / info["image"])

                    asset = PlacedAsset(
                        image_path,
                        self.asset_canvas
                    )

                    loaded_attributes = info.get("attributes", {})

                    asset.attributes.update(
                        loaded_attributes
                    )

                    zoom = self.zoom

                    asset.update_transform(self.zoom)
                    asset.reposition(self.zoom)

                    asset.show()

                    self.asset_canvas.assets.append(asset)

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
