import socket
import time
import json

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('localhost', 2000))

    while True:
        massage = 'Писка привет'
        sock.sendall(massage.encode('utf-8'))

        data = sock.recv(1024)
        print('Ответ сервера: ', data.decode('utf-8'))

        time.sleep(1)