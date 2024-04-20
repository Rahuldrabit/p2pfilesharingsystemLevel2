import os
import socket
import threading

class UploaderPeer:
    # Define a class variable for the port number
    port = 12555

    def __init__(self, host, directory_path):
        self.host = host
        self.directory_path = directory_path
        self.file_names = []  # Initialize an empty list for file names

    def start(self):
        # Get file names from the directory path
        self.file_names = self.get_file_names_from_path()

        # Check if file_names is a list, if not, it's an error message
        if not isinstance(self.file_names, list):
            print(self.file_names)
            return

        # Print file names
        print(f"File names in {self.directory_path}: {self.file_names}")

        # Create a comma-separated string of file names
        files_str = ",".join(self.file_names)

        try:
            # Connect to the server and send the file names
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, UploaderPeer.port))
            self.client_socket.send("uploader".encode())
            self.client_socket.recv(1024)  # Wait for server acknowledgment
            self.client_socket.send(files_str.encode())
            print(f"Sent file names: {files_str}")
            print("Files uploaded successfully")
            self.client_socket.close()
        except Exception as e:
            print(f"error in trying connection with server{e}")

        try:
            # Set up the uploader socket to listen for downloader connections
            self.upldr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upldr_socket.bind((self.host, UploaderPeer.port))
            self.upldr_socket.listen(5)
            print(f"Uploader listening on {self.host}:{UploaderPeer.port}")

            while True:
                dwnldr_socket, dwnldr_address = self.upldr_socket.accept()
                print(f"Connection from {dwnldr_address}")
                # Start a new thread to handle file downloader handling
                threading.Thread(target=self.handle_dwnldr, args=(dwnldr_socket,)).start()
        except Exception as e:
            print(f"error in trying connection with downloader{e}")
    


    def handle_dwnldr(self, dwnldr_socket):
        # Implement the logic to handle the downloader here
        try:
            message = dwnldr_socket.recv(1024).decode()
            print(f"Received message: {message}")
            if message == "downloader":
                ack_message = "ACK"
                dwnldr_socket.send(ack_message.encode())
                print(f"Acknowledgment sent to {dwnldr_socket.getpeername()}")
                file_name = dwnldr_socket.recv(1024).decode()
                threading.Thread(target=self.handle_file_name, args=(dwnldr_socket, file_name)).start()
            else:
                print("Peer is not a downloader")
        except Exception as e:
            print(f"Error handling downloader: {e}")
        finally:
            dwnldr_socket.close()

    def handle_file_name(self, dwnldr_socket, file_name):
        if file_name in self.file_names:
            dwnldr_socket.send("ready to receive file chunk".encode())
        else:
            dwnldr_socket.send("file not found".encode())

    def get_file_names_from_path(self):
        try:
            # Get a list of all files in the specified directory
            file_names = os.listdir(self.directory_path)
            return file_names
        except Exception as e:
            print(f"Error reading file names: {e}")

if __name__ == "__main__":
    # Path to the Documents directory
    documents_path = os.path.expanduser("~/Documents")

    # Create an UploaderPeer instance with the documents path
    uploader = UploaderPeer("localhost", documents_path)

    # Start the uploader
    uploader.start()
