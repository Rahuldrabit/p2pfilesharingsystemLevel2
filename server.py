import socket
import threading

class FileServer:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.files = {}
        self.lock = threading.Lock()

    def run_server(self):
            
            #uploader section
        
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind((self.host, self.port))
                server_socket.listen(5)
                print(f"Server listening on {self.host}:{self.port} for uploader")
                
                client_socket, client_address = server_socket.accept()
                client_ip, client_port = client_address  # Unpack the tuple
                print(f"Connection from IP: {client_ip}, Port: {client_port}")
                uploader_address=client_port    

                try:
                    peer_type = client_socket.recv(1024).decode()
                    if not peer_type:
                        raise Exception("Client disconnected")
                    print(f"Received peer type: {peer_type}")
                    client_socket.send("ACK".encode())  # Send acknowledgment to uploader
                    if peer_type == "uploader":
                        try:
                            client_socket.send("send".encode())
                        except Exception as e:
                            print(f"Error handling uploader: {e}")
                        try:
                            files = client_socket.recv(8192).decode().split(",")
                            with self.lock:
                                for i, file in enumerate(files, start=1):
                                    self.files[file] = client_socket.getpeername()
                                    print(f"Uploaded file {i}: {file}")
                            print("Files uploaded successfully")
                        except Exception as e:
                            print(f"Error handling uploader: {e}")

                except KeyboardInterrupt:
                    print("Server is shutting down.")
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                server_socket.close()
            server_socket.close()    

                #Downloader section

            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind((self.host, self.port))
                server_socket.listen(5)
                print(f"Server listening on {self.host}:{self.port} for Downloader")
                
                client_socket, client_address = server_socket.accept()
                client_ip, client_port = client_address  # Unpack the tuple
                print(f"Connection from IP: {client_ip}, Port: {client_port}")

                try:
                    peer_type = client_socket.recv(1024).decode()
                    if not peer_type:
                        raise Exception("Client disconnected")
                    print(f"Received peer type: {peer_type}")
                    client_socket.send("ACK".encode())  # Send acknowledgment to uploader
                    if peer_type == "downloader":
                        try:
                            file_name = client_socket.recv(1024).decode()
                            with self.lock:
                                if file_name in self.files:
                                    client_socket.send(str(uploader_address).encode())
                                else:
                                    client_socket.send("File not found".encode())
                        except Exception as e:
                            print(f"Error handling downloader: {e}")

                except KeyboardInterrupt:
                    print("Server is shutting down.")
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                server_socket.close()    


    

if __name__ == "__main__":
    uploader_address=0
    server = FileServer("localhost", 8000)  # Specify the port number here
    server.run_server()
