from audioop import mul
from concurrent.futures import thread
import io
import socket
import struct
from turtle import up
import numpy
from decouple import config
from PIL import Image
import cv2
from matplotlib import pyplot as pl
import keyboard
import threading

# Pins for raspi
# 7	<–>	In1(yellow)
# 8	<–>	In2(red)
# 9	<–>	In3(brown)
# 10	<–>	In4(white)
# GND	<–>	GND

# Accept a single connection and make a file-like object out of it


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
            print(img)
            image = Image.open(image_stream)

            im = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2GRAY)

            #faces = face_cascade.detectMultiScale(gray, 1.3, 4)
            profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

            #for (x, y, w, h) in faces:
                #cv2.rectangle(im, (x, y), (x+w, y+h), (255, 0, 0), 2)
                #cv2.putText(im, 'Not wearing Mask(front)', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,0.9, (36, 255, 12), 2)
            for (x, y, w, h) in profiles:
                cv2.rectangle(im, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(im, 'Not wearing Mask(profile)', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,0.9, (36, 255, 12), 2)

            cv2.imshow('Video', im)
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