import netaddr
from core.modules.base import Program
from core.modules.console import print


class MACLookup(Program):
    """IEEE EUI (Extended Unique Identifier) lookup tool.
       Both EUI-48 (used for layer 2 MAC addresses) and EUI-64 are supported.
       
       Input parsing for EUI-48 addresses is flexible, supporting many MAC
       variants."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("mac", type = str, metavar = "ADDRESS", help="Target MAC Address.")
    
    def run(self):
        mac = netaddr.EUI(int(self.arguments.mac) if self.arguments.mac.isdigit() else self.arguments.mac)
        info = mac.info["OUI"]
        print(f"[i] Media Access Control (MAC) Address Lookup Results For {mac}:")
        print(f" -  Extended Unique Identifier 64:       {mac.eui64()}", dark=True)
        print(f" -  Modified EUI64 Address:              {mac.modified_eui64()}", dark=True)
        print(f" -  Individual Access Block [IAB]:       {mac.iab if mac.is_iab() else 'Not an IAB'}", dark=True)
        print(f" -  Organizationally Unique Identifier:  {mac.oui}", dark=True)
        print(f" -  Extended Identifier [EI]:            {mac.ei}", dark=True)
        print(f" -  Local Link IPv6 Address:             {mac.ipv6_link_local()}", dark=True)
        print(f" -  Vendor Info:")
        print(f"    - Organization: {info['org']}", dark=True)
        print( "    - Address:      {}".format("\n                    ".join(info["address"])), dark=True)
        print(f" -  OUI Info:")
        print(f"    - Version: {mac.version}", dark=True)
        print(f"    - Offset:  {info['offset']}", dark=True)
        print(f"    - Size:    {info['size']}", dark=True)
        print(f"    - IDX:     {info['idx']}", dark=True)
        print(f"    - OUI:     {info['oui']}", dark=True)
        print(f" -  Packed Address:          {mac.packed}", dark=True)
        print(f" -  Hexadecimal Address:     {hex(mac)}", dark=True)
        print(f" -  48-bit Positive Integer: {mac.value}", dark=True)
        print(f" -  Octets:                  {', '.join(str(n) for n in mac.words)}", dark=True)
