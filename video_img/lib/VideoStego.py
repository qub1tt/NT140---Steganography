from PIL import Image
import shutil, cv2, os
import numpy as np
import itertools
from PyQt6.QtWidgets import QFileDialog, QMessageBox

def chunks(l,n):
    m = int(n)
    for i in range(0,len(l),m):
        yield l[i:i+m]
#function to add padding to make the function dividable by 8x8 blocks
def addPadd(img,row,col):
    img = cv2.resize(img,(col+(8-col%8),row+(8-row%8)))
    return img

def encode_frame(img, secret):
    
    text_to_hide_open = open(secret, "rb")
    # text_to_hide = repr(text_to_hide_open.read())
    text_to_hide = text_to_hide_open.read()
    text_to_hide_open.close()

    secret = text_to_hide
    message = str(len(secret)).encode()+b'*'+secret
    #get the size of the image in pixels
    row, col = img.shape[:2]
    if((col/8)*(row/8)<len(secret)):
        #alert("Error","Message too large to encode in image")
        return False
    if row%8 or col%8:
        img = addPadd(img,row,col)
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
    # print('imgBlocks', imgBlocks[0])
    # print('dctBlocks', dctBlocks[0])
    #blocks are run through quantization table / obtaining quantized dct coefficients
    quantDCT = dctBlocks
    # print('quantDCT', quantDCT[0])
    #set LSB in DC value corresponding bit of message
    messIndex=0
    letterIndex=0
    for qb in quantDCT:
        #find LSB in DCT cofficient and replace it with message bit
        bit = (message[messIndex] >> (7-letterIndex)) & 1
        DC = qb[0][0]
        #print(DC)
        DC = (int(DC) & ~31) | (bit * 15)
        #print(DC)
        qb[0][0] = np.float32(DC)
        letterIndex += 1
        if letterIndex == 8:
            letterIndex = 0
            messIndex += 1
            if messIndex == len(message):
                break
    #writing the stereo image
    #blocks run inversely through quantization table
    #blocks run through inverse DCT
    sImgBlocks = [cv2.idct(B)+128 for B in quantDCT]
    #puts the new image back together
    aImg=[]
    for chunkRowBlocks in chunks(sImgBlocks, col/8):
        for rowBlockNum in range(8):
            for block in chunkRowBlocks:
                aImg.extend(block[rowBlockNum])
    aImg = np.array(aImg).reshape(row, col)
    #converted from type float32
    aImg = np.uint8(aImg)
    #show(sImg)
    return cv2.merge((hImg,aImg,vImg))


# def decode_frame(img, outputFile=r"C:\Users\lec37\OneDrive\Desktop\z.txt"):
def decode_frame(img, outputFile):
    row, col = img.shape[:2]
    messSize = None
    messageBits = []
    buff = 0
    msg = ""
    #split the image into RGB channels
    hImg,sImg,vImg = cv2.split(img)
    #message hid in saturation channel so converted to type float32 for dct function
    sImg = np.float32(sImg)
    #break into 8x8 blocks
    imgBlocks = [sImg[j:j+8,i:i+8]-128 for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
    dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
    # the blocks are run through quantization table
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
                    # print('b')
                    pass
        if len(messageBits) - len(str(messSize)) - 1 == messSize:
            msg = messageBits.index(42)
            msg = bytes(messageBits[msg+1:])

    # msg = str(msg[1:-1])
    # print(msg)
    if msg != "":
        recovered_txt = open(outputFile, "wb")
        recovered_txt.write(msg)
        recovered_txt.close()
        return msg
    
    return None

def alert(string1, string2):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(string1)
    msg_box.setText(string2)
    # Thiết lập StyleSheet để căn giữa văn bản
    msg_box.setStyleSheet(
        "QLabel{font: 15pt \"Berlin Sans FB\"; min-height:150 px; min-width: 400px;} QPushButton{ width:100px; height:30px; border-radius: 5px; font: 75 14pt \"Berlin Sans FB Demi\"; background-color: rgb(165, 213, 255);} QPushButton:hover{background-color: rgb(3, 105, 161); color: rgb(255,255,255);}"
        )
    msg_box.exec()