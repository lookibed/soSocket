from server2 import ThreadedSocketClient  # Импортируем класс
import time

# Создаем экземпляр клиента
client = ThreadedSocketClient()
client.connect()

try:
    while client.running:
        # Отправляем сообщение каждую секунду
        client.send_data("Привет")
        
        # Проверяем, есть ли новые данные от сервера
        received_data = client.get_data()
        if received_data:
            print("Main Принято:", received_data)
        
        time.sleep(0.05)  # Задержка перед повторной отправкой
except KeyboardInterrupt:
    print("Main Ручная остановка клиента.")
finally:
    client.close()
