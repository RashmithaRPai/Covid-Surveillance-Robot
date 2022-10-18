import sys

if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

from os import listdir, path

if not path.isfile('face_alignment/detection/sfd/s3fd.pth'):
	raise FileNotFoundError('Save the s3fd model to face_detection/detection/sfd/s3fd.pth \
							before running this script!')

from audioop import mul
from concurrent.futures import thread
import io
import socket
import struct
from turtle import up
import numpy as np
from decouple import config
from PIL import Image
import cv2
from matplotlib import pyplot as pl
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, os, traceback, subprocess
import keyboard
import threading
from glob import glob
import face_alignment
from try_server import define_class

# Pins for raspi
# 7	<–>	In1(yellow)
# 8	<–>	In2(red)
# 9	<–>	In3(brown)
# 10	<–>	In4(white)
# GND	<–>	GND

fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, device='cuda:{}'.format(0))
template = 'ffmpeg -loglevel panic -y -i {} -strict -2 {}'

classCategory = {
    0: "with mask",
    1: "improper mask",
    2: "wihout mask"
}

def play_video():
    # video socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((config('IP_ADDRESS'), int(config('PORT'))))  # ADD IP HERE
    server_socket.listen(1)
    #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    connection = server_socket.accept()[0].makefile('rb')
    try:
        img = None
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))

            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            #print(img)
            image = Image.open(image_stream)

            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            preds = fa.get_landmarks(frame,return_bboxes=True)
            if preds != (None, None, None):
                cords=[]
                #print(preds)
                for i in enumerate(preds[2][0]):
                    x = int(i[1])
                    cords.append(x)
                x1, y1, x2, y2, _= cords
                copyframe = frame.copy()
                #cv2.imshow('Video', copyframe[x1:x2,y1:y2])
                index = define_class(copyframe[x1:x2,y1:y2])
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, str(classCategory[index]), (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('p'):
                break
            print('Image is %dx%d' % image.size)
            image.verify()
            print('Image is verified')
    finally:
        connection.close()
        server_socket.close()


def send_dir():
    server_dir_socket = socket.socket()
    server_dir_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_dir_socket.bind((config('IP_ADDRESS'), int(config('DIRPORT'))))  # ADD IP HERE
    server_dir_socket.listen(1)

    conn, _ = server_dir_socket.accept()

    while (True):
        key = keyboard.read_key()
        if key == 'q':
            return
        print(type(key))
        conn.sendall(key.encode())


if __name__ == "__main__":

    p1 = threading.Thread(target = play_video)
    p2 = threading.Thread(target = send_dir)

    p1.start()
    p2.start()