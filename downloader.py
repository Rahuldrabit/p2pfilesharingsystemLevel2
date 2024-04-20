import socket

class DownloaderPeer:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        try:
            file_name = input("Enter a file name (with extension) to download: ")
            if not file_name:
                raise ValueError("Please provide a non-empty file name.")

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send("downloader".encode())
            self.client_socket.recv(1024)  # Wait for server acknowledgment

            self.client_socket.send(file_name.encode())
            uploader_port_data = self.client_socket.recv(1024).decode()
            try:
                uploader_port = int(uploader_port_data)
                print(f"File found, connecting to uploader on port {uploader_port}")
                # Connect to the uploader and receive data
                self.client_socket.close()
                self.connect_to_uploader_and_receive_data(uploader_port, file_name)
            except ValueError:
                print("Received data is not a valid port number.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()

    def connect_to_uploader_and_receive_data(self, uploader_port, file_name):
        try:
            uploader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            uploader_socket.connect((self.host, int(uploader_port)))  # Ensure port is an integer
            print("Connected to uploader.")
            uploader_socket.send("downloader".encode())

            ack = uploader_socket.recv(1024).decode()  # Wait for server acknowledgment
            if ack == "ACK":
                # Send the file name to the uploader
                uploader_socket.send(file_name.encode())
                print(f"File name '{file_name}' sent to uploader.")

            # Open a file to write the received data
            with open(file_name, 'wb') as file:
                while True:
                    received_data = uploader_socket.recv(1024)
                    if not received_data:
                        break  # No more data from uploader
                    file.write(received_data)
                    print(f"Received data: {received_data}")

            print("File download completed.")
        except Exception as e:
            print(f"Error connecting to uploader: {e}")
        finally:
            uploader_socket.close()

if __name__ == "__main__":
    downloader = DownloaderPeer("localhost", 8000)  # Include the port number here
    downloader.start()
