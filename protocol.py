# protocol.py

STATUS_OK = '200 OK'
STATUS_UPLOAD_SUCCESS = '201 Upload Success'  
STATUS_PARTIAL_CONTENT = '206 Partial Content'
STATUS_INVALID_COMMAND = '400 Invalid Command'
STATUS_PERMISSION_DENIED = '403 Permission Denied'
STATUS_FILE_NOT_FOUND = '404 Not Found'
STATUS_FILE_ALREADY_EXISTS = '409 File Already Exists'
STATUS_HASH_MISMATCH = '500 Hash Mismatch'
STATUS_INTERNAL_SERVER_ERROR = '500 Internal Server Error'


def send_response(client_socket, status_code, message=""):
    response = f"{status_code} {message}".encode('utf-8')
    client_socket.send(response)

def recv_response(client_socket):
    response = client_socket.recv(1024).decode('utf-8')
    status_code, message = response.split(' ', 1)
    return status_code, message
