from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt  # Needed for alignment

import sys, hashlib

# play video
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer


import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../video_img')))

from lib.Secure import Secure

secure = Secure()


a_s = ''
r_s = ''
istxt = 0


class Video(object):
    def setupUi(self, Steganography):
        Steganography.setObjectName("Steganography")
        Steganography.resize(1200, 800)  # Kích thước mới
        Steganography.setStyleSheet("#Steganography{\n"
                                         "    background-color: rgb(255,255,255);\n"
                                         "}\n"
                                         "\n"
                                         "#Header {\n"
                                         "    background-color: rgb(165, 213, 255);\n"
                                         "}\n"
                                         "\n"
                                         "#Header #Logo{\n"
                                         "    image: url(:/Pic/logo.png);\n"
                                         "    border: none;\n"
                                         "}\n"
                                         "\n"
                                         "#Header #NameSW{\n"
                                         "    font: 75 20pt \"Berlin Sans FB Demi\";\n"
                                         "}\n"
                                         "\n"
                                         "#btn_frame {\n"
                                         "    border: 1px solid black;\n"
                                         "    border-radius: 10px;\n"
                                         "    background-color: rgb(255,255,255);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton{\n"
                                         "    background-color:pink;\n"
                                         "    border-radius: 10px;\n"
                                         "    font: 75 14pt \"Berlin Sans FB Demi\";\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "    background-color: #be185d; /* Màu nền mới khi hover */\n"
                                         "    border-color: rgb(65, 173, 255);\n"
                                         "    color: rgb(255, 255, 255);\n"
                                         "}\n"
                                         "QLineEdit {\n"
                                         "    padding-left: 10px;\n" 
                                         "    border: 1px solid black;\n "
                                         "    border-radius: 5px;\n "
                                         "}\n"
                                         "QTextEdit {\n"
                                         "    padding: 10px;\n"
                                         "    border: 1px solid black;\n"
                                         "    border-radius: 5px;\n"
                                         "}\n"
                                         "\n")
        self.centralwidget = QtWidgets.QWidget(parent=Steganography)
        self.centralwidget.setObjectName("centralwidget")

        # Header
        self.Header = QtWidgets.QFrame(parent=self.centralwidget)
        self.Header.setGeometry(QtCore.QRect(0, 0, 1200, 100))  # Header kích thước mới
        self.Header.setObjectName("Header")
        self.NameSW = QtWidgets.QLabel(parent=self.Header)
        self.NameSW.setGeometry(QtCore.QRect(30, 20, 800, 50))  # Cập nhật vị trí và kích thước
        self.NameSW.setObjectName("NameSW")
        self.NameSW.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.label_class = QtWidgets.QLabel(parent=self.Header)
        self.label_class.setGeometry(QtCore.QRect(900, 20, 300, 50))  # Điều chỉnh vị trí label
        self.label_class.setStyleSheet("font: 75 22pt \"Berlin Sans FB Demi\";")
        self.label_class.setText("Send")
        self.label_class.setAlignment(QtCore.Qt.AlignmentFlag.AlignBottom|QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft)
        self.label_class.setObjectName("label_class")

        # Tabs
        self.tabWidget = QTabWidget(parent=self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 120, 1160, 650))  # Kích thước tab được mở rộng
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                font: bold 12pt "Arial";
                padding: 10px;
                width: 100px;                     
            }
            QTabBar::tab:selected {
                background-color: rgb(165, 213, 255);
                color: black;
            }
        """)
        self.vdsendTab = self.vdcreateSendTab()
        self.vdreceiveTab = self.vdcreateReceiveTab()

        self.tabWidget.addTab(self.vdsendTab, "Send")
        self.tabWidget.addTab(self.vdreceiveTab, "Receive")

        Steganography.setCentralWidget(self.centralwidget)

        # Connect signal to handle tab change
        self.tabWidget.currentChanged.connect(self.updateLabelClass)

        # Apply font globally
        self.vdapplyGlobalFont(self.centralwidget)

        self.retranslateUi(Steganography)
        QtCore.QMetaObject.connectSlotsByName(Steganography)

    def retranslateUi(self, Steganography):
        _translate = QtCore.QCoreApplication.translate
        Steganography.setWindowTitle(_translate("Steganography", "MainWindow"))
        self.NameSW.setText(_translate("Steganography", "VIDEO STEGANOGRAPHY"))

    def updateLabelClass(self, index):
        # Change label text based on the selected tab
        if index == 0:  
            self.label_class.setText("Send")
        elif index == 1:  
            self.label_class.setText("Receive")


    def createVideoWidget(self, is_send):
        vdlayout = QtWidgets.QVBoxLayout()

        # Frame for video display and controls
        videoFrame = QtWidgets.QFrame()
        videoFrame.setFixedHeight(410)  # Adjusted height for more compact layout
        videoFrame.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px;")
        videoFrameLayout = QtWidgets.QVBoxLayout(videoFrame)
        videoFrameLayout.setSpacing(0)  # Remove extra spacing in the layout

        # Video display
        videoWidget = QVideoWidget()
        videoWidget.setFixedSize(525, 300)
        videoFrameLayout.addWidget(videoWidget)

        # Slider layout
        vdsliderLayout = QtWidgets.QHBoxLayout()
        vdsliderLayout.setContentsMargins(0, 155, 0, 0)  # Remove margins around slider layout
        videoSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        videoSlider.setEnabled(False)
        videoSlider.sliderMoved.connect(lambda pos: self.vdsetPlaybackPosition(pos, is_send=is_send))
        vdsliderLayout.addWidget(videoSlider)
        videoFrameLayout.addLayout(vdsliderLayout)

        if is_send:
            self.videoSliderSend = videoSlider
            self.videoWidgetSend = videoWidget
        else:
            self.videoSliderReceive = videoSlider
            self.videoWidgetReceive = videoWidget

        # Controls layout
        vdcontrolsLayout = QtWidgets.QHBoxLayout()
        vdcontrolsLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins around controls

        # Skip backward button
        self.vdskipBackwardBtn = QtWidgets.QPushButton()
        self.vdskipBackwardBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\rpl5.png"))
        self.vdskipBackwardBtn.setIconSize(QtCore.QSize(30, 30))
        self.vdskipBackwardBtn.setFixedSize(50, 50)
        self.vdskipBackwardBtn.clicked.connect(lambda: self.skipMedia(-5000, is_send))
        vdcontrolsLayout.addWidget(self.vdskipBackwardBtn)

        # Play/Pause button
        self.vdplayMediaBtn = QtWidgets.QPushButton()
        self.vdplayMediaBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\play.png"))
        self.vdplayMediaBtn.setIconSize(QtCore.QSize(50, 50))
        self.vdplayMediaBtn.setFixedSize(60, 60)
        if is_send:
            self.vdplayMediaBtnSend = self.vdplayMediaBtn
            self.vdplayMediaBtn.clicked.connect(lambda: self.playMedia(is_send=True))
        else:
            self.vdplayMediaBtnReceive = self.vdplayMediaBtn
            self.vdplayMediaBtn.clicked.connect(lambda: self.playMedia(is_send=False))
        vdcontrolsLayout.addWidget(self.vdplayMediaBtn)

        # Skip forward button
        self.vdskipForwardBtn = QtWidgets.QPushButton()
        self.vdskipForwardBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\fw5.png"))
        self.vdskipForwardBtn.setIconSize(QtCore.QSize(30, 30))
        self.vdskipForwardBtn.setFixedSize(50, 50)
        self.vdskipForwardBtn.clicked.connect(lambda: self.skipMedia(5000, is_send))
        vdcontrolsLayout.addWidget(self.vdskipForwardBtn)

        videoFrameLayout.addLayout(vdcontrolsLayout)
        vdlayout.addWidget(videoFrame)

        # Path display layout
        videoPathLayout = QtWidgets.QHBoxLayout()
        videoPathLayout.setSpacing(5)  # Reduce space between path components

        videoPathLineEdit = QtWidgets.QLineEdit()
        videoPathLineEdit.setReadOnly(True)
        videoPathLineEdit.setFixedHeight(30)
        videoPathLineEdit.setPlaceholderText("Video file path...")
        videoPathLayout.addWidget(videoPathLineEdit)

        vdbrowseVideoBtn = QtWidgets.QPushButton("Browse Video")
        vdbrowseVideoBtn.setFixedSize(150, 30)
        vdbrowseVideoBtn.clicked.connect(lambda: self.vdload_file_send() if is_send else self.vdload_file_receive())
        videoPathLayout.addWidget(vdbrowseVideoBtn)

        vdlayout.addLayout(videoPathLayout)

        if is_send:
            self.videoPathLineEditSend = videoPathLineEdit
            self.vdmediaPlayerSend = QMediaPlayer()
            self.vdmediaPlayerSend.setVideoOutput(self.videoWidgetSend)
            self.vdmediaPlayerSend.positionChanged.connect(lambda pos: self.vdupdateSlider(pos, is_send=True))
            self.vdmediaPlayerSend.durationChanged.connect(lambda dur: self.vdupdateSliderRange(dur, is_send=True))
        else:
            self.videoPathLineEditReceive = videoPathLineEdit
            self.vdmediaPlayerReceive = QMediaPlayer()
            self.vdmediaPlayerReceive.setVideoOutput(self.videoWidgetReceive)
            self.vdmediaPlayerReceive.positionChanged.connect(lambda pos: self.vdupdateSlider(pos, is_send=False))
            self.vdmediaPlayerReceive.durationChanged.connect(lambda dur: self.vdupdateSliderRange(dur, is_send=False))

        return vdlayout

    def skipMedia(self, milliseconds, is_send):
        player = self.vdmediaPlayerSend if is_send else self.vdmediaPlayerReceive
        new_position = max(0, player.position() + milliseconds)
        player.setPosition(new_position)

    def playMedia(self, is_send):
        vdplayer = self.vdmediaPlayerSend if is_send else self.vdmediaPlayerReceive
        vdplayBtn = self.vdplayMediaBtnSend if is_send else self.vdplayMediaBtnReceive

        if vdplayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            vdplayer.pause()
            vdplayBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\play.png"))
        else:
            current_file = self.videoPathLineEditSend.text() if is_send else self.videoPathLineEditReceive.text()

            if current_file:
                if vdplayer.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                    vdplayer.play()
                    vdplayBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\pause.png"))
                else:
                    vdplayer.setSource(QUrl.fromLocalFile(current_file))
                    vdplayer.play()
                    vdplayBtn.setIcon(QtGui.QIcon(r"dashboard\resources\image\pause.png"))

    def vdupdateSlider(self, position, is_send):
        slider = self.videoSliderSend if is_send else self.videoSliderReceive
        slider.setValue(position)

    def vdupdateSliderRange(self, duration, is_send):
        slider = self.videoSliderSend if is_send else self.videoSliderReceive
        slider.setRange(0, duration)
        slider.setEnabled(True)

    def vdsetPlaybackPosition(self, position, is_send):
        player = self.vdmediaPlayerSend if is_send else self.vdmediaPlayerReceive
        player.setPosition(position)


    def vdcreateSendTab(self):
        vdtab = QWidget()
        vdlayout = QVBoxLayout()

        # Key input and Generate Key button
        vdkeyLayout = QHBoxLayout()

        vdkeyLabel = QLabel("Key: ")
        vdkeyLabel.setStyleSheet("font-size: 18px; font-weight: bold;")  # Tăng kích thước font và làm đậm chữ
        vdkeyLayout.addWidget(vdkeyLabel)

        self.vdkey1Input = QLineEdit()
        self.vdkey1Input.setPlaceholderText("Key: ")
        self.vdkey1Input.setFixedHeight(30)
        vdkeyLayout.addWidget(self.vdkey1Input)

        vdlayout.addLayout(vdkeyLayout)

        # Horizontal line after Key section
        vdkeyDivider = QtWidgets.QFrame()
        vdkeyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        vdkeyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        vdkeyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        vdlayout.addWidget(vdkeyDivider)

        # Horizontal layout to divide into two sections
        vdhorizontalLayout = QHBoxLayout()

        # Left Section: Secret message
        vdmessageLayout = QVBoxLayout()
        vdleftFrame = QtWidgets.QFrame()
        vdleftFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        vdleftFrameLayout = QVBoxLayout(vdleftFrame)

        vdmessageLabel = QLabel("Secret File (Only Image or Text file):")
        vdmessageLabel.setStyleSheet("border: none;")
        vdleftFrameLayout.addWidget(vdmessageLabel)

        # Trong createSendTab
        vdscrollArea = QtWidgets.QScrollArea()
        vdscrollArea.setFixedHeight(410)
        vdscrollArea.setWidgetResizable(True)
        vdscrollArea.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px; background-color: white;")
        self.vdsendMessageBox = QLabel()  # Đổi tên thành sendMessageBox
        self.vdsendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        vdscrollArea.setWidget(self.vdsendMessageBox)
        vdleftFrameLayout.addWidget(vdscrollArea)

        vdpathLayout = QHBoxLayout()
        self.vdfilePathLineEdit = QLineEdit()
        self.vdfilePathLineEdit.setReadOnly(True)
        self.vdfilePathLineEdit.setPlaceholderText("Image or text file path...")
        self.vdfilePathLineEdit.setFixedHeight(30)
        vdpathLayout.addWidget(self.vdfilePathLineEdit)

        self.vdbrowsefileBtn = QPushButton("Browse file")
        self.vdbrowsefileBtn.setFixedSize(150, 30)
        self.vdbrowsefileBtn.clicked.connect(self.vdload_image)
        vdpathLayout.addWidget(self.vdbrowsefileBtn)
        vdleftFrameLayout.addLayout(vdpathLayout)
        vdleftFrameLayout.addStretch()
        vdmessageLayout.addWidget(vdleftFrame)

        # Right Section: video
        vdvideoLayout = QVBoxLayout()
        vdrightFrame = QtWidgets.QFrame()
        vdrightFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        vdrightFrameLayout = QVBoxLayout(vdrightFrame)

        vdvideoLabelTitle = QLabel("Video file:")
        vdvideoLabelTitle.setStyleSheet("border: none;")
        vdrightFrameLayout.addWidget(vdvideoLabelTitle)

        # Directly add the video widget
        vdvideoPlayerLayout = self.createVideoWidget(is_send=True)
        vdrightFrameLayout.addLayout(vdvideoPlayerLayout)

        vdrightFrameLayout.addStretch()
        vdvideoLayout.addWidget(vdrightFrame)


        vdhorizontalLayout.addLayout(vdmessageLayout)
        vdhorizontalLayout.addLayout(vdvideoLayout)

        vdlayout.addLayout(vdhorizontalLayout)

        # Horizontal line after Key section
        vdkeyDivider = QtWidgets.QFrame()
        vdkeyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        vdkeyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        vdkeyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        vdlayout.addWidget(vdkeyDivider)

        # Buttons
        vdbuttonLayout = QHBoxLayout()
        self.vdencodeBtn = QPushButton("Encode")
        self.vdencodeBtn.setStyleSheet("margin-top: 10px;")
        self.vdencodeBtn.setFixedSize(200, 50)
        self.vdencodeBtn.setEnabled(False)
        self.vdencodeBtn.clicked.connect(self.vdencodeMessage)
        vdbuttonLayout.addWidget(self.vdencodeBtn)

        vdlayout.addLayout(vdbuttonLayout)
        vdtab.setLayout(vdlayout)
        return vdtab

    def vdcreateReceiveTab(self):
        vdtab = QWidget()
        vdlayout = QVBoxLayout()

        # Prime inputs
        vdprimeLayout = QHBoxLayout()

        vdprime1InputLabel = QLabel("Key: ")
        vdprime1InputLabel.setStyleSheet("font-size: 18px; font-weight: bold;")
        vdprimeLayout.addWidget(vdprime1InputLabel)

        self.vdprime1Input = QLineEdit()
        self.vdprime1Input.setPlaceholderText("Key: ")
        self.vdprime1Input.setFixedHeight(30)
        vdprimeLayout.addWidget(self.vdprime1Input)

        vdlayout.addLayout(vdprimeLayout)

        # Horizontal line after Key section
        vdkeyDivider = QtWidgets.QFrame()
        vdkeyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        vdkeyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        vdkeyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        vdlayout.addWidget(vdkeyDivider)


        # Horizontal layout to divide into two sections
        vdhorizontalLayout1 = QHBoxLayout()

        # Right Section: Secret message
        vdmessageLayout = QVBoxLayout()
        vdrightFrame = QtWidgets.QFrame()
        vdrightFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        vdrightFrameLayout = QVBoxLayout(vdrightFrame)

        vdmessageLabel = QLabel("Secret File:")
        vdmessageLabel.setStyleSheet("border: none;")
        vdrightFrameLayout.addWidget(vdmessageLabel)

        vdscrollArea = QtWidgets.QScrollArea()
        vdscrollArea.setFixedHeight(410)
        vdscrollArea.setWidgetResizable(True)
        vdscrollArea.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px; background-color: white;")
        self.vdreceiveMessageBox = QLabel()  # Đổi tên thành receiveMessageBox
        vdscrollArea.setWidget(self.vdreceiveMessageBox)
        vdrightFrameLayout.addWidget(vdscrollArea)

        vdpathLayout = QHBoxLayout()
        
        self.vdbrowsefileBtn = QPushButton("Save file")
        self.vdbrowsefileBtn.setFixedSize(150, 30)
        self.vdbrowsefileBtn.clicked.connect(self.vdsave)
        vdpathLayout.addWidget(self.vdbrowsefileBtn)
        vdrightFrameLayout.addLayout(vdpathLayout)
        vdrightFrameLayout.addStretch()
        vdmessageLayout.addWidget(vdrightFrame)

        # left Section: video
        vdvideoLayout = QVBoxLayout()
        vdleftFrame = QtWidgets.QFrame()
        vdleftFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        vdleftFrameLayout = QVBoxLayout(vdleftFrame)

        vdvideoLabelTitle = QLabel("Video Encoded file:")
        vdvideoLabelTitle.setStyleSheet("border: none;")
        vdleftFrameLayout.addWidget(vdvideoLabelTitle)

        # Directly add the video widget
        vdvideoPlayerLayout = self.createVideoWidget(is_send=False)
        vdleftFrameLayout.addLayout(vdvideoPlayerLayout)

        vdleftFrameLayout.addStretch()
        vdvideoLayout.addWidget(vdleftFrame)

        vdhorizontalLayout1.addLayout(vdvideoLayout)
        vdhorizontalLayout1.addLayout(vdmessageLayout)

        vdlayout.addLayout(vdhorizontalLayout1)

        # Horizontal line after Key section
        vdkeyDivider = QtWidgets.QFrame()
        vdkeyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        vdkeyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        vdkeyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        vdlayout.addWidget(vdkeyDivider)

        # Buttons in a row
        vdbuttonLayout2 = QHBoxLayout()

        self.vddecodeBtn = QPushButton("Decode")
        self.vddecodeBtn.setStyleSheet("margin-top: 10px;")
        self.vddecodeBtn.setFixedSize(200, 50)
        self.vddecodeBtn.setEnabled(False)
        self.vddecodeBtn.clicked.connect(self.vddecodeMessage)

        vdbuttonLayout2.addWidget(self.vddecodeBtn)
        vdlayout.addLayout(vdbuttonLayout2)

        vdtab.setLayout(vdlayout)
        return vdtab
    
    def vdload_file_send(self):
        global a_s
        vdsender_fname, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Video File", "", "Video Files (*.mp4)")
        if vdsender_fname:
            a_s = vdsender_fname
            self.videoPathLineEditSend.setText(vdsender_fname)
            self.vdencodeBtn.setEnabled(True)

            
    def vdload_file_receive(self):
        global r_s
        vdfname, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Video File", "", "Video Files (*.mp4)")
        if vdfname:
            r_s = vdfname
            self.videoPathLineEditReceive.setText(vdfname)
            self.vddecodeBtn.setEnabled(True)

    def vdapplyGlobalFont(self, widget):
        font = QtGui.QFont("Arial", 12)
        for child in widget.findChildren((QLabel, QLineEdit, QTextEdit)):
            child.setFont(font)

    def generate_aes_256_key(self, strPasswd):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(strPasswd.encode('utf-8'))
        return bytes.fromhex(sha256_hash.hexdigest())

    def vdload_image(self):
        # Open file dialog to select files (images and text files)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.centralwidget,
            "Open File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;Text Files (*.txt)",
        )

        if file_path:
            self.vdfilePathLineEdit.setText(file_path)  # Display file path
            self.vdsendMessageBox.clear()  # Sử dụng sendMessageBox

            if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                # Display image
                pixmap = QtGui.QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        400, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio
                    )
                    self.vdsendMessageBox.setPixmap(pixmap)  # Sử dụng sendMessageBox
                    self.vdsendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                else:
                    self.vdsendMessageBox.setText("Invalid image file.")  # Sử dụng sendMessageBox
            elif file_path.lower().endswith(".txt"):
                # Display text content
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        text_content = file.read()
                    if not text_content.strip():
                        raise ValueError("File is empty.")
                    self.vdsendMessageBox.setPixmap(QtGui.QPixmap())  # Sử dụng sendMessageBox
                    self.vdsendMessageBox.setText(text_content)
                    self.vdsendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                    self.vdsendMessageBox.setWordWrap(True)
                except Exception as e:
                    self.vdsendMessageBox.setText(f"Error reading file: {str(e)}")  # Sử dụng sendMessageBox


    def vdsave(self):
        # Mở hộp thoại để chọn vị trí và tên file lưu
        if istxt == 1:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.centralwidget,
                "Save File",
                "",
                "Text Files (*.txt);"
            )
        elif istxt == 2:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )    
        else:
            return    
        if not file_path:
            return

        try:
            # Kiểm tra xem nội dung trong receiveMessageBox là hình ảnh hay văn bản
            if istxt == 2:
                # Nếu là ảnh, lưu ảnh
                self.vdreceiveMessageBox.pixmap().save(file_path)
                qmb_custom("Success", "Message saved successfully!")
            elif istxt == 1:
                # Nếu là văn bản, lưu văn bản
                content = self.vdreceiveMessageBox.text()
                if not content.strip():
                    qmb_custom("Error", "No content to save.")
                    return

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                qmb_custom("Success", "Message saved successfully!")

        except Exception as e:
            qmb_custom("Error", f"Failed to save file: {str(e)}")

    def vdencodeMessage(self):
        fName = self.vdfilePathLineEdit.text()
        coverVideo = a_s
        z = self.vdkey1Input.text()
        if not z:
            qmb_custom("Error", "Please enter password")
            return
        if not fName:
            qmb_custom("Error", "Please upload file")
            return

        if coverVideo != "":
            if os.path.isfile(coverVideo):
                secure.secure_file_video(fName, coverVideo, z)
            else:
                qmb_custom("Error", f"Cover Video [{coverVideo}] does not exists...")
                secure.secure_file_video(fName, z)
        else:
            secure.secure_file_video(fName, z)

    def vddecodeMessage(self):
        global istxt
        stegoVideo = r_s  # File video đầu vào chứa dữ liệu mã hóa
        password = self.vdprime1Input.text()

        if not password:
            qmb_custom("Error", "Please enter password")
            return

        # File tạm
        temp_output_file = "out"

        try:
            secure.desecure_file_video(stegoVideo, password, temp_output_file)
        except Exception as e:
            return

        try:
            file_type = detect_file_type(temp_output_file)
        except:
            return
        if file_type == 'jpg':
            # Xử lý khi file là ảnh
            pixmap = QtGui.QPixmap(temp_output_file)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    400, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )
                self.vdreceiveMessageBox.setPixmap(pixmap)
                self.vdreceiveMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                qmb_custom("Success", "Message decoded successfully")
                istxt = 2
                return
        elif file_type == 'txt':
            # Xử lý khi file là text
            with open(temp_output_file, "r", encoding="utf-8") as file:
                text_content = file.read()
                self.vdreceiveMessageBox.setPixmap(QtGui.QPixmap())  # Sử dụng sendMessageBox
                self.vdreceiveMessageBox.setText(text_content)
                self.vdreceiveMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                self.vdreceiveMessageBox.setWordWrap(True)
                qmb_custom("Success", "Message decoded successfully")
                istxt = 1
        else:
            os.remove("out.enc")
            return

        os.remove("out")

    def showError(self, message):
        qmb_custom("Error", message)
        #QMessageBox.critical(self.centralwidget, "Error", message)

    def showInfo(self, message):
        qmb_custom("Info", message)
        #QMessageBox.information(self.centralwidget, "Info", message)

def qmb_custom(string1, string2):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle(string1)
    msg_box.setText(string2)
    # Thiết lập StyleSheet để căn giữa văn bản
    msg_box.setStyleSheet(
        "QLabel{font: 15pt \"Berlin Sans FB\"; min-height:150 px; min-width: 400px;} QPushButton{ width:100px; height:30px; border-radius: 5px; font: 75 14pt \"Berlin Sans FB Demi\"; background-color: rgb(165, 213, 255);} QPushButton:hover{background-color: rgb(3, 105, 161); color: rgb(255,255,255);}"
        )
    msg_box.exec()

def detect_file_type(file_path):
    with open(file_path, 'rb') as file:
        header = file.read(4)  # Đọc 4 byte đầu tiên
        if header.startswith(b'\xFF\xD8'):
            return 'jpg'
        try:
            with open(file_path, 'r', encoding='utf-8') as text_file:
                text_file.read()  # Thử đọc file như text
                return 'txt'
        except:
            pass
    return 'unknown'

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Video()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
