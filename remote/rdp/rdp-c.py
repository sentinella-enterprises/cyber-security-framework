from core.modules.console import print
from core.modules.base import Program
import argparse


class RDPc(Program):
    """Create simple RDP connection files."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("target", help="Target address (hostname or ip-address).")
        self.parser.add_argument("-p", "--port", type=int, default=3389, help="Target port (defaults to 3389).")
        self.parser.add_argument("-o", "--output", type=argparse.FileType("w"), help="Output file (defaults to '{target}-{port}.rdp').")
    
    def run(self):
        file = self.arguments.output or open(f"{self.arguments.target}-{self.arguments.port}.rdp", "w")
        file.write("\n".join(["screen mode id:i:2", "use multimon:i:0", "desktopwidth:i:800",
                              "desktopheight:i:600", "session bpp:i:32", "winposstr:s:0,3,0,0,800,600",
                              "compression:i:1", "keyboardhook:i:2", "audiocapturemode:i:0",
                              "videoplaybackmode:i:1", "connection type:i:2", "displayconnectionbar:i:1",
                              "disable wallpaper:i:1", "allow font smoothing:i:0", "allow desktop composition:i:0",
                              "disable full window drag:i:1", "disable menu anims:i:1", "disable themes:i:0",
                              "disable cursor setting:i:0", "bitmapcachepersistenable:i:1",
                              f"full address:s:{self.arguments.target}:{self.arguments.port}", "audiomode:i:0",
                              "redirectprinters:i:1", "redirectcomports:i:0", "redirectsmartcards:i:1",
                              "redirectclipboard:i:1", "redirectposdevices:i:0", "redirectdirectx:i:1",
                              "autoreconnection enabled:i:1", "authentication level:i:0",
                              "prompt for credentials:i:0", "negotiate security layer:i:1",
                              "remoteapplicationmode:i:0", "alternate shell:s:",
                              "shell working directory:s:", "gatewayhostname:s:", "gatewayusagemethod:i:4",
                              "gatewaycredentialssource:i:4", "gatewayprofileusagemethod:i:0",
                              "promptcredentialonce:i:1", "use redirection server name:i:0",
                              "enablecredsspsupport:i:0"]))
        print("[i] Successfully created RDP connection file!")
        print(f" -  {filename}", dark = True)
