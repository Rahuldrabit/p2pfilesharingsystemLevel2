import socket
import threading

class FileServer:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.files = {}
        self.lock = threading.Lock()

    def run_server(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server is shutting down.")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            server_socket.close()

    def handle_client(self, client_socket):
        try:
            peer_type = client_socket.recv(1024).decode()
            if not peer_type:
                raise Exception("Client disconnected")
            print(f"Received peer type: {peer_type}")
            client_socket.send("ACK".encode())  # Send acknowledgment to uploader
            if peer_type == "uploader":
                self.handle_uploader(client_socket)
            elif peer_type == "downloader":
                self.handle_downloader(client_socket)
            else:
                print(f"Unknown peer type: {peer_type}")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def handle_uploader(self, client_socket):
        x=client_socket.recv(1024).decode()
        if x==int(x):
            client_socket.send("send".encode())
        
        try:
            files = client_socket.recv(8192).decode().split(",")
            with self.lock:
                for i, file in enumerate(files, start=1):
                    self.files[file] = client_socket.getpeername()
                    print(f"Uploaded file {i}: {file}")
            print("Files uploaded successfully")
        except Exception as e:
            print(f"Error handling uploader: {e}")

    def handle_downloader(self, client_socket):
        try:
            file_name = client_socket.recv(1024).decode()
            with self.lock:
                if file_name in self.files:
                    uploader_address = x
                    client_socket.send(int(uploader_address).encode())
                else:
                    client_socket.send("File not found".encode())
        except Exception as e:
            print(f"Error handling downloader: {e}")

if __name__ == "__main__":
    x=0
    server = FileServer("localhost", 8000)  # Specify the port number here
    server.run_server()
