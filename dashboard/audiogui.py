from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt  # Needed for alignment

import random
import string
import hashlib
import sys

# play audio
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PIL import Image
from audio.AES.sender import Sender
from audio.AES.receiver import receiver
from audio.steganography.encode_song import encode
from audio.steganography.decode_song import decode



sender_fname = ''
fname = ''
file_message = ''

class Audio(object):
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
        self.sendTab = self.createSendTab()
        self.receiveTab = self.createReceiveTab()

        self.tabWidget.addTab(self.sendTab, "Send")
        self.tabWidget.addTab(self.receiveTab, "Receive")

        Steganography.setCentralWidget(self.centralwidget)

        # Connect signal to handle tab change
        self.tabWidget.currentChanged.connect(self.updateLabelClass)

        # Apply font globally
        self.applyGlobalFont(self.centralwidget)

        self.retranslateUi(Steganography)
        QtCore.QMetaObject.connectSlotsByName(Steganography)

    def retranslateUi(self, Steganography):
        _translate = QtCore.QCoreApplication.translate
        Steganography.setWindowTitle(_translate("Steganography", "MainWindow"))
        self.NameSW.setText(_translate("Steganography", "AUDIO STEGANOGRAPHY"))

    def updateLabelClass(self, index):
        # Change label text based on the selected tab
        if index == 0:  
            self.label_class.setText("Send")
        elif index == 1:  
            self.label_class.setText("Receive")


    # play audio 
    def createAudioWidget(self, is_send):
        layout = QtWidgets.QVBoxLayout()

        # Frame for slider, controls, and image
        controlFrame = QtWidgets.QFrame()
        controlFrame.setFixedHeight(410)
        controlFrame.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px;")
        controlFrameLayout = QtWidgets.QVBoxLayout(controlFrame)

        # Image display
        imageLabel = QtWidgets.QLabel()
        imageLabel.setPixmap(QtGui.QPixmap(r"resources\image\wavefile.png").scaled(600, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        controlFrameLayout.addWidget(imageLabel)

        # Slider layout
        sliderLayout = QtWidgets.QHBoxLayout()
        audioSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        audioSlider.setEnabled(False)
        audioSlider.sliderMoved.connect(lambda pos: self.setPlaybackPosition(pos, is_send=is_send))
        sliderLayout.addWidget(audioSlider)
        controlFrameLayout.addLayout(sliderLayout)
        if is_send:
            self.audioSliderSend = audioSlider
        else:
            self.audioSliderReceive = audioSlider

        # Controls layout
        controlsLayout = QtWidgets.QHBoxLayout()

        # Skip backward button
        self.skipBackwardBtn = QtWidgets.QPushButton()  # Store as class attribute
        self.skipBackwardBtn.setIcon(QtGui.QIcon(r"resources\image\rpl5.png"))  # Replace with your image file
        self.skipBackwardBtn.setIconSize(QtCore.QSize(30, 30))
        self.skipBackwardBtn.setFixedSize(50, 50)
        self.skipBackwardBtn.clicked.connect(lambda: self.skipAudio(-5000, is_send))
        controlsLayout.addWidget(self.skipBackwardBtn)

        # Play/Pause button
        self.playAudioBtn = QtWidgets.QPushButton()  # Store as class attribute
        self.playAudioBtn.setIcon(QtGui.QIcon(r"resources\image\play.png"))  # Replace with your play image file
        self.playAudioBtn.setIconSize(QtCore.QSize(50, 50))
        self.playAudioBtn.setFixedSize(70, 70)
        if is_send:
            self.playAudioBtnSend = self.playAudioBtn
            self.playAudioBtn.clicked.connect(lambda: self.playAudio(is_send=True))
        else:
            self.playAudioBtnReceive = self.playAudioBtn
            self.playAudioBtn.clicked.connect(lambda: self.playAudio(is_send=False))
        controlsLayout.addWidget(self.playAudioBtn)

        # Skip forward button
        self.skipForwardBtn = QtWidgets.QPushButton()  # Store as class attribute
        self.skipForwardBtn.setIcon(QtGui.QIcon(r"resources\image\fw5.png"))  # Replace with your image file
        self.skipForwardBtn.setIconSize(QtCore.QSize(30, 30))
        self.skipForwardBtn.setFixedSize(50, 50)
        self.skipForwardBtn.clicked.connect(lambda: self.skipAudio(5000, is_send))
        controlsLayout.addWidget(self.skipForwardBtn)

        controlFrameLayout.addLayout(controlsLayout)
        layout.addWidget(controlFrame)

        # Path display layout
        audioPathLayout = QtWidgets.QHBoxLayout()
        audioPathLineEdit = QtWidgets.QLineEdit()
        audioPathLineEdit.setReadOnly(True)
        audioPathLineEdit.setFixedHeight(30)
        audioPathLineEdit.setPlaceholderText("Audio file path...")
        audioPathLayout.addWidget(audioPathLineEdit)

        browseAudioBtn = QtWidgets.QPushButton("Browse Audio")
        browseAudioBtn.setFixedSize(150, 30)
        browseAudioBtn.clicked.connect(lambda: self.load_file_send() if is_send else self.load_file_receive())
        audioPathLayout.addWidget(browseAudioBtn)
        layout.addLayout(audioPathLayout)

        if is_send:
            self.audioPathLineEditSend = audioPathLineEdit
            self.audioPlayerSend = QMediaPlayer()
            self.audioOutputSend = QAudioOutput()
            self.audioPlayerSend.setAudioOutput(self.audioOutputSend)
            self.audioPlayerSend.positionChanged.connect(lambda pos: self.updateSlider(pos, is_send=True))
            self.audioPlayerSend.durationChanged.connect(lambda dur: self.updateSliderRange(dur, is_send=True))
        else:
            self.audioPathLineEditReceive = audioPathLineEdit
            self.audioPlayerReceive = QMediaPlayer()
            self.audioOutputReceive = QAudioOutput()
            self.audioPlayerReceive.setAudioOutput(self.audioOutputReceive)
            self.audioPlayerReceive.positionChanged.connect(lambda pos: self.updateSlider(pos, is_send=False))
            self.audioPlayerReceive.durationChanged.connect(lambda dur: self.updateSliderRange(dur, is_send=False))

        return layout



    def skipAudio(self, milliseconds, is_send):
        player = self.audioPlayerSend if is_send else self.audioPlayerReceive
        new_position = max(0, player.position() + milliseconds)
        player.setPosition(new_position)


    def playAudio(self, is_send):
        player = self.audioPlayerSend if is_send else self.audioPlayerReceive
        playBtn = self.playAudioBtnSend if is_send else self.playAudioBtnReceive

        # Check if the audio is playing
        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.pause()
            playBtn.setIcon(QtGui.QIcon(r"resources\image\play.png"))  # Set Play icon
        else:
            # Check if the file path is set
            current_file = self.audioPathLineEditSend.text() if is_send else self.audioPathLineEditReceive.text()
            
            if current_file:
                # If the audio is paused, resume from the current position
                if player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                    player.play()  # Simply resume playback
                    playBtn.setIcon(QtGui.QIcon(r"resources\image\pause.png"))  # Set Pause icon
                else:
                    # Set the audio source and start playback from the beginning
                    player.setSource(QUrl.fromLocalFile(current_file))
                    player.play()
                    playBtn.setIcon(QtGui.QIcon(r"resources\image\pause.png"))  # Set Pause icon
    
    def updateSlider(self, position, is_send):
        slider = self.audioSliderSend if is_send else self.audioSliderReceive
        slider.setValue(position)

    def updateSliderRange(self, duration, is_send):
        slider = self.audioSliderSend if is_send else self.audioSliderReceive
        slider.setRange(0, duration)
        slider.setEnabled(True)

    def setPlaybackPosition(self, position, is_send):
        player = self.audioPlayerSend if is_send else self.audioPlayerReceive
        player.setPosition(position)

    def createSendTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Key input and Generate Key button
        keyLayout = QHBoxLayout()

        keyLabel = QLabel("Key: ")
        keyLabel.setStyleSheet("font-size: 18px; font-weight: bold;")  # Tăng kích thước font và làm đậm chữ
        keyLayout.addWidget(keyLabel)

        self.key1Input = QLineEdit()
        self.key1Input.setPlaceholderText("Key: ")
        self.key1Input.setFixedHeight(30)
        keyLayout.addWidget(self.key1Input)

        layout.addLayout(keyLayout)

        # Horizontal line after Key section
        keyDivider = QtWidgets.QFrame()
        keyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        keyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        keyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        layout.addWidget(keyDivider)

        # Horizontal layout to divide into two sections
        horizontalLayout = QHBoxLayout()

        # Left Section: Secret message
        messageLayout = QVBoxLayout()
        leftFrame = QtWidgets.QFrame()
        leftFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        leftFrameLayout = QVBoxLayout(leftFrame)

        messageLabel = QLabel("Secret File (Only Image or Text file):")
        messageLabel.setStyleSheet("border: none;")
        leftFrameLayout.addWidget(messageLabel)

        # Trong createSendTab
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setFixedHeight(410)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px; background-color: white;")
        self.sendMessageBox = QLabel()  # Đổi tên thành sendMessageBox
        self.sendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        scrollArea.setWidget(self.sendMessageBox)
        leftFrameLayout.addWidget(scrollArea)

        pathLayout = QHBoxLayout()
        self.filePathLineEdit = QLineEdit()
        self.filePathLineEdit.setReadOnly(True)
        self.filePathLineEdit.setPlaceholderText("Image or text file path...")
        self.filePathLineEdit.setFixedHeight(30)
        pathLayout.addWidget(self.filePathLineEdit)

        self.browsefileBtn = QPushButton("Browse file")
        self.browsefileBtn.setFixedSize(150, 30)
        self.browsefileBtn.clicked.connect(self.load_image)
        pathLayout.addWidget(self.browsefileBtn)
        leftFrameLayout.addLayout(pathLayout)
        leftFrameLayout.addStretch()
        messageLayout.addWidget(leftFrame)

        # Right Section: Audio
        audioLayout = QVBoxLayout()
        rightFrame = QtWidgets.QFrame()
        rightFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        rightFrameLayout = QVBoxLayout(rightFrame)

        audioLabelTitle = QLabel("Audio file:")
        audioLabelTitle.setStyleSheet("border: none;")
        rightFrameLayout.addWidget(audioLabelTitle)

        # Directly add the audio widget
        audioPlayerLayout = self.createAudioWidget(is_send=True)
        rightFrameLayout.addLayout(audioPlayerLayout)

        rightFrameLayout.addStretch()
        audioLayout.addWidget(rightFrame)


        horizontalLayout.addLayout(messageLayout)
        horizontalLayout.addLayout(audioLayout)

        layout.addLayout(horizontalLayout)

        # Horizontal line after Key section
        keyDivider = QtWidgets.QFrame()
        keyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        keyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        keyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        layout.addWidget(keyDivider)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.encodeBtn = QPushButton("Encode")
        self.encodeBtn.setStyleSheet("margin-top: 10px;")
        self.encodeBtn.setFixedSize(200, 50)
        self.encodeBtn.setEnabled(False)
        self.encodeBtn.clicked.connect(self.encodeMessage)
        buttonLayout.addWidget(self.encodeBtn)

        layout.addLayout(buttonLayout)
        tab.setLayout(layout)
        return tab

    def createReceiveTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Prime inputs
        primeLayout = QHBoxLayout()

        prime1InputLabel = QLabel("Key: ")
        prime1InputLabel.setStyleSheet("font-size: 18px; font-weight: bold;")  # Tăng kích thước font và làm đậm chữ
        primeLayout.addWidget(prime1InputLabel)

        self.prime1Input = QLineEdit()
        self.prime1Input.setPlaceholderText("Key: ")
        self.prime1Input.setFixedHeight(30)
        primeLayout.addWidget(self.prime1Input)

        layout.addLayout(primeLayout)

        # Horizontal line after Key section
        keyDivider = QtWidgets.QFrame()
        keyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        keyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        keyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        layout.addWidget(keyDivider)


        # Horizontal layout to divide into two sections
        horizontalLayout1 = QHBoxLayout()

        # Right Section: Secret message
        messageLayout = QVBoxLayout()
        rightFrame = QtWidgets.QFrame()
        rightFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        rightFrameLayout = QVBoxLayout(rightFrame)

        messageLabel = QLabel("Secret File:")
        messageLabel.setStyleSheet("border: none;")
        rightFrameLayout.addWidget(messageLabel)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setFixedHeight(410)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet("border: 1px solid black; border-radius: 10px; margin-bottom: 5px; background-color: white;")
        self.receiveMessageBox = QLabel()  # Đổi tên thành receiveMessageBox
        self.receiveMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        scrollArea.setWidget(self.receiveMessageBox)
        rightFrameLayout.addWidget(scrollArea)

        pathLayout = QHBoxLayout()
        
        self.browsefileBtn = QPushButton("Save file")
        self.browsefileBtn.setFixedSize(150, 30)
        self.browsefileBtn.clicked.connect(self.save)
        pathLayout.addWidget(self.browsefileBtn)
        rightFrameLayout.addLayout(pathLayout)
        rightFrameLayout.addStretch()
        messageLayout.addWidget(rightFrame)

        # left Section: Audio
        audioLayout = QVBoxLayout()
        leftFrame = QtWidgets.QFrame()
        leftFrame.setStyleSheet("border: 1px solid black; border-radius: 10px;")
        leftFrameLayout = QVBoxLayout(leftFrame)

        audioLabelTitle = QLabel("Audio Encoded file:")
        audioLabelTitle.setStyleSheet("border: none;")
        leftFrameLayout.addWidget(audioLabelTitle)

        # Directly add the audio widget
        audioPlayerLayout = self.createAudioWidget(is_send=False)
        leftFrameLayout.addLayout(audioPlayerLayout)

        leftFrameLayout.addStretch()
        audioLayout.addWidget(leftFrame)

        horizontalLayout1.addLayout(audioLayout)
        horizontalLayout1.addLayout(messageLayout)

        layout.addLayout(horizontalLayout1)

        # Horizontal line after Key section
        keyDivider = QtWidgets.QFrame()
        keyDivider.setStyleSheet("border: 2px solid rgb(165, 213, 255);")
        keyDivider.setFrameShape(QtWidgets.QFrame().Shape.HLine)
        keyDivider.setFrameShadow(QtWidgets.QFrame().Shadow.Sunken)
        layout.addWidget(keyDivider)

        # Buttons in a row
        buttonLayout2 = QHBoxLayout()

        self.decodeBtn = QPushButton("Decode")
        self.decodeBtn.setStyleSheet("margin-top: 10px;")
        self.decodeBtn.setFixedSize(200, 50)
        self.decodeBtn.setEnabled(False)
        self.decodeBtn.clicked.connect(self.decodeMessage)

        buttonLayout2.addWidget(self.decodeBtn)
        layout.addLayout(buttonLayout2)

        tab.setLayout(layout)
        return tab


    def applyGlobalFont(self, widget):
        font = QtGui.QFont("Arial", 12)
        for child in widget.findChildren((QLabel, QLineEdit, QTextEdit)):
            child.setFont(font)


    def load_image(self):
        # Open file dialog to select files (images and text files)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.centralwidget,
            "Open File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;Text Files (*.txt)",
        )

        if file_path:
            self.filePathLineEdit.setText(file_path)  # Display file path
            self.sendMessageBox.clear()  # Sử dụng sendMessageBox

            if file_path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                # Display image
                pixmap = QtGui.QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        400, 300, QtCore.Qt.AspectRatioMode.KeepAspectRatio
                    )
                    self.sendMessageBox.setPixmap(pixmap)  # Sử dụng sendMessageBox
                    self.sendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                else:
                    self.sendMessageBox.setText("Invalid image file.")  # Sử dụng sendMessageBox
            elif file_path.lower().endswith(".txt"):
                # Display text content
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        text_content = file.read()
                    if not text_content.strip():
                        raise ValueError("File is empty.")
                    self.sendMessageBox.setPixmap(QtGui.QPixmap())  # Sử dụng sendMessageBox
                    self.sendMessageBox.setText(text_content)
                    self.sendMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                    self.sendMessageBox.setWordWrap(True)
                except Exception as e:
                    self.sendMessageBox.setText(f"Error reading file: {str(e)}")  # Sử dụng sendMessageBox


    def save(self):
        # Mở hộp thoại để chọn vị trí và tên file lưu
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.centralwidget,
            "Save File",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            # Lấy nội dung hiện tại trong receiveMessageBox
            content = self.receiveMessageBox.text()
            if not content.strip():
                qmb_custom("Error", "No content to save.")
                return
            
            try:
                # Ghi nội dung vào file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                qmb_custom("Success", "File saved successfully!")
            except Exception as e:
                qmb_custom("Error", f"Failed to save file: {str(e)}")

    def load_file_send(self):
        sender_fname, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Audio File", "", "Audio Files (*.wav)")
        if sender_fname:
            self.audioPathLineEditSend.setText(sender_fname)
            self.encodeBtn.setEnabled(True)
            
    def load_file_receive(self):
        receiver_fname, _ = QtWidgets.QFileDialog.getOpenFileName(self.centralwidget, "Open Audio File", "", "Audio Files (*.wav)")
        if receiver_fname:
            self.audioPathLineEditReceive.setText(receiver_fname)
            self.decodeBtn.setEnabled(True)

    def generate_aes_256_key(self, strPasswd):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(strPasswd.encode('utf-8'))
        return bytes.fromhex(sha256_hash.hexdigest())

    def encodeMessage(self):
        passwd = self.key1Input.text()
        if not passwd:
            qmb_custom("Error", "Please enter a password")
            return

        # Sinh khóa AES-256 từ mật khẩu nhập vào
        key = self.generate_aes_256_key(passwd)

        # Lấy đường dẫn đến tệp
        filePath = self.filePathLineEdit.text()

        # Kiểm tra loại tệp và xử lý
        try:
            with open(filePath, 'rb') as file:
                fileContent = file.read()

            if filePath.endswith(('.png', '.jpg', '.jpeg')):
                # Nếu là hình ảnh
                message = b'1' + fileContent
            elif filePath.endswith('.txt'):
                with open(filePath, 'r', encoding='utf-8') as textFile:
                    textContent = textFile.read()
                message = b'0' + textContent.encode('utf-8')
            else:
                qmb_custom("Error", "Unsupported file type")
                return

            # Mã hóa thông điệp và lưu
            encrypted = Sender.send_msg(message, key)
            encode(self.audioPathLineEditSend.text(), encrypted)
            qmb_custom("Success", "Message encoded successfully")
        except Exception as e:
            print(e)


    def decodeMessage(self):
        passwd = self.prime1Input.text()
        if not passwd:
            qmb_custom("Error", "Please enter a password")
            return

        key = self.generate_aes_256_key(passwd)
        encoded = decode(self.audioPathLineEditReceive.text())
        decoded = receiver.message_read(encoded, key)

        if decoded:
            flag = decoded[0]
            decoded = decoded[1:]
            if flag == 50:  # Flag for text
                middle = bytes.fromhex('9999')
                position = decoded.find(middle)
                textMessage = decoded[:position]
                self.receiveMessageBox.setPixmap(QtGui.QPixmap())  # Sử dụng sendMessageBox
                self.receiveMessageBox.setText(textMessage.decode('utf-8'))  # Display text in scrollArea
                self.receiveMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                self.receiveMessageBox.setWordWrap(True)
                qmb_custom("Decoded Message", "Text message decoded successfully!")
            elif flag == 49:  # Flag for image
                # Load and display the image in the scrollArea
                pixmap = QtGui.QPixmap()
                if pixmap.loadFromData(decoded):

                    self.receiveMessageBox.setPixmap(pixmap.scaled(
                        400,300,
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    ))
                    self.receiveMessageBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    qmb_custom("Success", "Image decoded and displayed successfully!")
                else:
                    qmb_custom("Error", "Failed to display the image.")
            else:
                self.receiveMessageBox.setText(decoded.decode('utf-8'))  # Fallback for other text formats
                qmb_custom("Decoded Message", "Message decoded successfully!")



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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Audio()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
