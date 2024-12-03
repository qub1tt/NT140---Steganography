import math
import os
from Crypto.Cipher import AES
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
        decrypted_message = cipher.decrypt_and_verify(ciphertext, tag)
        
        return decrypted_message