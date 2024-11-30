from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt

class Sender():
    # def __init__(self):
    #     pass
    # def ask_to_send(self):
    #     with open('message.txt' , 'w') as f:
    #         f.write('SEND')
    #         f.close()

    @staticmethod
    def send_msg(message: bytes, key: bytes):

        nonce = get_random_bytes(12)
    
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        ciphertext, tag = cipher.encrypt_and_digest(message)
        # print(f"Ciphertext: {ciphertext.hex()}")
        # print(f"Nonce: {nonce.hex()}")
        # print(f"Tag: {tag.hex()}")
        return nonce + tag + ciphertext


    