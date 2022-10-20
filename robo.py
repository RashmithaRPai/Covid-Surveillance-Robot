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
            #if pressed 'w' move forward
            robby.forward()
            print("forward")
        elif data == "a":
            #if pressed 'a' move left 
            robby.left()
            print('left')
        elif data == "d":
            #if pressed 'd' move right
            robby.right()
            print("right")
        elif  data == "s":
            #if prerssed 's' move back
            robby.backward()
            print("back")
        elif data == "p":
            #if pressed 'p' close socket
            robby.stop()
            s.close()
            client_socket.close()
            print("stopped!!")
    
        
