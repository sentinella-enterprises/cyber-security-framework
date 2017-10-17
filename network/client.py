from core.modules import base, console
from network.modules import socket
import sys, threading


class Client(base.Program):
    """Network Client."""
    def __init__(self):
        super().__init__()
        socket.add_argument_group(self.parser)
        self.parser.add_argument("-c", "--crlf", action = "store_true", help = "Use CRLF for EOL sequences.")
    
    def run(self):
        EOL = b"\r\n" if self.arguments.crlf else b"\n"
        kwargs = {"family": socket.AF_INET6 if self.arguments.ipv6 else socket.AF_INET,
                  "type": socket.SOCK_DGRAM if self.arguments.udp else socket.SOCK_STREAM,
                  "proto": self.arguments.protocol, "timeout": self.arguments.timeout, "blocking": self.arguments.blocking}
        
        data = b"\x00"
        client = socket.socket(**kwargs)
        client.connect((self.arguments.address, self.arguments.port))
        def _input():
            while not client._closed:
                data = client.recv(0xFFFF)
                if not data:
                    break
                console.print(data.decode("ascii", errors="backslashreplace"))
        threading.Thread(target=_input, daemon = True).start()
        while data:
            try:
                inpt = input().encode("ascii")
                client.send(inpt + (b"" if inpt.endswith(EOL) else EOL))
            except (EOFError, KeyboardInterrupt):
                break
        client.shutdown(socket.SHUT_RDWR)
        client.close()
