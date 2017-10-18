from network.modules.packets import IPv4
from network.modules import socket
from core.modules.console import print, hexdump
from core.modules import base
from datetime import datetime
from impacket import ImpactDecoder


class Sniffer(socket.sniffer):
    decoder = ImpactDecoder.IPDecoder()
    def __init__(self, address: str = "", **kwargs):
        try:
            socket.inet_pton(socket.AF_INET6, address)
            ipv6 = True
        except OSError:
            ipv6 = False
        super().__init__(address or socket.gethostname(), family = socket.AF_INET6 if ipv6 else socket.AF_INET, **kwargs)
    
    def on_start(self):
        print(datetime.now().strftime("[i] Started sniffing %A, %B %d at %H:%M:%S!"))
    
    def on_stop(self):
        print(datetime.now().strftime("[i] Stopped sniffing %A, %B %d at %H:%M:%S!"))
    
    def on_recv(self, address, data):
        packet = self.decoder.decode(data)
        print(packet)
        """packet = IPv4(data)
        print(packet)
        hexdump(packet.data, prefix = "       ")
        if packet.version != 4:
            print(f"     - Invalid Version field: {packet.version}", color = "red", dark = True)
        if packet.ihl < 5:
            print(f"     - Invalid Internet Header Length (IHL) field: {packet.ihl} (Must be at least 5)", color = "red", dark = True)
        if packet.total_length < 20:
            print(f"     - Invalid Total Length field: {packet.total_length}", color = "red", dark = True)
        if packet.time_to_live < 1:
            print(f"     - Invalid/Exceeded Time To Live (TTL) field: {packet.time_to_live}", color = "red", dark = True)
        if packet.check_sum(packet.raw_header) != 0 and packet.checksum != 0:
            print(f"     - Incorrect Header Checksum: {packet.checksum:04x}", color = "red", dark = True)
        if packet.source != address[0]:
            print(f"     - Spoofed Source Address: {packet.source} (Original is {repr(address[0])})", color = "red", dark = True)
        print()"""
    
    def on_error(self, address, exception):
        raise exception
        print(f"[!] {type(exception).__name__} [{':'.join(map(str, address))}]:", color = "red")
        print(f" -  {exception}", color = "red", dark = True)

class Program(base.Program):
    """Sniff and parse IPv4 traffic reporting anomalies sent from and to the interface of the specified address."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("-a", "--address", type = str, default = socket.gethostname(), help = "Target address.")
        socket.add_argument_group(self.parser)
    
    def run(self):
        kwargs = {"proto": self.arguments.protocol, "timeout": self.arguments.timeout, "blocking": self.arguments.blocking}
        sniffer = Sniffer(self.arguments.address, **kwargs)
        sniffer.sniff()
