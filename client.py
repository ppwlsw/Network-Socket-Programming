#client.py
import socket, hashlib, os
from protocol import (
    STATUS_OK, STATUS_FILE_NOT_FOUND, STATUS_INVALID_COMMAND,
    STATUS_HASH_MISMATCH, STATUS_FILE_ALREADY_EXISTS,
    STATUS_PERMISSION_DENIED, STATUS_INTERNAL_SERVER_ERROR,
    STATUS_UPLOAD_SUCCESS, send_response, recv_response
)

SERVER_HOST = socket.gethostname()
SERVER_PORT = 12345

def create_local_folder(username):
    if not os.path.exists(username):
        os.makedirs(username)

def upload_file(client_socket, local_folder):
    filename = input("Enter the filename to upload: ")
    filepath = os.path.join(local_folder, filename)
    
    if os.path.exists(filepath):
        filesize = os.path.getsize(filepath)
        filehash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(1024):
                filehash.update(chunk)
        filehash_hex = filehash.hexdigest()
        command = f'UPLOAD {filename} {filesize} {filehash_hex}'
        client_socket.send(command.encode('utf-8'))
        
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(1024):
                    client_socket.send(chunk)
            status_code, message = recv_response(client_socket)
            print(f"[CODE]: {status_code}\n[PHRASE] {message}")
            if status_code == STATUS_FILE_ALREADY_EXISTS.split()[0]:
                print("Error: File already exists on the server.")
            elif status_code == STATUS_UPLOAD_SUCCESS.split()[0]:
                print("Success: File uploaded successfully.")
        except Exception as e:
            print(f"An error occurred while uploading: {e}")
    else:
        print("File does not exist.")

def list_files(client_socket):
    command = 'LIST'
    client_socket.send(command.encode('utf-8'))
    
    try:
        status_code, file_list = recv_response(client_socket)
        print(f"[STATUS : {status_code}]")
        if status_code == STATUS_OK.split()[0]:
            print("\nFiles available on the server:\n")
            print("\n".join(file_list[3::].split()))
            print()
        else:
            print("Error:", file_list)
    except Exception as e:
        print(f"An error occurred while listing files: {e}")

def download_file(client_socket, local_folder):
    filename = input("Enter the filename to download: ")
    filepath = os.path.join(local_folder, filename)
    
    if os.path.exists(filepath):
        overwrite = input(f"The file '{filename}' already exists. Do you want to overwrite it? (yes/no): ")
        if overwrite.lower() != 'yes':
            print("Download canceled.")
            return
    
    command = f'DOWNLOAD {filename}'
    client_socket.send(command.encode('utf-8'))
    
    try:
        status_code, response = recv_response(client_socket)
        print(f"[STATUS : {status_code}] \n[RESPONSE]{response.split()[0]}")
        if status_code == STATUS_FILE_NOT_FOUND.split()[0]:
            print("Error:", response)
        elif status_code == STATUS_OK.split()[0]:
            filesize = int(response.split()[1])
            with open(filepath, 'wb') as f:
                bytes_received = 0
                while bytes_received < filesize:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_received += len(chunk)
            print("File downloaded successfully.")
        else:
            print("Unexpected response:", response)
    except Exception as e:
        print(f"An error occurred while downloading: {e}")

def start_client():
    username = input("Enter your username: ")
    create_local_folder(username)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except Exception as e:
        print(f"An error occurred while connecting to the server: {e}")
        return
    
    while True:
        print("\n1. Upload file\n2. List files and download\n3. Exit\n")
        choice = input("Enter choice: ")
        print();
        if choice == '1':
            upload_file(client_socket, username)
        elif choice == '2':
            list_files(client_socket)
            download_file(client_socket, username)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")
    
    client_socket.close()

if __name__ == "__main__":
    start_client()
