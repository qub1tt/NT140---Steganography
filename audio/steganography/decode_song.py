import wave
def decode(path):

    end_char = '#$%'
    # song = wave.open('song_embedded.wav', 'rb')
    song = wave.open(path, 'rb')

    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    received = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]  
    # print(type(received[0]))

    # decoded = ""
    # for i in range(0, len(received), 8):
    #     '''
    #         map(str, [int list]): will convert all ints to string: [1,0,1]: ['1','0','1']
    #         .join(): convert list to string
    #         int(string, 2): convert given string to integer and the given base is 2(binary)
    #         chr: convert the given integer to it's corresponding character
    #     '''
    #     char = chr(int("".join(map(str, received[i:i+8])), 2))
    #     decoded += char
    #     if end_char in decoded[len(decoded) - len(end_char) - 1:-1]:
    #         decoded = decoded.split(end_char)[0]
    #         break
    
    end_char_byte = end_char.encode('utf-8')
    end_char_length = len(end_char_byte)

    decoded_bytes = bytearray()
    for i in range(0, len(received), 8):
        # Nhóm 8 bit lại và chuyển sang một byte
        byte = int("".join(map(str, received[i:i+8])), 2)
        if len(decoded_bytes) >= end_char_length:
            # So sánh phần cuối của decoded_bytes với end_char
            if decoded_bytes[-end_char_length:] == end_char_byte:
                # Nếu có, dừng lại và trả về thông điệp giải mã
                break
        decoded_bytes.append(byte)
        

    # Tìm và loại bỏ dấu kết thúc thông điệp
    # decoded = bytes(decoded_bytes).decode('utf-8', errors='ignore')
    # if end_char in decoded:
    #     decoded = decoded.split(end_char)[0]
    decoded_bytes = decoded_bytes[:-3]
    return decoded_bytes