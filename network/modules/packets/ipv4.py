import struct, socket, random
from ctypes import Structure, c_ubyte, c_ushort, c_ulong
from enum import Enum


class DSCP(Enum):
    #Default Forwarding
    DF = 0
    
    #AssuredForwarding
    ##Class 1
    AF11 = 10 #Low drop probability
    AF12 = 12 #Med drop probability
    AF13 = 14 #High drop probability
    ##Class 2
    AF21 = 18 #Low drop probability
    AF22 = 20 #Med drop probability
    AF23 = 22 #High drop probability
    ##Class 3
    AF31 = 26 #Low drop probability
    AF32 = 28 #Med drop probability
    AF33 = 30 #High drop probability
    ##Class 4
    AF41 = 34 #Low drop probability
    AF42 = 36 #Med drop probability
    AF43 = 38 #High drop probability
    
    #VoiceAdmit
    VA0 = 44
    
    #ExpeditedForwarding
    EF0 = 46
    
    #ClassSelector
    CS0 = 0  # Default
    CS1 = 8  # Scavenger
    CS2 = 16 # OAM
    CS3 = 24 # Signaling
    CS4 = 32 # Realtime
    CS5 = 40 # Broadcast video
    CS6 = 48 # Network control
    CS7 = 56

class ECN(Enum):
    NonECT = 0b00 # Non ECN-Capable Transport, Non-ECT
    ECT = (0b10,  # ECN Capable Transport, ECT(0)
           0b01)  # ECN Capable Transport, ECT(1)
    CE = 0b11     # Congestion Encountered, CE

