import math
import os
from Crypto.Cipher import AES
from tkinter import messagebox

from PyQt6 import QtWidgets

class receiver():
    @staticmethod
    def message_read(encrypted_message: bytes, key: bytes):
    # Tách nonce, tag và ciphertext từ dữ liệu đã mã hóa
        nonce = encrypted_message[:12]
        tag = encrypted_message[12:28]
        ciphertext = encrypted_message[28:]
        
        # print(f"key: {key.hex()}")
        # print(f"encrypted: {encrypted_message.hex()}")

        # Khởi tạo đối tượng AES với nonce và tag
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # print(f"Ciphertext: {ciphertext.hex()}")
        # print(f"Nonce: {nonce.hex()}")
        # print(f"Tag: {tag.hex()}")

        # Giải mã và kiểm tra tính toàn vẹn
        try:
            decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted_message
        except:
            qmb_custom("Notification", "Incorrect password")
            return None
        
def qmb_custom(string1, string2):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle(string1)
    msg_box.setText(string2)
    # Thiết lập StyleSheet để căn giữa văn bản
    msg_box.setStyleSheet(
        "QLabel{font: 15pt \"Berlin Sans FB\"; min-height:150 px; min-width: 400px;} QPushButton{ width:100px; height:30px; border-radius: 5px; font: 75 14pt \"Berlin Sans FB Demi\"; background-color: rgb(165, 213, 255);} QPushButton:hover{background-color: rgb(3, 105, 161); color: rgb(255,255,255);}"
        )
    msg_box.exec()