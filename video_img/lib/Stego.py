import numpy as np
from imageio import imread, imwrite
from multipledispatch import dispatch
from lib.VideoStego import *
from subprocess import call, STDOUT
import cv2
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import subprocess
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class Stego:

    def __init__(self, cover="lib/images/cover.png", coverVideo="lib/videos/cover.mp4"):
        self.img_path = cover
        self.video_path = coverVideo
        self.output_path = "lib/output/secured.png"
        self.max_value = 255
        self.header_len = 4 * 8

    @dispatch(str)
    def stego(self, file_path):
        # Hiển thị hộp thoại để chọn vị trí lưu file
        output_path, _ = QFileDialog.getSaveFileName(None, "Save Encoded Image", "", "Images (*.png *.bmp *.jpg)")
        if not output_path:
            return

        image, shape_orig = self.read_image(self.img_path)
        file = self.read_file(file_path)
        file_len = file.shape[0]
        len_array = np.array([file_len], dtype=np.uint32).view(np.uint8)
        len_array = np.unpackbits(len_array)
        img_len = image.shape[0]

        if file_len >= img_len - self.header_len:  # 4 bytes are used to store file length
            alert("Warning","File size too large, trying a different cover image...")
            self.img_path = "images/coverLarge.png"
            image, shape_orig = self.read_image(self.img_path)
            img_len = image.shape[0]
            if file_len >= img_len - self.header_len:
                alert("Warning","File size too large, going for video steganography...")
                self.stegoVideo(file_path)
                return
            else:
                tmp = file
                file = np.random.randint(2, size=img_len, dtype=np.uint8)
                file[self.header_len:self.header_len + file_len] = tmp
        else:
            tmp = file
            file = np.random.randint(2, size=img_len, dtype=np.uint8)
            file[self.header_len:self.header_len + file_len] = tmp
        file[:self.header_len] = len_array
        encoded_data = self.encode_data(image, file)

        self.write_image(output_path, encoded_data, shape_orig)
        os.remove(file_path)
        alert("Success","Message encoded successfully")
        #print(f"Output available at: {output_path}")
        self.img_path = "lib/images/cover.png"
        return

    @dispatch(str, str)
    def stego(self, f, coverImg):
        self.img_path = coverImg
        self.stego(f)

    def unStego(self, stegoImgFile, outputFile):
        img_path = stegoImgFile
        if not os.path.isfile(img_path):
            #print("Image file does not exist")
            return
        file_path = outputFile
        encoded_data, shape_orig = self.read_image(img_path)
        data = self.decode_data(encoded_data)
        el_array = np.packbits(data[:self.header_len])
        extracted_len = el_array.view(np.uint32)[0]
        data = data[self.header_len:extracted_len + self.header_len]
        self.write_file(file_path, data)
        #print("Starting Image decoding...")
        return

    @staticmethod
    def read_image(img_path):
        img = np.array(imread(img_path), dtype=np.uint8)
        orig_shape = img.shape
        return img.flatten(), orig_shape

    @staticmethod
    def write_image(img_path, img_data, shape):
        img_data = np.reshape(img_data, shape)
        imwrite(img_path, img_data)

    @staticmethod
    def bytes2array(byte_data):
        byte_array = np.frombuffer(byte_data, dtype=np.uint8)
        return np.unpackbits(byte_array)

    @staticmethod
    def array2bytes(bit_array):
        byte_array = np.packbits(bit_array)
        return byte_array.tobytes()

    def read_file(self, file_path):
        file_bytes = open(file_path, "rb").read()
        return self.bytes2array(file_bytes)

    def write_file(self, file_path, file_bit_array):
        bytes_data = self.array2bytes(file_bit_array)
        f = open(file_path, 'wb')
        f.write(bytes_data)
        f.close()

    def encode_data(self, image, file_data):
        or_mask = file_data
        and_mask = np.zeros_like(or_mask)
        and_mask = (and_mask + self.max_value - 1) + or_mask
        res = np.bitwise_or(image, or_mask)
        res = np.bitwise_and(res, and_mask)
        return res

    @staticmethod
    def decode_data(encoded_data):
        out_mask = np.ones_like(encoded_data)
        output = np.bitwise_and(encoded_data, out_mask)
        return output
    
    @staticmethod
    def video_to_frames(video_path, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        cap = cv2.VideoCapture(video_path)
        current_frame = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_name = os.path.join(output_folder, f"{current_frame}.png")
            cv2.imwrite(frame_name, frame)
            current_frame += 1
        cap.release()

        # Extract audio from video
        video = VideoFileClip(video_path)
        audio_path = os.path.join(output_folder, "audio.mp3")
        video.audio.write_audiofile(audio_path)
        print(f"Frames and audio extracted to {output_folder}")

    @staticmethod
    def frames_to_video(frames_folder, output_video_path, output_audio_path, final_output_path, fps=24):
        frames = []
        frame_files = [f for f in os.listdir(frames_folder) if f.endswith(".png")]
        frame_files.sort(key=lambda x: int(os.path.splitext(x)[0]))  # Sort by frame number

        # Read and append frames
        for frame_file in frame_files:
            frame_path = os.path.join(frames_folder, frame_file)
            img = cv2.imread(frame_path)
            frames.append(img)

        height, width, _ = frames[0].shape
        size = (width, height)
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

        for frame in frames:
            out.write(frame)
        out.release()

        # Merge audio with video
        audio_clip = AudioFileClip(output_audio_path)
        video_clip = VideoFileClip(output_video_path)
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac")



    @dispatch(str)
    def stegoVideo(self, file_path):
        video_path = self.video_path
        temp_folder = "./lib/temp"
        output_video_path = os.path.join(temp_folder, "video.mp4")
        output_audio_path = os.path.join(temp_folder, "audio.mp3")
        final_output_path = "./lib/output/secured.mp4"

        if not os.path.exists(video_path):
            print("Video not found...")
            return

        print("Extracting video frames and audio...")
        self.video_to_frames(video_path, temp_folder)

        frame_idx = input("Choose no. frame to hide: ")

        print("Encrypting data into a specific frame...")
        frame_to_encode = os.path.join(temp_folder, "{}.png".format(frame_idx))  # Adjust the frame index as needed
        if not os.path.exists(frame_to_encode):
            print("Frame not found for encoding.")
            return
        
        # Perform encoding
        img = cv2.imread(frame_to_encode, cv2.IMREAD_UNCHANGED)
        encoded_img = encode_frame(img, file_path)
        cv2.imwrite(frame_to_encode, encoded_img)
        os.remove(file_path)

        print("Merging frames into video and adding audio...")
        self.frames_to_video(temp_folder, output_video_path, output_audio_path, final_output_path)
        print(f"Stego video created at: {final_output_path}")


    @dispatch(str, str)
    def stegoVideo(self, f, coverVideo):
        self.video_path = coverVideo
        self.stegoVideo(f)

    @staticmethod
    def unStegoVideo(stegoVideoFile, outputFile):
        file_name = stegoVideoFile

        try:
            open(file_name)
        except IOError:
            print("Video not found...")
            return
        decoded = None

        print("Decrypting Frame(s)...")
        path = "./lib/temp"
        files = [f for f in os.listdir(path) if not f.startswith('.')]
        for file in files:
            filename = os.path.join(path, file)
            img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            decoded = decode_frame(img, outputFile)
            if decoded != None:
                break


def alert(string1, string2):
    msg_box = QMessageBox()
    msg_box.setWindowTitle(string1)
    msg_box.setText(string2)
    # Thiết lập StyleSheet để căn giữa văn bản
    msg_box.setStyleSheet(
        "QLabel{font: 15pt \"Berlin Sans FB\"; min-height:150 px; min-width: 400px;} QPushButton{ width:100px; height:30px; border-radius: 5px; font: 75 14pt \"Berlin Sans FB Demi\"; background-color: rgb(165, 213, 255);} QPushButton:hover{background-color: rgb(3, 105, 161); color: rgb(255,255,255);}"
        )
    msg_box.exec()