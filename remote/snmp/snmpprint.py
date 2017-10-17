from pysnmp.hlapi import *
from core.modules.base import Program
from core.modules.console import print


class SNMPPrint(Program):
    """SNMP data "walking" program."""
    requirements = {"pysnmp"}
    def __init__(self):
        super().__init__()
        self.parser.add_argument("target", type=str, help="Target address or hostname.")
        self.parser.add_argument("-p", "--port", type=int, default=161, help="Target SNMP port.")
        self.parser.add_argument("-c", "--community", type=str, default="public", help="Community name.")
        self.parser.add_argument("-g", "--get", nargs="+", type=str, help="Use getCmd for the object identities specified here against the target instead of using nextCmd.")
        self.parser.add_argument("-t", "--timeout", type=int, default=8, help="Response timeout in seconds.")
        self.parser.add_argument("-r", "--retries", type=int, default=5, help="Maximum number of request retries.")
        transports = self.parser.add_mutually_exclusive_group()
        transports.add_argument("-6", "--udp6", action="store_true", help="Use the UDP6 Transport.")
        transports.add_argument("-u", "--unix", action="store_true", help="Use the Unix Transport.")
    
    def run(self):
        transport = Udp6TransportTarget if self.arguments.udp6 else (UnixTransportTarget if self.arguments.unix else UdpTransportTarget)
        args = (SnmpEngine(), CommunityData(self.arguments.community, mpModel=0),
                transport((self.arguments.target, self.arguments.port), timeout=self.arguments.timeout, retries=self.arguments.retries),
                ContextData())
        response = (getCmd(*args, *[ObjectType(ObjectIdentity(obj)) for obj in self.arguments.get])
                    if self.arguments.get else
                    nextCmd(*args, ObjectType(ObjectIdentity("SNMPv2-MIB"))))
        record = next(response, None)
        while record:
            for value in record[-1]:
                print(value.prettyPrint(), dark = True)
            record = next(response, None)
