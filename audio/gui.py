from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from prime_number.Prime import Prime
from tkinter import messagebox
# from RSA.receiver import receiver
from AES.receiver import receiver
from steganography.decode_song import decode
# from RSA.sender import Sender
from AES.sender import Sender
from steganography.encode_song import encode
import re
import os
from PIL import Image
import io
from Crypto.Random import get_random_bytes
import hashlib

fname = None
decodeButton = None
sender_fname = None
encodeButton = None
fnameImage = None
isImageFile_sender = False
isImageFile_receiver = False

def generate_aes_256_key(strPasswd):
    # Tạo khóa AES 256-bit (32 bytes)
    # key = get_random_bytes(32)  # 32 bytes = 256 bits
    # keyEntry.delete(0, END)
    # keyEntry.insert(0, key.hex())
    sha256_hash = hashlib.sha256()
    sha256_hash.update(strPasswd.encode('utf-8'))
    hash_value = sha256_hash.hexdigest()
    return bytes.fromhex(hash_value)
    

def is_hex(s):
    # Kiểm tra chuỗi có phải là hex (gồm các ký tự 0-9 và a-f hoặc A-F)
    return bool(re.match(r'^[0-9a-fA-F]+$', s))


def encodeMessage(textBox, keyEntry):
    '''
    sends the message to the encode_song module
    '''
    passwd = keyEntry.get()
    if passwd == '':
        messagebox.showerror("Error", "Please enter a password")
        return
    key = generate_aes_256_key(passwd)
    global isImageFile_sender

    textMessage = textBox.get("1.0", END)

    if len(textMessage) != 1 and isImageFile_sender:
        textMessage = textMessage.encode('utf-8')

        imageMessage = load_file_image(fnameImage)

        middle = bytes.fromhex('9999')

        message = '2'.encode('utf-8') + textMessage + middle + imageMessage
    elif len(textMessage) == 1 and isImageFile_sender:
        imageMessage = load_file_image(fnameImage)
        message = '1'.encode('utf-8') + imageMessage
    else:
        message = '0'.encode('utf-8') + textMessage.encode('utf-8')


    
    encrypted = Sender.send_msg(message, key)
    # print(f"key: {key.hex()}")
    # print(f"encrypted: {encrypted.hex()}")
    encode(sender_fname, encrypted)
    isImageFile_sender = False


def addSendTab():
    '''
    adding the send tab in tkinter
    provides a text box for message
    and 2 entry box for the public key
    '''
    tab1.columnconfigure(0, weight=1)
    tab1.columnconfigure(1, weight=1)


    label1 = Label(tab1, text="Enter Password: ")
    label1.grid(row=1, column=0, pady=10)
    keyEntry = Entry(tab1, width=70, borderwidth=3)
    keyEntry.grid(row=1, column=1)

    # label2 = Label(tab1, text="Key 2")
    # label2.grid(row=0, column=2, pady=10)
    # key2Entry = Entry(tab1, width=20, borderwidth=3)
    # key2Entry.grid(row=1, column=2, padx=20)

    # generatekeyButton = Button(tab1, text="Password:", command = lambda: generate_aes_256_key(keyEntry))
    # generatekeyButton.grid(row=0, column=1, sticky="nsew", pady=10)

    textBox = Text(tab1, height=5, width=20)
    textBox.grid(row=5, column=0, columnspan=3, sticky="ew", padx=(50,50))

    encodeButton = Button(tab1, text="Encode", state=DISABLED, command= lambda: encodeMessage(textBox, keyEntry))
    encodeButton.grid(row=6, column=1, sticky="ew", pady=10)

    uploadAudioButton = Button(tab1, text="Browse Audio", command=lambda: load_file(encodeButton, keyEntry))
    uploadAudioButton.grid(row=3, column=1, sticky="ew", pady=10, padx=5)

    uploadImageButton = Button(tab1, text="Browse Image", command=lambda: add_file_image())
    uploadImageButton.grid(row=3, column=2, sticky="ew", pady=10, padx=5)
    # label_temp = Label(tab1 , text = "sample text")
    # label_temp.grid(row = 2 , column = 2 , pady = 10)


    # textBox = Entry(tab1, borderwidth=3)
    massageLabel = Label(tab1, text="Secret Message")
    massageLabel.grid(row=4, column=0)

    # encode code


