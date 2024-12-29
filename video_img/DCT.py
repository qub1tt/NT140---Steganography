import os
import xlwt
import shutil
import cv2
import sys
import math
import numpy as np
import itertools
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from scipy import signal
from Crypto.Cipher import AES

quant = np.array([[16,11,10,16,24,40,51,61],      # QUANTIZATION TABLE
                    [12,12,14,19,26,58,60,55],    # required for DCT
                    [14,13,16,24,40,57,69,56],
                    [14,17,22,29,51,87,80,62],
                    [18,22,37,56,68,109,103,77],
                    [24,35,55,64,81,104,113,92],
                    [49,64,78,87,103,121,120,101],
                    [72,92,95,98,112,100,103,99]])

def msg_encrypt(msg,cipher):
    if (len(msg)%16 != 0):
        #a = len(msg)%16 != 0 
        #print(a)
        msg = msg + ' '*(16 - len(msg)%16)
    #nonce = cipher.nonce
    t1 = msg.encode()
    enc_msg = cipher.encrypt(t1)
    return enc_msg

def msg_decrypt(ctext,cipher):
    dec_msg = cipher.decrypt(ctext)
    msg1 = dec_msg.decode()
    return msg1

class DCT():    
    def __init__(self): # Constructor
        self.message = None
        self.bitMess = None
        self.oriCol = 0
        self.oriRow = 0
        self.numBits = 0   
    #encoding part : 
    def encode_image(self,img,secret_msg):
        self.message = str(len(secret_msg)).encode()+b'*'+secret_msg
        #get the size of the image in pixels
        row, col = img.shape[:2]
        if((col/8)*(row/8)<len(secret_msg)):
            print("Error: Message too large to encode in image")
            return False
        if row%8 or col%8:
            img = self.addPadd(img,row,col)
        row,col = img.shape[:2]
        #split image into RGB channels
        hImg,sImg,vImg = cv2.split(img)
        #message to be hid in saturation channel so converted to type float32 for dct function
        #print(bImg.shape)
        sImg = np.float32(sImg)
        #breaking the image into 8x8 blocks
        imgBlocks = [np.round(sImg[j:j+8,i:i+8]-128) for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        #print('imgBlocks',imgBlocks[0])
        #blocks are run through dct / apply dct to it
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        print('imgBlocks', imgBlocks[0])
        print('dctBlocks', dctBlocks[0])
        #blocks are run through quantization table / obtaining quantized dct coefficients
        quantDCT = dctBlocks
        print('quantDCT', quantDCT[0])
        #set LSB in DC value corresponding bit of message
        messIndex=0
        letterIndex=0
        print(self.message)
        for qb in quantDCT:
            #find LSB in DCT cofficient and replace it with message bit
            bit = (self.message[messIndex] >> (7-letterIndex)) & 1
            DC = qb[0][0]
            #print(DC)
            DC = (int(DC) & ~31) | (bit * 15)
            #print(DC)
            qb[0][0] = np.float32(DC)
            letterIndex += 1
            if letterIndex == 8:
                letterIndex = 0
                messIndex += 1
                if messIndex == len(self.message):
                    break
        #writing the stereo image
        #blocks run inversely through quantization table
        #blocks run through inverse DCT
        sImgBlocks = [cv2.idct(B)+128 for B in quantDCT]
        #puts the new image back together
        aImg=[]
        for chunkRowBlocks in self.chunks(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    aImg.extend(block[rowBlockNum])
        aImg = np.array(aImg).reshape(row, col)
        #converted from type float32
        aImg = np.uint8(aImg)
        #show(sImg)
        return cv2.merge((hImg,aImg,vImg))

    #decoding part :
    def decode_image(self,img):
        row, col = img.shape[:2]
        messSize = None
        messageBits = []
        buff = 0
        #split the image into RGB channels
        hImg,sImg,vImg = cv2.split(img)
        #message hid in saturation channel so converted to type float32 for dct function
        sImg = np.float32(sImg)
        #break into 8x8 blocks
        imgBlocks = [sImg[j:j+8,i:i+8]-128 for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        # the blocks are run through quantization table
        print('imgBlocks',imgBlocks[0])
        print('dctBlocks',dctBlocks[0])
        quantDCT = dctBlocks
        i=0
        flag = 0
        #message is extracted from LSB of DCT coefficients
        for qb in quantDCT:
            if qb[0][0] > 0:
                DC = int((qb[0][0]+7)/16) & 1
            else:
                DC = int((qb[0][0]-7)/16) & 1
            #print('qb',qb[0][0],'dc',DC)
            #unpacking of bits of DCT
            buff += DC << (7-i)
            i += 1
            #print(i)
            if i == 8:
                messageBits.append(buff)
                #print(buff,end=' ')
                buff = 0
                i =0
                if messageBits[-1] == 42 and not messSize:
                    try:
                        messSize = chr(messageBits[0])
                        for j in range(1,len(messageBits)-1):
                            messSize += chr(messageBits[j])
                        messSize = int(messSize)
                        print(messSize,'a')
                    except:
                        print('b')
            if len(messageBits) - len(str(messSize)) - 1 == messSize:
                return messageBits
        print("msgbits", messageBits)
        return None
      
    """Helper function to 'stitch' new image back together"""
    def chunks(self, l, n):
        m = int(n)
        for i in range(0, len(l), m):
            yield l[i:i + m]
    def addPadd(self,img, row, col):
        img = cv2.resize(img,(col+(8-col%8),row+(8-row%8)))    
        return img
    
    def toBits(self):
        bits = []
        for char in self.message:
            binval = bin(ord(char))[2:].rjust(8,'0')
            bits.append(binval)
        self.numBits = bin(len(bits))[2:].rjust(8,'0')
        return bits

class LSB():
    #encoding part :
    def encode_image(self,img, msg):
        length = len(msg)
        if length > 255:
            print("text too long! (don't exeed 255 characters)")
            return False
        encoded = img.copy()
        width, height = img.size
        index = 0
        for row in range(height):
            for col in range(width):
                if img.mode != 'RGB':
                    r, g, b ,a = img.getpixel((col, row))
                elif img.mode == 'RGB':
                    r, g, b = img.getpixel((col, row))
                # first value is length of msg
                if row == 0 and col == 0 and index < length:
                    asc = length
                elif index <= length:
                    c = msg[index -1]
                    asc = ord(c)
                else:
                    asc = b
                encoded.putpixel((col, row), (r, g , asc))
                index += 1
        return encoded

    #decoding part :
    def decode_image(self,img):
        width, height = img.size
        msg = ""
        index = 0
        for row in range(height):
            for col in range(width):
                if img.mode != 'RGB':
                    r, g, b ,a = img.getpixel((col, row))
                elif img.mode == 'RGB':
                    r, g, b = img.getpixel((col, row))  
                # first pixel r value is length of message
                if row == 0 and col == 0:
                    length = b
                elif index <= length:
                    msg += chr(b)
                index += 1
        lsb_decoded_image_file = "lsb_" + original_image_file
        #img.save(lsb_decoded_image_file)
        ##print("Decoded image was saved!")
        return msg




class Compare():
    def correlation(self, img1, img2):
        return signal.correlate2d (img1, img2)
    
    def meanSquareError(self, img1, img2):
        if img1.shape != img2.shape:
            print(f"Dimension mismatch: Original {img1.shape}, Encoded {img2.shape}")
            img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
        error = np.sum((img1.astype('float') - img2.astype('float')) ** 2)
        error /= float(img1.shape[0] * img1.shape[1])
        return error
    
    def psnr(self, img1, img2):
        mse = self.meanSquareError(img1,img2)
        if mse == 0:
            return 100
        PIXEL_MAX = 255.0
        return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))



#driver part :
#deleting previous folders :
if os.path.exists("Encoded_image/"):
    shutil.rmtree("Encoded_image/")
if os.path.exists("Decoded_output/"):
    shutil.rmtree("Decoded_output/")
if os.path.exists("Comparison_result/"):
    shutil.rmtree("Comparison_result/")
#creating new folders :
os.makedirs("Encoded_image/")
os.makedirs("Decoded_output/")
os.makedirs("Comparison_result/")
original_image_file = ""    # to make the file name global variable
lsb_encoded_image_file = ""
dct_encoded_image_file = ""
pvd_encoded_image_file = ""


while True:
    m = input("To encode press '1', to decode press '2', to compare press '3', press any other button to close: ")

    if m == "1":
        os.chdir("Original_image/")
        original_image_file = input("Enter the name of the file with extension : ")
        lsb_img = Image.open(original_image_file)
        dct_img = cv2.imread(original_image_file, cv2.IMREAD_UNCHANGED)
#        dwt_img = cv2.imread(original_image_file, cv2.IMREAD_UNCHANGED)
        print("Description : ",lsb_img,"\nMode : ", lsb_img.mode)
        secret_msg = input("Enter the message you want to hide: ")
        print("The message length is: ",len(secret_msg))
        os.chdir("..")
        os.chdir("Encoded_image/")

        key = b'Sixteen byte key'
        cipher = AES.new(key,AES.MODE_ECB)
        enc_msg = msg_encrypt(secret_msg,cipher)

        lsb_img_encoded = LSB().encode_image(lsb_img, secret_msg)
        dct_img_encoded = DCT().encode_image(dct_img, enc_msg)
#        dwt_img_encoded = DWT().encode_image(dwt_img, secret_msg)
        lsb_encoded_image_file = "lsb_" + original_image_file
        lsb_img_encoded.save(lsb_encoded_image_file)
        dct_encoded_image_file = "dct_" + original_image_file
        cv2.imwrite(dct_encoded_image_file,dct_img_encoded)
#        dwt_encoded_image_file = "dwt_" + original_image_file
#        cv2.imwrite(dwt_encoded_image_file,dwt_img_encoded) # saving the image with the hidden text
        print("Encoded images were saved!")
        os.chdir("..")

    elif m == "2":
        os.chdir("Encoded_image/")
        lsb_img = Image.open(lsb_encoded_image_file)
        dct_img = cv2.imread(dct_encoded_image_file, cv2.IMREAD_UNCHANGED)
#        dwt_img = cv2.imread(dwt_encoded_image_file, cv2.IMREAD_UNCHANGED)
        os.chdir("..") #going back to parent directory
        os.chdir("Decoded_output/")
        key = b'Sixteen byte key'
        cipher = AES.new(key,AES.MODE_ECB)

        lsb_hidden_text = LSB().decode_image(lsb_img)
        dct_hidden_text = DCT().decode_image(dct_img) 

        a = dct_hidden_text.index(42)
        decoded = bytes(dct_hidden_text[a+1:])
        text = msg_decrypt(decoded,cipher)

#        dwt_hidden_text = DWT().decode_image(dwt_img) 
        file = open(r"lsb_hidden_text.txt","w")
        file.write(lsb_hidden_text) # saving hidden text as text file
        file.close()
        file = open(r"dct_hidden_text.txt","w")
        file.write(text) # saving hidden text as text file
        file.close()
#        file = open("dwt_hidden_text.txt","w")
#        file.write(dwt_hidden_text) # saving hidden text as text file
#        file.close()
        print("Hidden texts were saved as text file!")
        os.chdir("..")
    elif m == "3":
        #comparison calls
        os.chdir("Original_image/")
        original = cv2.imread(original_image_file)
        os.chdir("..")
        os.chdir("Encoded_image/")
        lsbEncoded = cv2.imread(lsb_encoded_image_file)
        dctEncoded = cv2.imread(dct_encoded_image_file)
#        dwtEncoded = cv2.imread(dwt_encoded_image_file)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        lsb_encoded_img = cv2.cvtColor(lsbEncoded, cv2.COLOR_BGR2RGB)
        dct_encoded_img = cv2.cvtColor(dctEncoded, cv2.COLOR_BGR2RGB)
#        dwt_encoded_img = cv2.cvtColor(dwtEncoded, cv2.COLOR_BGR2RGB)
        os.chdir("..")
        os.chdir("Comparison_result/")

        book = xlwt.Workbook()
        sheet1=book.add_sheet("Sheet 1")
        style_string = "font: bold on , color red; borders: bottom dashed"
        style = xlwt.easyxf(style_string)
        sheet1.write(0, 0, "Original vs", style=style)
        sheet1.write(0, 1, "MSE", style=style)
        sheet1.write(0, 2, "PSNR", style=style)
        sheet1.write(1, 0, "LSB")
        sheet1.write(1, 1, Compare().meanSquareError(original, lsb_encoded_img))
        sheet1.write(1, 2, Compare().psnr(original, lsb_encoded_img))
        sheet1.write(2, 0, "DCT")
        sheet1.write(2, 1, Compare().meanSquareError(original, dct_encoded_img))
        sheet1.write(2, 2, Compare().psnr(original, dct_encoded_img))
        sheet1.write(3, 0, "DWT")
#        sheet1.write(3, 1, Compare().meanSquareError(original, dwt_encoded_img))
#        sheet1.write(3, 2, Compare().psnr(original, dwt_encoded_img))

        book.save("Comparison.xls")
        print("Comparison Results were saved as xls file!")
        os.chdir("..")
    else:
        print("Closed!")
        break