class IPv4(Structure):
    class Options(Structure):
        class Classes(Enum):
            control = 0
            debugging = 2
        
        _fields_ = [("_copied", c_ubyte, 1),
                    ("_opt_class", c_ubyte, 2),
                    ("opt_number", c_ubyte, 5),
                    ("opt_length", c_ubyte, 8)]
        def __new__(self, buffer: bytes = b""):
            return self.from_buffer_copy(buffer[:2] if isinstance(buffer, bytes) else buffer)
        
        def __init__(self, buffer: bytes = b""):
            super().__init__()
            self.copied = bool(self._copied)
            self.option_class = self._opt_class
            if self._opt_class in self.Classes.__members__:
                self.option_class = {v.value: k for k, v in self.Classes.__members__.items()}[self._opt_class]
            self.data = buffer[2:]
        
        def __repr__(self):
            return f"Options(copied={self.copied}, opt_class={self.option_class}, opt_number={self.opt_number}, opt_length={self.opt_length}, opt_data={self.data})"
    
    protocols = {0x00: "HOPOPT",    0x01: "ICMP",        0x02: "IGMP",
                 0x03: "GGP",       0x04: "IP-in-IP",    0x05: "ST",
                 0x06: "TCP",       0x07: "CBT",         0x08: "EGP",
                 0x09: "IGP",       0x0A: "BBN-RCC-MON", 0x0B: "NVP-II",
                 0x0C: "PUP",       0x0D: "ARGUS",       0x0E: "EMCON",
                 0x0F: "XNET",      0x10: "CHAOS",       0x11: "UDP",
                 0x12: "MUX",       0x13: "DCN-MEAS",    0x14: "HMP",
                 0x15: "PRM",       0x16: "XNS-IDP",     0x17: "TRUNK-1",
                 0x18: "TRUNK-2",   0x19: "LEAF-1",      0x1A: "LEAF-2",
                 0x1B: "RDP",       0x1C: "IRTP",        0x1D: "ISO-TP4",
                 0x1E: "NETBLT",    0x1F: "MFE-NSP",     0x20: "MERIT-INP",
                 0x21: "DCCP",      0x22: "3PC",         0x23: "IDPR",
                 0x24: "XTP",       0x25: "DDP",         0x26: "IDPR-CMTP",
                 0x27: "TP++",      0x28: "IL",          0x29: "IPv6",
                 0x2A: "SDRP",      0x2B: "IPv6-Route",  0x2C: "IPv6-Frag",
                 0x2D: "IDRP",      0x2E: "RSVP",        0x2F: "GREs",
                 0x30: "DSR",       0x31: "BNA",         0x32: "ESP",
                 0x33: "AH",        0x34: "I-NLSP",      0x35: "SWIPE",
                 0x36: "NARP",      0x37: "MOBILE",      0x38: "TLSP",
                 0x39: "SKIP",      0x3A: "IPv6-ICMP",   0x3B: "IPv6-NoNxt",
                 0x3C: "IPv6-Opts", 0x3E: "CFTP",        0x40: "SAT-EXPAK",
                 0x41: "KRYPTOLAN", 0x42: "RVD",         0x43: "IPPC",
                 0x45: "SAT-MON",   0x46: "VISA",        0x47: "IPCU",
                 0x48: "CPNX",      0x49: "CPHB",        0x4A: "WSN",
                 0x4B: "PVP",       0x4C: "BR-SAT-MON",  0x4D: "SUN-ND",
                 0x4E: "WB-MON",    0x4F: "WB-EXPAK",    0x50: "ISO-IP",
                 0x51: "VMTP",      0x52: "SECURE-VMTP", 0x53: "VINES",
                 0x54: "TTP",       0x54: "IPTM",        0x55: "NSFNET-IGP",
                 0x56: "DGP",       0x57: "TCF",         0x58: "EIGRP",
                 0x59: "OSPF",      0x5A: "Sprite-RPC",  0x5B: "LARP",
                 0x5C: "MTP",       0x5D: "AX.25",       0x5E: "OS",
                 0x5F: "MICP",      0x60: "SCC-SP",      0x61: "ETHERIP",
                 0x62: "ENCAP",     0x64: "GMTP",        0x65: "IFMP",
                 0x66: "PNNI",      0x67: "PIM",         0x68: "ARIS",
                 0x69: "SCPS",      0x6A: "QNX",         0x6B: "A/N",
                 0x6C: "IPComp",    0x6D: "SNP",         0x6E: "Compaq-Peer",
                 0x6F: "IPX-in-IP", 0x70: "VRRP",        0x71: "PGM",
                 0x73: "L2TP",      0x74: "DDX",         0x75: "IATP",
                 0x76: "STP",       0x77: "SRP",         0x78: "UTI",
                 0x79: "SMP",       0x7A: "SM",          0x7B: "PTP",
                 0x7C: "IS-IS",     0x7D: "FIRE",        0x7E: "CRTP",
                 0x7F: "CRUDP",     0x80: "SSCOPMCE",    0x81: "IPLT",
                 0x82: "SPS",       0x83: "PIPE",        0x84: "SCTP",
                 0x85: "FC",        0x8A: "manet",       0x87: "Mobility Header",
                 0x88: "UDPLite",   0x89: "MPLS-in-IP",  0x86: "RSVP-E2E-IGNORE",
                 0x8B: "HIP",       0x8C: "Shim6",       0x8D: "WESP",
                 0x8E: "ROHC"}
    
    _fields_ = [("ihl", c_ubyte, 4),
                ("version", c_ubyte, 4),
                ("raw_dscp", c_ubyte, 6),
                ("raw_ecn", c_ubyte, 2),
                ("raw_total_length", c_ushort),
                ("raw_identification", c_ushort),
                ("raw_flags", c_ushort, 3),
                ("fragment_offset", c_ushort, 13),
                ("time_to_live", c_ubyte),
                ("raw_protocol", c_ubyte),
                ("raw_checksum", c_ushort),
                ("raw_source", c_ulong),
                ("raw_destination", c_ulong)]
    
    def __new__(self, buffer: bytes = b""):
        return self.from_buffer_copy(buffer[:20])
    
    def __init__(self, buffer: bytes = b""):
        super().__init__()
        self.data_offset = self.ihl * 4
        
        self.raw_buffer = buffer
        self.raw_header = buffer[:self.data_offset]
        
        phbs = {v.value: k for k, v in DSCP.__members__.items()}
        self.dscp = phbs[self.raw_dscp] if self.raw_dscp in phbs else "Unknown PHB"
        self.ecn = "Non-ECT" if self.raw_ecn is 0 else ("ECT(0)" if self.raw_ecn is 2 else ("ECT(1)" if self.raw_ecn is 1 else "CE"))
        self.differentiated_services = (self.dscp, self.ecn)
        self.total_length = socket.ntohs(self.raw_total_length)
        self.identification = socket.ntohs(self.raw_identification)
        self.flags = {0: self.raw_flags&1, 1: self.raw_flags&2, 2: self.raw_flags&4}
        self.protocol = self.protocols[self.raw_protocol] if self.raw_protocol in self.protocols else "Unknown"
        self.checksum = socket.ntohs(self.raw_checksum)
        self.source = socket.inet_ntoa(struct.pack("<L", self.raw_source))
        self.destination = socket.inet_ntoa(struct.pack("<L", self.raw_destination))
        
        self.raw_options = b""
        self.options = None
        if self.ihl > 5:
            self.raw_options = buffer[0x14:self.data_offset]
            self.options = self.options = self.Options(self.raw_options)#self.parse_options(self.raw_options)
        self.data = buffer[self.data_offset:]
    
    def __len__(self):
        return len(self.raw_buffer)
    
    def __repr__(self):
        flags_set = dict(filter(lambda x: x[1] != 0, self.flags.items()))
        flags = []
        if 1 in flags_set:
            flags.append("Don't Fragment (DF)")
        if 2 in flags_set:
            flags.append("More Fragments (MF)")
        return "\n".join([f"[IPv{self.version}] [Proto.{self.raw_protocol} ({self.protocol})] {self.source} -> {self.destination}",
                          f"     - Internet Header Length (IHL). . : {self.ihl * 4} bytes (0x{self.ihl:02x})",
                          f"     - Differentiated Services (DS) . .: {', '.join(self.differentiated_services)} (DSCP: 0x{self.raw_dscp:02x}, ECN: 0x{self.raw_ecn:01x})",
                          f"     - Total Length. . . . . . . . . . : {self.total_length} bytes",
                          f"     - Identification (ID). . . . . . .: 0x{self.identification:04x} ({self.identification})",
                          f"     - Flags:. . . . . . . . . . . . . : {', '.join(flags) if flags else None}",
                          f"     - Fragment Offset. . . . . . . . .: 0x{self.fragment_offset:04x} ({self.fragment_offset})",
                          f"     - Time to Live (TTL). . . . . . . : 0x{self.time_to_live:02x} ({self.time_to_live})",
                          f"     - Header Checksum. . . . . . . . .: 0x{self.checksum:04x} ({'NOT CALCULATED' if self.checksum is 0 else ('CORRECT' if self.check_sum(self.raw_header) is 0 else 'INCORRECT')})",
                          f"     - Options . . . . . . . . . . . . : {self.options}"])
    
    @staticmethod
    def check_sum(data, udp: bool = False):
        s = 0
        w = 0
        for i in range(0, len(data), 2):
            w = data[i] + (data[i+1] << 8)
            s = ((s + w) & 0xFFFF) + ((s + w) >> 16)
        return ~s & 0xFFFF
    
    @staticmethod
    def parse_options(raw_options: bytes):
        # Beautiful version of https://github.com/kisom/pypcapfile/blob/master/pcapfile/protocols/network/ip.py
        options = {}
        index = 0
        left = len(raw_options)
        while left:
            type = raw_options[index]
            if type is 0: # end
                break
            elif type is 1:  # NOP
                index += 1
                left -= 1
                continue
            
            if left < 2:
                break # invalid
            length = raw_options[index + 1]
            if length < 2 or length > left:
                break # invalid
            
            # Custom options parsing goes here
            if type is 0x55:
                if length < 1 + 1 + 2 + 4 + 8:
                    break # invalid
                _, _, _, _, options["uat"] = struct.unpack("!BBHIQ", raw_options[:16])
            
            index += length
            left -= length
        return options