def load_file(button, key):
    '''
    for loading the file in the send tab
    opens the dialog box for the file names and asks for a wav file
    if not provided a wav file shows an error
    '''
    global sender_fname
    sender_fname = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
    if sender_fname:
        try:
            # print("""here it comes: """)
            print(sender_fname)
            # if label1['text'].isdigit():
                # print('yes')
            # if is_hex(key.get()):
                # print('yes')
            button['state'] = 'normal'
            # else:
            #     displayError('Please enter an key (hex)')
        except:                     
            messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % sender_fname)
    return

def add_file_image():
    global fnameImage
    fnameImage = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg")])
    global isImageFile_sender
    isImageFile_sender = True
    if fnameImage:
        try:
            print(fnameImage)
            # button['state'] = 'normal'
        except:
            messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fnameImage)
    return 

def load_file_image(filename):
    with open(filename, 'rb') as img_file:
        # Read the image as a byte string
        byte_string = img_file.read()
    return byte_string

def load_file_receiver(button, key):
    '''
    opens up the filedialog box to browse the audio file where the message is hidden
    '''
    global fname
    fname = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
    if fname:
        try:
            # print("""here it comes: """)
            print(fname)
            if key.get() != '':
                button['state'] = 'normal'
            else:
                messagebox.showerror("Error", "Please enter a password")
                return
        except:                     
            messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fname)
        return



def generatePrimes(prime1Entry, prime2Entry):
    '''
    generates the prime number for the user if User does not want to calculate prime numbers
    '''
    (x, y) = Prime.generatePrimePair()
    # print(x,y)
    prime1Entry.delete(0, END)
    prime2Entry.delete(0 , 'end')
    prime1Entry.insert(0, str(x))
    prime2Entry.insert(0, str(y))

def displayError(text):
    '''
    shows the error when an exception is raised
    '''
    messagebox.showerror(message=text)

def checkEntries(prime1Entry, prime2Entry):
    '''
    checks the entries if both entries in the entry box are prime or not
    otherwise shows the error on the message box
    '''
    p1 = (prime1Entry.get()).strip()
    p2 = (prime2Entry.get()).strip()
    # print(p1.isdigit())
    # print(p1, p2) 
    # print(not p1.isdigit())
    if p1.isdigit() == False or p2.isdigit() == False:
        displayError("Please enter a valid Integer!!")
        return


    p1 = int(p1)
    p2 = int(p2)

    if p1 == p2:
        displayError("Same Numbers not allowed")
        prime1Entry.delete(0 , 'end')
        prime2Entry.delete(0 , 'end')
        return


    if Prime.checkPrime(p1) and Prime.checkPrime(p2):
        # create keys
        print('Both Primes')
        global pk1, pk2, pr1
        pk1, pk2, pr1 = receiver.receiver_create_key(p1, p2)
        changeKeyText(pk1, pk2, pr1)

        if fname is not None:
            decodeButton['state'] = 'normal'
        print(pk1, pk2, pr1)

    else:
        ls = []
        if(Prime.checkPrime(p1) == False): 
            ls.append(p1)
            prime1Entry.delete(0 , 'end')
        if(Prime.checkPrime(p2) == False): 
            ls.append(p2)
            prime2Entry.delete(0 , 'end')
        message = "Please enter valid prime numbers:\n"
        for elem in ls:
            message += "{} is not a prime\n".format(elem)
        displayError(message)

def decodeMessage(keyEntry):
    '''
    calls the decode module from the receiver tab and shows the message in a message box
    both decodes the message and decrypts the message
    '''
    passwd = keyEntry.get()
    if passwd == '':
        messagebox.showerror("Error", "Please enter a password")
        return
    key = generate_aes_256_key(passwd)
    encoded = decode(fname) #get secret message
    decoded = receiver.message_read(encoded, key) #return bytes

    flag = decoded[0]
    decoded = decoded[1:]

    if flag == 50:
        middle = bytes.fromhex('9999')
        position = decoded.find(middle)
        textMessage = decoded[:position]
        messagebox.showinfo("Decoded Message", "secet message: {}".format(textMessage.decode('utf-8')))
        saveTextFile(textMessage.decode('utf-8'), fname)
        imageMessage = decoded[position + len(middle):]
        saveImageFile(imageMessage, fname)
    elif flag == 49:
        messagebox.showinfo("Success", "Decoded image Successfully!")
        saveImageFile(decoded, fname)
    else:
        messagebox.showinfo("Decoded Message", "secet message: {}".format(decoded.decode('utf-8')))
        saveTextFile(decoded.decode('utf-8'), fname)

