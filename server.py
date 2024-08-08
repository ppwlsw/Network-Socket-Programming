# server.py

import socket, threading, os, hashlib
from protocol import (
    STATUS_OK, STATUS_FILE_NOT_FOUND, STATUS_INVALID_COMMAND,
    STATUS_HASH_MISMATCH, STATUS_FILE_ALREADY_EXISTS,
    STATUS_PERMISSION_DENIED, STATUS_INTERNAL_SERVER_ERROR,
    STATUS_UPLOAD_SUCCESS, send_response
)

SERVER_HOST = socket.gethostname()
SERVER_PORT = 12345
CENTRAL_FOLDER = 'central_folder'

if not os.path.exists(CENTRAL_FOLDER):
    os.makedirs(CENTRAL_FOLDER)

def list_files():
    return os.listdir(CENTRAL_FOLDER)

def handle_client(client_socket):
    while True: 
        try:
            command = client_socket.recv(1024).decode('utf-8')
            print(f"[COMMAND RECEIVE] {command}")
            if command.startswith('UPLOAD'):
                parts = command.split()
                if len(parts) < 4:
                    send_response(client_socket, STATUS_INVALID_COMMAND)
                    continue
                filename = " ".join(parts[1:-2])
                filesize = int(parts[-2])
                filehash = parts[-1]
                filepath = os.path.join(CENTRAL_FOLDER, filename)
                
                if os.path.exists(filepath):
                    send_response(client_socket, STATUS_FILE_ALREADY_EXISTS)
                    continue

                try:
                    received_hash = hashlib.sha256()
                    with open(filepath, 'wb') as f:
                        bytes_received = 0
                        while bytes_received < filesize:
                            chunk = client_socket.recv(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            received_hash.update(chunk)
                            bytes_received += len(chunk)
                    
                    received_hash_hex = received_hash.hexdigest()
                    if received_hash_hex == filehash:
                        send_response(client_socket, STATUS_UPLOAD_SUCCESS, "File uploaded and verified.")
                    else:
                        send_response(client_socket, STATUS_HASH_MISMATCH, "File upload failed due to hash mismatch.")
                        os.remove(filepath)
                except Exception as e:
                    send_response(client_socket, STATUS_INTERNAL_SERVER_ERROR, str(e))
                    if os.path.exists(filepath):
                        os.remove(filepath)

            elif command == 'LIST':
                try:
                    files = list_files()
                    file_list = "\n".join(files)
                    send_response(client_socket, STATUS_OK, file_list)
                except Exception as e:
                    send_response(client_socket, STATUS_INTERNAL_SERVER_ERROR, str(e))

            elif command.startswith('DOWNLOAD'):
                parts = command.split()
                if len(parts) < 2:
                    send_response(client_socket, STATUS_INVALID_COMMAND)
                    continue
                filename = parts[1]
                filepath = os.path.join(CENTRAL_FOLDER, filename)
                if os.path.exists(filepath):
                    try:
                        send_response(client_socket, STATUS_OK, f"{os.path.getsize(filepath)}")
                        with open(filepath, 'rb') as f:
                            while chunk := f.read(1024):
                                client_socket.send(chunk)
                    except Exception as e:
                        send_response(client_socket, STATUS_INTERNAL_SERVER_ERROR, str(e))
                else:
                    send_response(client_socket, STATUS_FILE_NOT_FOUND)
            else:
                send_response(client_socket, STATUS_INVALID_COMMAND)
        except ConnectionResetError:
            break
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
