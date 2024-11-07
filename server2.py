import socket
import threading
import queue
import time

class ThreadedSocketClient:
    def __init__(self, ip="localhost", port=2000, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.data_queue = queue.Queue()  # Очередь для хранения данных

    def connect(self):
        try:
            self.client_socket.connect((self.ip, self.port))
            print(f"Подключено к {self.ip}:{self.port}")
            # Запускаем поток для получения данных
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()
        except ConnectionRefusedError:
            print(f"Ошибка подключения к {self.ip}:{self.port}")
            self.running = False

    def receive_data(self):
        while self.running:
            try:
                data = self.client_socket.recv(self.buffer_size)
                if data:
                    decoded_data = data.decode("utf-8")
                    print("Thread_1 Принято:", decoded_data)
                    self.data_queue.put(decoded_data)  # Кладем данные в очередь
                else:
                    print("Thread_1 Сервер разорвал соединение.")
                    self.running = False
                    break
            except Exception as e:
                print("Thread_1 Error receiving data:", e)
                self.running = False
                break

    def send_data(self, message):
        try:
            self.client_socket.sendall(message.encode("utf-8"))
            print("Отправлено:", message)
        except Exception as e:
            print("Error sending data:", e)
            self.running = False

    def get_data(self):
        # Возвращает данные из очереди, если они есть
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None

    def close(self):
        self.running = False
        self.client_socket.close()
