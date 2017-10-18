from core.modules.base import Program
from core.modules.console import print
from network.modules import socket
import re


class Whois(Program):
    """Query & output whois data."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("query", type = str, help = "Query to be sent to the whois server.")
        self.parser.add_argument("-s", "--server", default = "whois.iana.org", type=str, help="Whois server address (defaults to 'whois.iana.org').")
        self.parser.add_argument("-p", "--port", default = 43, type=int, help="Whois server port (defaults to 43).")
        socket.add_argument_group(self.parser)
    
    def query(self, server: str, port: int):
        kwargs = {"family": socket.AF_INET6 if self.arguments.ipv6 else socket.AF_INET,
                  "type": socket.SOCK_DGRAM if self.arguments.udp else socket.SOCK_STREAM,
                  "proto": self.arguments.protocol, "timeout": self.arguments.timeout, "blocking": self.arguments.blocking}
        sock = socket.socket(**kwargs)
        sock.connect((server, port))
        sock.send(f"{self.arguments.query}\r\n".encode())
        
        data = chunk = sock.recv(0xFFF)
        while chunk:
            chunk = sock.recv(0xFFF)
            data += chunk
        return data.decode("utf-8", errors="replace")
    
    def run(self):
        answer = self.query(self.arguments.server, self.arguments.port)
        server = re.search("whois\: (.*)", answer)
        if server: answer = self.query(server.groups()[0].strip(), 43)
        for line in answer.split("\n"):
            print(line.strip(), dark = line.startswith("%"))
