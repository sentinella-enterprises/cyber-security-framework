from network.modules import socket
from crypto.modules import hkbit
from core.modules import base
import threading, argparse, socks, sys, os


__all__ = ["Client", "Program"]

class Client(socks.socksocket):
    def __init__(self, key):
        super().__init__()
        self.set_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9150)
        self.settimeout(10)
        self.key = key
    
    def crypt(self, data: bytes):
        self.key.seek(0)
        crypted = hkbit.crypt(data, self.key.read(len(data)))[0]
        self.key.seek(0)
        return crypted
    
    def send(self, data: bytes):
        return super().send(self.crypt(data))
    
    def recv(self, buffer: int = 0xFFFF):
        return self.crypt(super().recv(buffer))
    
    def interact(self):
        shut = False
        def _input():
            while not self._closed:
                try:
                    self.send(input().encode("ascii") + b"\r\n")
                except (EOFError, KeyboardInterrupt):
                    shut = True
                    self.shutdown(socket.SHUT_RDWR)
                    self.close()
                    sys.exit()
        threading.Thread(target=_input, daemon = True).start()
        while not shut:
            try:
                data = self.recv(0xFFFF)
                if not data:
                    break
                print(data.decode("ascii", errors="backslashreplace"))
            except KeyboardInterrupt:
                shut = True
        self.shutdown(socket.SHUT_RDWR)
        self.close()

class Program(base.Program):
    """Basic HKBit based chat client."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("address", help = "Target server's address.")
        self.parser.add_argument("-p", "--port", default = 1337, type = int, help = "Target server's port.")
        self.parser.add_argument("key", type = argparse.FileType("rb"), help = "Server key file.")
    
    def run(self):
        try:
            c = Client(self.arguments.key)
            c.connect((self.arguments.address, self.arguments.port))
            c.interact()
        except KeyboardInterrupt as e:
            print(f"[!] {type(e).__name__}: {e}")
        except KeyboardInterrupt:
            pass
