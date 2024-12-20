# from tkinter import messagebox
# import wave
# import os
# def encode(path, message: bytes):
#     filename = os.path.basename(path)
#     end_char = '#$%' # denotes message end
#     # song = wave.open('song.wav', 'rb')
#     song = wave.open(path, 'rb')
#     # f = open('message.txt' , 'r+')
#     # msg_list = f.read().split()
#     # # f.close()
#     # message = ''
#     # for i in msg_list:
#     #     message= message + i + ' '
#     # print(message)

#     '''
#         This will give us the number of bytes of frames that we have
#         song.getnframes() -> gets the number of audio frames
#         song.readframes() -> read those frames and return a binary string 
#         bytearray-> converts the normal list to bytearray
#     '''
#     frame_byte = bytearray(list(song.readframes(song.getnframes())))
#     # print(frame_byte[1002310])
#     # print(len(frames))

#     '''
#         len(message)-> number of bytes required
#         *8 -> will give us the number of bits that we need
#         each framebyte can only store 1 bit of data(LSB)
#         Therefore, we will require that many frame_bytes as the number of bits that we need. Others are extra
#     '''

#     # file_size = os.path.getsize(path)
#     # print(f"Kích thước của file là: {file_size} byte")
#     # print(f"Kích thước tối đa có thể ẩn dữ liệu là: {len(frame_byte)/8} byte")
#     # print(f"Tỉ lệ là: {(len(frame_byte)/8)/file_size}")


#     # message = message + min(int((len(frame_byte) - len(message)*8)/8), 3)*'#'
#     if(len(frame_byte) - len(message)*8 - len(end_char)*8< 0): # 24 for ending characters
#         messagebox.showinfo("Reduce the message size", "The ratio is 1 byte of data / 8 bytes of size.")
#         print('Reduce the message size')
#         song.close()
#         return

#     # add end of message
    

#     # print(message)

#     # #char->ascii(int)->binaryRepresentation->remove 0b prefix
#     # x = [bin(ord(i)).lstrip('0b') for i in message]
#     # #make it in the form of 8bits i.e 1 byte. Eg: 5: 101 -> 00000101
#     # y = [i.rjust(8, '0') for i in x]
#     # #convert to string
#     # tempStr = ''.join(y)
#     # #convert char to int : '1': 1, '0': 0
#     # bitArray = list(map(int, tempStr))
#     # for i, bit in enumerate(bitArray):
#     #     #Add the required bit to the LSB of the frame byte
#     #     frame_byte[i] = (frame_byte[i]&254) | bit
    
#     message += end_char.encode('utf-8')
#     message_bits = ''.join([bin(byte)[2:].rjust(8, '0') for byte in message])

#     bitArray = list(map(int, message_bits))
#     for i, bit in enumerate(bitArray):
#         #Add the required bit to the LSB of the frame byte
#         frame_byte[i] = (frame_byte[i]&254) | bit

#     # for i in range(len(message_bits)):
#     #     bit = int(message_bits[i])
#     #     frame_byte[i] = (frame_byte[i] & 0xFE) | bit

#     #save the song
#     with wave.open(os.path.join("output",os.path.splitext(filename)[0] + '_encoded.wav'), 'wb') as fd:
#         fd.setparams(song.getparams())
#         fd.writeframes(bytes(frame_byte))
#     song.close()
#     messagebox.showinfo("Success", "Encoded Successfully")


from tkinter import messagebox, filedialog
import wave
import os

def encode(path, message: bytes):
    filename = os.path.basename(path)
    end_char = '#$%'  # denotes message end
    song = wave.open(path, 'rb')

    frame_byte = bytearray(list(song.readframes(song.getnframes())))

    if len(frame_byte) - len(message)*8 - len(end_char)*8 < 0:  # Check space availability
        messagebox.showinfo("Error", "Reduce the message size. The ratio is 1 byte of data / 8 bytes of size.")
        song.close()
        return

    # Append end character and convert message to bit array
    message += end_char.encode('utf-8')
    message_bits = ''.join([bin(byte)[2:].rjust(8, '0') for byte in message])
    bitArray = list(map(int, message_bits))

    for i, bit in enumerate(bitArray):
        # Add the required bit to the LSB of the frame byte
        frame_byte[i] = (frame_byte[i] & 254) | bit

    # Open save dialog to choose the save location
    save_path = filedialog.asksaveasfilename(
        title="Save Encoded File",
        defaultextension=".wav",
        filetypes=[("Waveform Audio File", "*.wav")]
    )
    if not save_path:  # If the user cancels the save dialog
        messagebox.showinfo("Cancelled", "Encoding process cancelled by the user.")
        song.close()
        return

    # Save the encoded song
    with wave.open(save_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(bytes(frame_byte))

    song.close()

