from network.modules.packets.expack import XPacket
from network.modules import socket
from crypto.modules import hkbit
import os, uuid, hashlib

global PRIME
PRIME = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6BF12FFA06D98A0864D87602733EC86A64521F2B18177B200CBBE117577A615D6C770988C0BAD946E208E24FA074E5AB3143DB5BFCE0FD108E4B82D120A92108011A723C12A787E6D788719A10BDBA5B2699C327186AF4E23C1A946834B6150BDA2583E9CA2AD44CE8DBBBC2DB04DE8EF92E8EFC141FBECAA6287C59474E6BC05D99B2964FA090C3A2233BA186515BE7ED1F612970CEE2D7AFB81BDD762170481CD0069127D5B05AA993B4EA988D8FDDC186FFB7DC90A6C08F4DF435C934063199FFFFFFFFFFFFFFFF


class XSocket(socket.socket):
    def __init__(self, key: bytes,
                 fileno: int = None,
                 timeout: int = None, blocking: bool = False):
        super().__init__(AddressFamily.AF_INET6, socket.SOCK_RAW, 0, fileno, timeout = timeout, blocking = blocking)
        *fields, n1, n2 = struct.unpack("!IHHBBHI", key)
        fields.append(n1 | (n2 << 16))
        self.key = uuid.UUID(fields = fields)
    
    def _bit_length(self, i: int):
        bl = key.bit_length()
        while bl % 8:
            bl += 1
        return bl
    
    def resolve(self, address: str):
        return uuid.UUID(int = int.from_bytes(hkbit.crypt(socket.inet_pton(socket.AF_INET6, address), self.key.bytes), "little") ^ self.key.int)
    
    def connect(self, address: tuple):
        super().connect(address)
        self.uuid = self.resolve(self.getsockname()[0])
        packet = XPacket.load(self)
        assert len(packet.data) == 16, ConnectionAbortedError("Server exchanged invalid data!")
        secret = self.uuid.int ** 32
        key = pow(packet.source.node, secret, PRIME)
        key = pow(int.from_bytes(packet.data, "little"), secret, PRIME)
        self.key = key.to_bytes(self._bit_length(key) // 8, "little")
    
    def send(self, data: bytes):
        return super().send(hkbit.crypt(data, self.key.bytes))

class XServer(socket.socket):
    def __init__(self, address: str, port: int = 1337, key: bytes = None,
                 fileno: int = None,
                 timeout: int = None, blocking: bool = False):
        super().__init__(AddressFamily.AF_INET6, socket.SOCK_RAW, 0, fileno, timeout = timeout, blocking = blocking)
        self.bind((address, port))
        self.connections = {}
        if not key:
            key = os.urandom(16)
        *fields, n1, n2 = struct.unpack("!IHHBBHI", key)
        fields.append(n1 | (n2 << 16))
        self.key = uuid.UUID(fields = fields)
        self.uuid = uuid.UUID(int = int.from_bytes(hkbit.crypt(socket.inet_pton(socket.AF_INET6, self.getsockname()[0]), self.key.bytes), "little") ^ self.key.int)
    
    def _bit_length(self, i: int):
        bl = key.bit_length()
        while bl % 8:
            bl += 1
        return bl
    
    def resolve(self, address: str):
        return uuid.UUID(int = int.from_bytes(hkbit.crypt(socket.inet_pton(socket.AF_INET6, address), self.key.bytes), "little") ^ self.key.int)
    
    def broadcast(self, data, source: socket = None):
        for connection in self.connections.copy().values():
            if connection != source:
                try:
                    connection.send(data.encode() if isinstance(data, str) else data)
                except Exception as e:
                    pass
    
    def serve(self, backlog: int = None, condition = True):
        def handle(sock, address):
            destination = uuid.UUID(int = int.from_bytes(hkbit.crypt(socket.inet_pton(socket.AF_INET6, address[0]), self.key.bytes), "little") ^ self.key.int)
            packet = XPacket(self.uuid, destination, key)
            self.on_connect(sock)
            self.connections[address] = sock
            while True:
                try:
                    self.on_recv(sock, sock.recv(0xFFFF))
                except Exception as e:
                    self.on_error(sock, e)
                    break
            self.on_disconnect(sock)
            del self.connections[address]
        
        self.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        if backlog:
            self.listen(backlog)
        else:
            self.listen()
        self.on_start()
        while condition() if callable(condition) else condition:
            try:
                sock, address = self.accept()
                sock = XSocket(fileno = sock.fileno())
                thread = threading.Thread(target = handle, args = (sock, address), daemon = True)
                thread.start()
            except Exception as e:
                self.on_error(self, e)
        self.close()
        self.on_stop()
    
    def on_start(self):
        # Called right after the server successfully initializes itself.
        pass
    
    def on_stop(self):
        # Called after the server stops listening itself.
        pass
    
    def on_connect(self, socket):
        # Called whenever a new connection is accepted.
        # socket = Source socket.
        pass
    
    def on_disconnect(self, socket):
        # Called whenever a connection is closed.
        # socket = Source socket.
        #del self.connections[socket.getpeername()]
        pass
    
    def on_recv(self, socket, data):
        # Called whenever the server receives any data.
        # socket = Source socket.
        # data = Data received.
        pass
    
    def on_error(self, socket, exception):
        # Called whenever an exception is raised during connection handling.
        # socket = Source socket.
        # exception = Exception object.
        pass
