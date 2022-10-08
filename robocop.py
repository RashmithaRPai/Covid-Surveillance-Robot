from gpiozero import Robot
from time import sleep
import socket
from decouple import config

client_socket = socket.socket()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((config('IP_ADDRESS'), int(config('DIRPORT'))))
    while True:
        data = s.recv(1024).decode()
        print(f"Received {data!r}")
        #robot = Robot(left=(4, 14), right=(17, 18))
