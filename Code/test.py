import socket

HOST = 'localhost'
PORT = 6666

try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((HOST, PORT))
    print("Connection successful!")
except ConnectionRefusedError:
    print(f"Connection refused. Check if the server at {HOST}:{PORT} is running.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    socket.close()
