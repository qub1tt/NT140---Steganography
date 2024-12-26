from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class Crypt:
    def __init__(self):
        self.key = None

    @staticmethod
    def derive_key(password):
        """Tạo khóa AES 16 byte từ mật khẩu bằng SHA-256."""
        return hashlib.sha256(password.encode()).digest()
    
    def encrypt(self, message, key):
        """Mã hóa dữ liệu bằng AES-GCM."""
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(message)
        return cipher.nonce + tag + ciphertext  # Kết hợp nonce, tag và ciphertext

    def decrypt(self, ciphertext, key):
        """Giải mã dữ liệu bằng AES-GCM."""
        nonce = ciphertext[:16]  # Nonce có độ dài 16 byte
        tag = ciphertext[16:32]  # Tag có độ dài 16 byte
        encrypted_message = ciphertext[32:]  # Ciphertext bắt đầu từ byte thứ 32
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(encrypted_message, tag)  # Giải mã và xác thực

    # def encrypt_file(self, file_name):
    #     """Mã hóa tệp tin."""
    #     try:
    #         with open(file_name, 'rb') as fo:
    #             plaintext = fo.read()
    #     except FileNotFoundError:
    #         print(f"File {file_name} not found!")
    #         return

    #     # Yêu cầu mật khẩu từ người dùng
    #     passW = input(f"Set password for [{file_name}]: ")
    #     self.key = self.derive_key(passW)

    #     # Mã hóa nội dung file
    #     enc = self.encrypt(plaintext, self.key)

    #     # Lưu tệp mã hóa
    #     newF = file_name + ".enc"
    #     with open(newF, 'wb') as fo:
    #         fo.write(enc)
    #     print("\nFile Encrypted!")

    #     return newF

    def encrypt_file(self, file_name, pw):
        """Mã hóa tệp tin."""
        try:
            with open(file_name, 'rb') as fo:
                plaintext = fo.read()
        except FileNotFoundError:
            #print(f"File {file_name} not found!")
            return

        # Yêu cầu mật khẩu từ người dùng
        passW = pw
        self.key = self.derive_key(passW)

        # Mã hóa nội dung file
        enc = self.encrypt(plaintext, self.key)

        # Lưu tệp mã hóa
        newF = file_name + ".enc"
        with open(newF, 'wb') as fo:
            fo.write(enc)

        return newF

    # def decrypt_file(self, file_name):
    #     """Giải mã tệp tin."""
    #     try:
    #         with open(file_name, 'rb') as fo:
    #             ciphertext = fo.read()
    #     except FileNotFoundError:
    #         print(f"File {file_name} not found!")
    #         return

    #     # Yêu cầu mật khẩu từ người dùng
    #     passW = input("File password: ")
    #     self.key = self.derive_key(passW)

    #     # Giải mã nội dung file
    #     try:
    #         dec = self.decrypt(ciphertext, self.key)
    #     except ValueError:
    #         print("Decryption failed! Incorrect password or file integrity compromised.")
    #         return

    #     # Lưu tệp đã giải mã
    #     op_file = file_name[:-4]  # Xóa phần mở rộng ".enc"
    #     with open(op_file, 'wb') as fo:
    #         fo.write(dec)
    #     os.remove(file_name)
    #     print("File fully Decrypted!!!")
    #     print(f"Decrypted file saved as: {op_file}")
    #     return op_file

    def decrypt_file(self, file_name, output_file, password):
        """Giải mã tệp tin với mật khẩu được cung cấp."""
        try:
            with open(file_name, 'rb') as fo:
                ciphertext = fo.read()
        except FileNotFoundError:
            #print(f"File {file_name} not found!")
            return

        # Tạo khóa AES từ mật khẩu
        self.key = self.derive_key(password)

        # Giải mã nội dung file
        try:
            dec = self.decrypt(ciphertext, self.key)
        except ValueError:
            # print("Decryption failed! Incorrect password or file integrity compromised.")
            alert("Error", "Incorrect Password")
            return

        # Lưu tệp đã giải mã
        with open(output_file, 'wb') as fo:
            fo.write(dec)

        os.remove(file_name)  # Xóa file tạm thời
        #print("File fully decrypted!")
        #print(f"Decrypted file saved as: {output_file}")
        return output_file

    @staticmethod
    def get_all_files():
        """Lấy danh sách tất cả các file trong thư mục hiện tại."""
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dirs = []
        for dirName, subdirList, fileList in os.walk(dir_path):
            for fname in fileList:
                dirs.append(dirName + "/" + fname)
        return dirs

    def encrypt_all_files(self):
        """Mã hóa tất cả các tệp tin trong thư mục."""
        dirs = self.get_all_files()
        for file_name in dirs:
            if not file_name.endswith('.enc'):  # Không mã hóa file đã được mã hóa
                self.encrypt_file(file_name)

    def decrypt_all_files(self):
        """Giải mã tất cả các tệp tin trong thư mục."""
        dirs = self.get_all_files()
        for file_name in dirs:
            if file_name.endswith('.enc'):  # Chỉ giải mã các file có đuôi '.enc'
                self.decrypt_file(file_name)

def alert(string1, string2):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(string1)
    msg_box.setText(string2)
    # Thiết lập StyleSheet để căn giữa văn bản
    msg_box.setStyleSheet(
        "QLabel{font: 15pt \"Berlin Sans FB\"; min-height:150 px; min-width: 400px;} QPushButton{ width:100px; height:30px; border-radius: 5px; font: 75 14pt \"Berlin Sans FB Demi\"; background-color: rgb(165, 213, 255);} QPushButton:hover{background-color: rgb(3, 105, 161); color: rgb(255,255,255);}"
        )
    msg_box.exec()