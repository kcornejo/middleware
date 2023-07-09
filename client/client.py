import socket
import threading
import os

from dotenv import load_dotenv
load_dotenv('.env')


host = 'localhost'
port = 5000

username = input(f"{host}:{port} enter your identity: " )

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == '@id':
                client.send(username.encode('utf-8'))
            else:
                print(message)
        except:
            print("An a error ocurred")
            client.close()

def write_messages():
    while True:
        message = f"{input('')}"
        client.send(message.encode('utf-8'))
    
rec_msg_thr = threading.Thread(target=receive_messages)    
rec_msg_thr.start()

wr_msg_thr = threading.Thread(target=write_messages)    
wr_msg_thr.start()
    