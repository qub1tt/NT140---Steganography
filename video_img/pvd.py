import cv2
import numpy as np
import bisect
import argparse

from typing import Tuple


def embending(n: int) -> Tuple[int, int, int]:
    srange = (0, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256)
    l = bisect.bisect_right(srange, n) - 1
    return srange[l], int(np.log2(srange[l + 1] - srange[l])), srange[l + 1] - 1

def change_diff(diff: int, l: int, r: int) -> Tuple[bool, int, int]:
    swap = False
    if l > r:
        l, r = r, l
        swap = True
    
    sg = np.sign(diff)
    ost = sg * (np.abs(diff) % 2)
    floor = sg * (np.abs(diff) // 2)

    l -= floor
    r += floor
    
    if l < 0 or r > 255 or ost > 0 and l == 0 and r == 255:
        return False, 0, 0
    
    if ost > 0 and l > (255 - r) or ost < 0 and l < (255 - r):
        l -= ost
    else:
        r += ost
    
    if swap:
        l, r = r, l

    return True, l, r

def bin_to_bytes_readable(b: str) -> bytearray:
    return bytearray([int(b[i:i+8], 2) for i in range(0, len(b), 8)])

def pvd_store(img_name: str, secret: str) -> bool:
    img = cv2.imread(img_name)

    height, width = img.shape[0], img.shape[1]
    width -= width % 2
    
    data = bin(int.from_bytes(bytearray(secret.encode()), byteorder='big'))[2:]

    data = '0' * (8 - len(data) % 8) + data

    data_len = bin(len(data))[2:].zfill(32)
    data = data_len + data

    i = capacity = 0
    while i < height:
        for j in range(0, width, 2):
            for k in range(3):
                dif = max(img[i, j + 1, k], img[i, j, k]) - min(img[i, j + 1, k], img[i, j, k])

                emb, n, maxr = embending(dif)
                res, _, _ = change_diff(maxr - dif, min(img[i, j + 1, k], img[i, j, k]), max(img[i, j + 1, k], img[i, j, k]))
                if not res:
                    continue
                
                bits = data[capacity:capacity + n]
                capacity += len(bits)

                new_dif = emb + int(bits, 2)
                _, img[i, j, k], img[i, j + 1, k] = change_diff(new_dif - dif, img[i, j, k], img[i, j + 1, k])

                if capacity == len(data):
                    cv2.imwrite('stego.png', img)
                    
                    return True
        
        i += 1

    return False

def pvd_unstore(img_name: str) -> str:
    img = cv2.imread(img_name)

    height, width = img.shape[0], img.shape[1]
    width -= width % 2

    capacity = -1
    result_len, is_body = '', False
    result = ''
    for i in range(height):
        for j in range(0, width, 2):
            for k in range(3):
                dif = max(img[i, j + 1, k], img[i, j, k]) - min(img[i, j + 1, k], img[i, j, k])

                emb, ln, maxr = embending(dif)
                res, _, _ = change_diff(maxr - dif, min(img[i, j + 1, k], img[i, j, k]), max(img[i, j + 1, k], img[i, j, k]))
                if not res:
                    continue
                
                secret = dif - emb

                bits = bin(secret)[2:].zfill(ln)
                if not is_body:
                    result_len += bits

                    if len(result_len) >= 32:
                        is_body = True
                        capacity = int(result_len[:32], 2)

                        if len(result_len) > 32:
                            result = result_len[32:]
                    
                    continue
                else:
                    if len(bits) + len(result) > capacity:
                        bits = bits.lstrip('0')
                        bits = bits.zfill(capacity - len(result))
                    
                    result += bits
                
                if is_body and len(result) == capacity:
                    return bin_to_bytes_readable(result).decode()
    
    return 'Error! Impossible to extract secret message!'

def main():
    parser = argparse.ArgumentParser(description='PVD steganography')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', help='Hide secret message', action='store_true')
    group.add_argument('-d', help='Reveal secret message', action='store_true')
    parser.add_argument('image', metavar="image", type=str, help="Path to container image")
    
    params = parser.parse_args()
    if params.e:
        secret = input('Input secret message: ')
        if pvd_store(params.image, secret):
            print('Text was successfully hidden in stego.png')
        else:
            print(f'Too long text for image {params.image}. Container "stego.png" is invalid.')
        
        return
    
    if params.d:
        secret = pvd_unstore(params.image)
        print(f'Hidden message: {secret}')
        
        return

    parser.print_help()


if __name__ == '__main__':
    main()