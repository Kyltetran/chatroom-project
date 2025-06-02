import socket

SERVER = '127.0.0.1'
PORT = 8888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

try:
    while True:
        msg = input("You: ")
        client.send(msg.encode())
except KeyboardInterrupt:
    client.close()