# def decodeImage(keyEntry):
#     key = bytes.fromhex(keyEntry.get())
#     encoded = decode(fname) #get secret message
#     decoded = receiver.message_read(encoded, key) #return bytes
#     messagebox.showinfo("Success", "Decoded Successfully!")
#     saveImageFile(decoded, fname)


def saveTextFile(text, filename):  
    filename = os.path.basename(filename)
    with open(os.path.join("output",os.path.splitext(filename)[0] + '_text.txt'), 'w') as fd:
        fd.write(text)

def saveImageFile(bytes, filename):
    img_data = io.BytesIO(bytes)
    img = Image.open(img_data)
    output_path = os.path.join("output",os.path.splitext(filename)[0] + '_image.jpg')
    img.save(output_path)

def changeKeyText(pk1, pk2, pr1):
    '''
    if prime numbers are valid this method
    replaces the lables to accomodate prime number within them
    '''
    global key1Label, key2Label, key3Label
    key1Label['text'] = 'Public Key 1: ' + str(pk1)
    key2Label['text'] = 'Public Key 2: ' + str(pk2)
    key3Label['text'] = 'Private Key: ' + str(pr1)

def addReceiveTab():
    '''
    receiver tab code
    pops up a message box when audio is decoded
    '''
    
    tab2.columnconfigure(1, weight=1)
    tab2.columnconfigure(0, weight=1)
    tab2.columnconfigure(2, weight=1)

    # label1 = Label(tab2, text="Prime 1")
    # label1.grid(row=0, column=0, pady=10)
    # prime1Entry = Entry(tab2, width=20, borderwidth=3)
    # prime1Entry.grid(row=1, column=0, padx=20)

    # label2 = Label(tab2, text="Prime 2")
    # label2.grid(row=0, column=2, pady=10)
    # prime2Entry = Entry(tab2, width=20, borderwidth=3)
    # prime2Entry.grid(row=1, column=2, padx=20)

    # generatePrimeButton = Button(tab2, text="Generate Prime Pair", command=lambda: generatePrimes(prime1Entry, prime2Entry))
    # generatePrimeButton.grid(row=2, column=1, sticky="ew")
    
    # generateKeyButton = Button(tab2, text="Generate Keys", command=lambda: checkEntries(prime1Entry, prime2Entry))
    # generateKeyButton.grid(row=3, column=1, pady=5, sticky="ew")

    # print(pk1, pk2, pr1)

    # key1Label.grid(row=4,column=0)

    # key2Label.grid(row=4,column=1)

    # key3Label.grid(row=4,column=2)

    label1 = Label(tab2, text="Key: ")
    label1.grid(row=1, column=0, pady=10)
    keyEntry = Entry(tab2, width=70, borderwidth=3)
    keyEntry.grid(row=1, column=1)

    global decodeButton
    decodeButton = Button(tab2, text="Decode", state=DISABLED, command=  lambda: decodeMessage(keyEntry))
    decodeButton.grid(row=7, column=1, sticky="ew", pady=10, padx=5)

    uploadAudioButton = Button(tab2, text="Browse Audio", command=lambda: load_file_receiver(decodeButton, keyEntry))
    uploadAudioButton.grid(row=5, column=1, sticky="ew", pady=10)

    # uploadImageButton = Button(tab2, text="Decode Image", command=lambda: decodeImage(keyEntry))
    # uploadImageButton.grid(row=7, column=2, sticky="ew", pady=10, padx=5)

    #maybe add file loacation label or a audio player



if __name__ == '__main__':
    root = Tk()
    root.title("Enshroud")
    root.geometry("800x350")
    # e = Entry(root, width=35, borderwidth=5)
    # e.grid(row=3, column=1, columnspan=3, padx=10, pady=10)

    tabControl = ttk.Notebook(root)

    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)

    pk1 = "-"
    pk2 = "-"
    pr1 = "-"

    key1Label = Label(tab2, text="public Key 1: " + pk1)
    key2Label = Label(tab2, text="public Key 2: " + pk2)
    key3Label = Label(tab2, text="private Key: " + pr1)

    tabControl.add(tab1, text="Send")
    tabControl.add(tab2, text="Receive")

    # tabControl.grid(row)


    addSendTab()
    addReceiveTab()

    tabControl.pack(expand=1,fill='both')
    root.mainloop()