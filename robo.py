from gpiozero import Robot
from time import sleep
import socket
from decouple import config

client_socket = socket.socket()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((config('IP_ADDRESS'), int(config('DIRPORT'))))
    robby = Robot(left=(7, 8), right=(9,10))
    while True:
        data = s.recv(1024).decode()
        if data=="w":
            robby.forward()
            print("forward")
        elif data == "a":
            robby.left()
            print('left')
        elif data == "d":
            robby.right()
            print("right")
        elif  data == "s":
            robby.backward()
            print("back")
        elif data == "p":
            robby.stop()
            s.close()
            client_socket.close()
            print("stopped!!")
    
        
