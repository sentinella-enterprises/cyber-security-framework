from socket import *
import socks
import os, threading, urllib.parse


create_connection = socks.create_connection

class socksocket(socks.socksocket):
    def __init__(self, family: AddressFamily = AddressFamily.AF_INET, type: SocketKind = SocketKind.SOCK_STREAM, proto: int = 0, fileno: int = None,
                 timeout: int = None, blocking: bool = False, proxy: str = "", rdns: bool = True):
        super(socks.socksocket, self).__init__(family, type, proto, fileno)
        if proxy:
            proxy = urllib.parse.urlparse(proxy, scheme = "socks5")
            assert proxy.scheme.upper() in socks.PROXY_TYPES, ValueError(f"Invalid proxy type: {repr(proxy.scheme)}.")
            kwargs = {"addr": proxy.hostname, "rdns": rdns}
            if proxy.port: kwargs["port"] = proxy.port
            if proxy.username: kwargs["username"] = proxy.username
            if proxy.password: kwargs["password"] = proxy.password
            self.set_proxy(socks.PROXY_TYPES[proxy.scheme.upper()], **kwargs)
        self.settimeout(timeout)
        if blocking:
            self.setblocking(blocking)

class socket(socket):
    def __init__(self, family: AddressFamily = AddressFamily.AF_INET, type: SocketKind = SocketKind.SOCK_STREAM, proto: int = 0, fileno: int = None,
                 timeout: int = None, blocking: bool = False):
        # SOCKS enabled socket. In order for SOCKS to work, you must specify family=AF_INET and proto=0,
        # and the "type" argument must be either SOCK_STREAM or SOCK_DGRAM.
        # family = Socket Address Family.
        # type = Socket Kind.
        # proto = Target Protocol.
        # fileno = Socket file descriptor.
        # timeout = float, giving in seconds, or None. Setting a timeout of None disables
        #           the timeout feature and is equivalent to setting blocking = True.
        #           Setting a timeout of zero is the same as setting blocking = False.
        # blocking = Set the socket to blocking (flag is true) or non-blocking (false).
        #            blocking = True is equivalent to timeout = None;
        #            blocking = False is equivalent to timeout = 0.0.
        #self.context = None
        super(socket, self).__init__(family, type, proto, fileno)
        self.settimeout(timeout)
        if blocking:
            self.setblocking(blocking)
    
    # Set file-like functions to make our lives easier.
    read = socket.recv
    write = socket.send

class server(socket):
    def __init__(self, address: str, port: int, *args, **kwargs):
        # Adapted socket object for listening for incomming connections.
        # address = Source address which to bind on.
        # port = Source port which to bind on.
        # Other arguments are going to be passed to the socket object.
        super().__init__(*args, **kwargs)
        self.address, self.port = address, port
        self.bind((self.address, self.port))
        self.connections = {}
    
    def broadcast(self, data, source: socket = None):
        # Send `data` to all connected sockets other than `source`.
        # If `source` is set to None, no socket is going to be skipped.
        # All exceptions raised during the `send` process inside this function are ignored.
        for connection in self.connections.copy().values():
            if connection != source:
                try:
                    connection.send(data.encode() if isinstance(data, str) else data)
                except Exception as e:
                    pass
    
    def serve(self, backlog: int = None, condition = True):
        # Initializes the server and starts listening for incomming connections.
        # backlog: If backlog is specified, it must be
        #          at least 0 (if it is lower, it is set to 0); it specifies the number of
        #          unaccepted connections that the system will allow before refusing new
        #          connections. If not specified, a default reasonable value is chosen.
        # condition: Function or variable on which the server will base on to keep looping.
        #            Once this returns a negative value (False, 0, -1, "", [...])
        #            or is set to that, the server stops the loop and shuts itself down.
        def handle(sock, address):
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

class sniffer(socket):
    def __init__(self, address: str = "", port: int = 0, *args, **kwargs):
        # Adapted socket object for sniffing data.
        # address = Source address which to bind on.
        # port = Source port which to bind on (Irrelevant, at least on Windows).
        # Other arguments are going to be passed to the socket object.
        kwargs["type"] = SOCK_RAW
        super().__init__(*args, **kwargs)
        self.bind((address, port))
        if self.proto is IPPROTO_IP:
            self.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)
        
        if os.name == "nt":
            self.ioctl(SIO_RCVALL, RCVALL_ON)
    
    def close(self):
        if os.name == "nt":
            self.ioctl(SIO_RCVALL, RCVALL_OFF)
        super().close()
    
    def sniff(self, condition = True):
        # condition: Function or value on which the server will base on to keep looping.
        #            Once this returns a negative value (False, 0, -1, "", [...])
        #            or is set to that, the sniffer stops the loop and shuts itself down.
        self.on_start()
        while condition() if callable(condition) else condition:
            address = self.getsockname()
            try:
                data, address = self.recvfrom(0xFFFF)
                self.on_recv(address, data)
            except Exception as e:
                self.on_error(address, e)
        self.on_stop(self)
    
    def on_start(self):
        # Called when the sniffer starts running.
        pass
    
    def on_stop(self):
        # Called when the sniffer stops running.
        pass
    
    def on_recv(self, address, data):
        # Called whenever the sniffer receives any data.
        # address = Source address.
        # data = Data got.
        pass
    
    def on_error(self, address, exception):
        # Called whenever an exception is raised during packet receival.
        # address = Source address.
        # exception = Exception object.
        pass
