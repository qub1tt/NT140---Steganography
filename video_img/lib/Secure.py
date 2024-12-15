from lib.Crypt import Crypt
from lib.Stego import Stego
from multipledispatch import dispatch
import os

class Secure:

    def __init__(self):
        self.crypt = Crypt()
        self.stego = Stego()

    # @dispatch(str)
    # def secure_file(self, f):
    #     f = self.crypt.encrypt_file(f)
    #     self.stego.stego(f)

    # @dispatch(str, str)
    # def secure_file(self, f, coverImg):
    #     f = self.crypt.encrypt_file(f)
    #     self.stego.stego(f, coverImg)

    @dispatch(str, str)
    def secure_file(self, f, pw):
        f = self.crypt.encrypt_file(f, pw)
        self.stego.stego(f)

    @dispatch(str, str, str)
    def secure_file(self, f, coverImg, pw):
        f = self.crypt.encrypt_file(f, pw)
        self.stego.stego(f, coverImg)

    @dispatch(str)
    def secure_file_video(self, f):
        f = self.crypt.encrypt_file(f)
        self.stego.stegoVideo(f)

    @dispatch(str, str)
    def secure_file_video(self, f, coverVideo):
        f = self.crypt.encrypt_file(f)
        self.stego.stegoVideo(f, coverVideo)

    # def desecure_file(self, stegoImgFile, outputFile="lib/output/decrypted.txt"):
    #     outputFile += ".enc"
    #     self.stego.unStego(stegoImgFile, outputFile)
    #     self.crypt.decrypt_file(outputFile)


    def desecure_file(self, stegoImgFile, password):
        """
        Giải mã file chứa dữ liệu được nhúng (stegoImgFile)
        và trả về nội dung dữ liệu đã giải mã.
        """
        # Trích xuất dữ liệu được nhúng
        embeddedFile = "temp_output.enc"  # File tạm thời để lưu dữ liệu đã trích xuất
        self.stego.unStego(stegoImgFile, embeddedFile)
        # Giải mã file đã trích xuất
        try:
            with open(embeddedFile, 'rb') as fo:
                ciphertext = fo.read()
            os.remove(embeddedFile)  # Xóa file tạm thời ngay sau khi đọc
        except FileNotFoundError:
            print(f"File {embeddedFile} not found!")
            return None
        # Tạo khóa AES từ mật khẩu
        key = self.crypt.derive_key(password)
        # Giải mã nội dung
        try:
            decrypted_data = self.crypt.decrypt(ciphertext, key)
        except ValueError:
            #print("Decryption failed! Incorrect password or file integrity compromised.")
            return None
        #print("File successfully decrypted!")
        return decrypted_data


    def desecure_file_video(self, stegoVideoFile, outputFile="lib/output/decrypted.txt"):
        outputFile += ".enc"
        self.stego.unStegoVideo(stegoVideoFile, outputFile)
        self.crypt.decrypt_file(outputFile)
