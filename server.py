from cgitb import grey
import io
import socket
import struct
import numpy
from decouple import config
from PIL import Image
import cv2
from matplotlib import pyplot as pl

server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((config('IP_ADDRESS'), int(config('PORT'))))  # ADD IP HERE
server_socket.listen(1)
path=config('PATH')
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

def draw_found_faces(detected, image, color: tuple):
    for (x, y, width, height) in detected:
        cv2.rectangle(
            image,
            (x, y),
            (x + width, y + height),
            color,
            thickness=2
        )

# Accept a single connection and make a file-like object out of it
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
        image = Image.open(image_stream)
        #faceCascade=cv2.CascadeClassifier(path)
        im = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        
        gray=cv2.cvtColor(numpy.array(image),cv2.COLOR_BGR2GRAY)
        faces=face_cascade.detectMultiScale(gray,1.1,4)
        profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (255, 0, 0), 2)
        for (x, y, w, h) in profiles:
            cv2.rectangle(im, (x, y), (x+w, y+h), (255, 0, 0), 2)
        print("face",faces)
        print("profile",profiles)
        #cv2.imshow('Video',im)
        if cv2.waitKey(1) & 0xFF == ord('q'):
           break

        print('Image is %dx%d' % image.size)
        image.verify()
        print('Image is verified')
finally:
    connection.close()
    server_socket.close()
