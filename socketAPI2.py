import os
import socket
import threading
import time

class SocketAPI:
    def __init__(self):
        self.curdirect = ""
        self.connected = False
        self.buffer_size = 1024  # Default buffer size
        self.socket = None
        self.export_directory = self.find_export_directory()
        
        if not self.export_directory:
            print("Directory /export does not exist")
            input("Press Enter to exit...")
            return
        
        # Define file paths
        self.in_data_path = os.path.join(self.export_directory, "inData")
        self.out_data_path = os.path.join(self.export_directory, "outData")
        
        # Clean up existing data files
        self.delete_file(self.out_data_path)
        self.delete_file(self.in_data_path)
        
        # Start the timer thread
        self.timer = threading.Thread(target=self.in_data_timer)
        self.timer.daemon = True
        self.timer.start()
        
        print("Started")
        
        # Keep the main thread alive
        self.keep_running()

    def find_export_directory(self):
        th2 = ""
        path = "./"
        for _ in range(4):
            path = os.path.join("./", th2)
            export_path = os.path.join(path, "export")
            if os.path.isdir(export_path):
                return export_path
            th2 = os.path.join(th2, "..")
        return ""

    def delete_file(self, file_path):
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    def in_data_timer(self):
        while True:
            if os.path.isfile(self.in_data_path):
                try:
                    with open(self.in_data_path, 'r', encoding='utf-8') as f:
                        indata = f.read()
                    os.remove(self.in_data_path)
                    
                    if self.connected:
                        response = self.send_socket(indata)
                        self.out_data(response)
                    else:
                        self.connect(indata)
                except Exception as e:
                    print(f"Error processing inData: {e}")
            time.sleep(0.1)  # 100 ms

    def connect(self, data):
        try:
            args = data.split('/')
            if len(args) < 3:
                print("Invalid connection data format")
                self.out_data("-cn")
                return
            
            ip = args[0]
            port = int(args[1])
            self.buffer_size = int(args[2])
            remaining_data = '/'.join(args[3:])
            
            # Clean up existing data files
            self.delete_file(self.out_data_path)
            self.delete_file(self.in_data_path)
            
            # Create and connect the socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
            self.connected = True
            print("Connected")
            
            # Send the remaining data
            response = self.send_socket(remaining_data)
            if response == "-cn":
                print("Error connecting to server")
            self.out_data(response)
        except Exception as e:
            print("Error connecting program")
            print(e)
            self.out_data("-cn")

    def send_socket(self, data):
        try:
            if not self.socket:
                print("Socket is not connected")
                self.connected = False
                return "-cn"
            
            # Send data
            self.socket.sendall(data.encode('utf-8'))
            
            # Receive response
            self.socket.settimeout(5)  # Timeout after 5 seconds
            received_data = []
            while True:
                try:
                    part = self.socket.recv(self.buffer_size)
                    if not part:
                        break
                    received_data.append(part.decode('utf-8'))
                except socket.timeout:
                    break
            return ''.join(received_data)
        except Exception as e:
            print("Disconnected")
            print(e)
            self.connected = False
            return "-cn"

    def out_data(self, outdata):
        try:
            if not os.path.isfile(self.out_data_path):
                with open(self.out_data_path, 'w', encoding='utf-8') as f:
                    f.write(outdata)
            else:
                print("outData write failed: File already exists")
        except Exception as e:
            print(f"Error writing outData: {e}")

    def keep_running(self):
        try:
            while True:
                input()  # Wait for user input to keep the program running
        except KeyboardInterrupt:
            print("Program terminated by user.")
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    SocketAPI()
