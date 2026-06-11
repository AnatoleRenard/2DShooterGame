import socket

#constants for Socket
MAX_RECV = 1024
ENCODING = "utf-8"

class Sock:
    def __init__(self, ip, port):
        self.ip   = ip
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            return self.receive()
        except socket.error as e:
            print(e)
    
    def receive(self):
        try:
            return self.sock.recv(MAX_RECV).decode(ENCODING)
        except socket.error as e:
            print(e)
    
    def send(self, message):
        try:
            self.sock.send(bytes(message, encoding=(ENCODING)))
        except socket.error as e:
            print(e)

    def close(self):
        self.sock.close()