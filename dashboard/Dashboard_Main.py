import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QListWidgetItem, QWidget, QGridLayout, QVBoxLayout, QFrame, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from video_img.imagegui import Image

from audiogui import Audio

from video_img.videogui import Video


# Import the UI class from the 'main_ui' module
from Dashboard_UI import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        

        # Initialize the UI from the generated 'main_ui' class
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(1450, 800)
        # Set window properties
        self.setWindowTitle("STEGANOGRAPHY APP")

        # Initialize UI elements
        self.title_label = self.ui.title_label
        self.title_label.setText("Dashboard")

        self.title_icon = self.ui.title_icon
        self.title_icon.setText("")
        self.title_icon.setPixmap(QPixmap(r""))
        self.title_icon.setScaledContents(True)

        self.side_menu = self.ui.listWidget
        self.side_menu.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu_icon_only = self.ui.listWidget_icon_only
        self.side_menu_icon_only.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.side_menu_icon_only.hide()
        self.main_content = self.ui.stackedWidget
        
        self.menu_btn = self.ui.menu_btn
        self.menu_btn.setText("")
        self.menu_btn.setIcon(QIcon(r""))
        self.menu_btn.setIconSize(QSize(30, 30))
        self.menu_btn.setCheckable(True)
        self.menu_btn.setChecked(False)

        # Define a list of menu items with names and icons
        self.menu_list = [
            {
                "name": "AUDIO",
                "icon": r"D:\StudySpace\HK5\ATM\Project\NT140---STEGANOGRAPHY\dashboard\resources\image\audio.png"
            },
            {
                "name": "IMAGE",
                "icon": r"D:\StudySpace\HK5\ATM\Project\NT140---STEGANOGRAPHY\dashboard\resources\image\img.png"
            },
            {
                "name": "VIDEO",
                "icon": r"D:\StudySpace\HK5\ATM\Project\NT140---STEGANOGRAPHY\dashboard\resources\image\video.png"
            },
        ]

        # Initialize the UI elements and slots
        self.init_list_widget()
        self.init_stackwidget()
        self.init_single_slot()
        
        # Set initial page
        self.main_content.setCurrentIndex(0)
        self.side_menu.setCurrentRow(0)
        self.side_menu_icon_only.setCurrentRow(0)
    
    def init_single_slot(self):
        
        # Connect signals and slots for switching between menu items
        self.side_menu.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu_icon_only.currentRowChanged['int'].connect(self.main_content.setCurrentIndex)
        self.side_menu.currentRowChanged['int'].connect(self.side_menu_icon_only.setCurrentRow)
        self.side_menu_icon_only.currentRowChanged['int'].connect(self.side_menu.setCurrentRow)
        # self.menu_btn.toggled.connect(self.button_icon_change)

    def init_list_widget(self):
        # Initialize the side menu and side menu with icons only
        self.side_menu_icon_only.clear()
        self.side_menu.clear()

        for menu in self.menu_list:
            # Set items for the side menu with icons only
            item = QListWidgetItem()
            item.setIcon(QIcon(menu.get("icon")))
            item.setSizeHint(QSize(40, 40))
            self.side_menu_icon_only.addItem(item)
            self.side_menu_icon_only.setCurrentRow(0)

            # Set items for the side menu with icons and text
            item_new = QListWidgetItem()
            item_new.setIcon(QIcon(menu.get("icon")))
            item_new.setText(menu.get("name"))
            self.side_menu.addItem(item_new)
            self.side_menu.setCurrentRow(0)
            
    
         
    def init_stackwidget(self):
        # Create 3 empty QMainWindow instances
        window_1 = Audio()
        audio =  QMainWindow()
        window_1.setupUi(audio)

        window_2 = Image()
        image =  QMainWindow()
        window_2.setupUi(image)

        window_3 = Video()
        video =  QMainWindow()
        window_3.setupUi(video)

        # Add the empty QMainWindow instances to the QStackWidget
        self.main_content.insertWidget(0, audio)
        self.main_content.insertWidget(1, image)
        self.main_content.insertWidget(2, video)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Load style file
    with open(r"D:\StudySpace\HK5\ATM\Project\NT140---STEGANOGRAPHY\Dashboard\Dashboard.qss") as f:
        style_str = f.read()

    app.setStyleSheet(style_str)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())