from core.modules.base import Program
from core.modules.console import print
import dns.query, dns.zone
import argparse, socket


class DNSZT(Program):
    """Request a zone transfer (AXFR Query) from a DNS server."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("zone", type=str, help="The name of the zone to transfer.")
        self.parser.add_argument("-w", "--where", type=str, default="", help="String containing an IPv4 or IPv6 address where to send the message.")
        self.parser.add_argument("-p", "--port", type=int, default=53, help="The port to which to send the message. The default is 53.")
        self.parser.add_argument("-s", "--source", type=str, default=None, help="Source address. The default is the wildcard address.")
        self.parser.add_argument("-sP", "--source-port", type=int, default=0, help="The port from which to send the message. The default is 0.")
        self.parser.add_argument("-t", "--timeout", type=int, default=None, help="The number of seconds to wait for each response message.")
        self.parser.add_argument("-l", "--lifetime", type=float, default=None, help="The total number of seconds to spend doing the transfer. If None, the default, then there is no limit on the time the transfer may take.")
        self.parser.add_argument("-u", "--use-udp", type=bool, default=False, help="Use UDP (only meaningful for IXFR).")
        self.parser.add_argument("--rdtype", type=str, default="AXFR", help="The type of zone transfer. The default is \"AXFR\".")
        self.parser.add_argument("--rdclass", type=str, default="IN", help="The class of the zone transfer. The default is \"IN\".")
        self.parser.add_argument("--af", "--address-family", type=str, default="AF_INET", help="the address family to use. The default is None, which causes the address family to use to be inferred from the form of where. If the inference attempt fails, AF_INET is used.")
        self.parser.add_argument("--serial", type=int, default=None, help="The SOA serial number to use as the base for an IXFR diff sequence (only meaningful if rdtype == \"IXFR\").")
        self.parser.add_argument("--keyalgorithm", type=str, default=None, help="The TSIG algorithm to use; defaults to \"{}\".".format(str(dns.tsig.default_algorithm)))
        self.parser.add_argument("--relativize", type=bool, default=True, help="If True, all names in the zone will be relativized to the zone origin.")
        self.parser.add_argument("--check-origin", type=bool, default=True, help="Should sanity checks of the origin node be done? The default is True.")
        self.parser.add_argument("-e", "--export", type=argparse.FileType("wb"), help="Export DNS Zone.")
    
    def run(self):
        (zone, where, port,
         source, source_port,
         timeout, lifetime, use_udp,
         rdtype, rdclass, af,
         serial, keyalgorithm, relativize,
         check_origin, export) = (getattr(self.arguments, name) for name in
                                  ["zone", "where", "port", "source", "source-port",
                                   "timeout", "lifetime", "use-udp",
                                   "rdtype", "rdclass", "address-family",
                                   "serial", "keyalgorithm", "relativize",
                                   "check-origin", "export"])
        if not where:
            where = zone
        where = socket.gethostbyname(where)
        
        if rdtype not in [type for type in dir(dns.rdatatype) if type.isupper()]:
            raise ValueError(f"Unknown or invalid DNS Rdata Type \"{rdtype}\" ...")
        rdtype = getattr(dns.rdatatype, rdtype)
        
        if rdclass not in [type for type in dir(dns.rdataclass) if type.isupper()]:
            raise ValueError(f"Unknown or invalid DNS Rdata Class \"{rdclass}\" ...")
        rdclass = getattr(dns.rdataclass, rdclass)
        
        if af not in [i for i in dir(socket) if i.startswith("AF_")]:
            raise ValueError(f"Unknown or invalid Address Family \"{af}\" ...")
        address_family = int(getattr(socket, af))
        
        if keyalgorithm and keyalgorithm not in [alg for alg in dir(dns.tsig) if alg.startswith("HMAC_")]:
            raise ValueError(f"Unknown or invalid TSIG Algorithm \"{keyalgorithm}\" ...")
        keyalgorithm = dns.tsig.default_algorithm if not keyalgorithm else getattr(dns.tsig, keyalgorithm)
        
        
        config = {"query": {"zone": zone, "where": where, "port": port, "source_port": source_port, "timeout": timeout, "lifetime": lifetime, "use_udp": use_udp},
                  "zone": {"check_origin": check_origin, "relativize": relativize}}
        config["query"].update({"rdtype": rdtype, "rdclass": rdclass, "af": address_family, "serial": serial, "keyalgorithm": keyalgorithm, "relativize": relativize})
        
        if source:
            config["query"]["source"] = source
        
        zone = dns.zone.from_xfr(dns.query.xfr(**config["query"]), **config["zone"]).to_text()
        if export:
            export.write(zone)
        print(zone.decode("ascii"), dark = True)
