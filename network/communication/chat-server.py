from network.modules import socket
from crypto.modules import hkbit
from core.modules import base
import argparse, sys, os


__all__ = ["Server", "Program"]

class Server(socket.server):
    def __init__(self, address: str, port: int, key):
        super().__init__(address, port)
        self.key = key
        def send(sock, data: bytes):
            return sock._send(self.crypt(data))
        def recv(sock, buffer: int = 0xFFFF):
            return self.crypt(sock._recv(buffer))
        from socket import socket
        socket._send, socket._recv = socket.send, socket.recv
        socket.send = send
        socket.recv = recv
    
    def crypt(self, data: bytes):
        self.key.seek(0)
        crypted = hkbit.crypt(data, self.key.read(len(data)))[0]
        self.key.seek(0)
        return crypted
    
    def recv(self, buffer: int = 0xFFFF):
        return self.crypt(super().recv(buffer))
    
    def broadcast(self, data: bytes, source: socket.socket = None):
        if isinstance(data, str):
            data = data.encode("ascii", errors = "backslashreplace")
        super().broadcast(data, source)
    
    def on_start(self):
        print(f"[i] Server successfully initialized.")
        print(f" -  Listening on: {':'.join(map(str, self.getsockname()))}")
        print()
    
    def on_stop(self):
        print("[i] Server stopped listening (Socket closed).")
    
    def on_connect(self, sock):
        connections = len(self.connections)
        sock.send(b"[i] Successfully connected!")
        sock.send(f" -  There {'is' if connections == 1 else 'are'} {connections or 'no'} other client{'s' if connections != 1 else ''} here.".encode())
        self.broadcast(f"\r[*] {':'.join(map(str, sock.getpeername()))} Connected!")
    
    def on_disconnect(self, sock):
        self.broadcast(f"\r[-] {':'.join(map(str, sock.getpeername()))} Disconnected!")
    
    def on_recv(self, sock, data):
        if data:
            self.broadcast(f"\r[+] {':'.join(map(str, sock.getpeername()))}: {data.decode('ascii', errors='replace')}", sock)
    
    def on_error(self, sock, e):
        self.broadcast(f"\r[!] {':'.join(map(str, sock.getpeername()))} [{type(e).__name__}]: {e}")

class Program(base.Program):
    """Basic HKBit encrypted chat server."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("-k", "--key", type = argparse.FileType("rb"), help = "Key file.")
    
    def run(self):
        key = self.arguments.key
        if not key:
            key = open("./server.key", "wb+")
            key.write(os.urandom(0xFFFF))
            key.seek(0)
            print(f"[*] Key file generated and saved as {repr(key.name)}.")
        server = Server("127.0.0.1", 1337, key)
        server.serve()
        key.seek(0)
        key.close()
