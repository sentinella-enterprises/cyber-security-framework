from network.modules import tor
from core.modules import base
from core.modules.console import print
import argparse


__all__ = ["EPH_HS"]

class EPH_HS(base.Program):
    """Ephemeral Hidden Server (EPH-HS) management program."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("-l", "--list", action="store_true", help="List active hidden services.")
        self.parser.add_argument("-c", "--close", nargs="+", help="Discontinue the specified hidden service.")
        self.parser.add_argument("-p", "--ports", nargs="+", help="Hidden service port or map of hidden service port to their targets.")
        self.parser.add_argument("-d", "--discard-key", action="store_true", help="Avoid providing the key back in our response.")
        self.parser.add_argument("-k", "--private-key", type=argparse.FileType(), default=None, help="Key for the service to use.")

    def run(self):
        try:
            if not tor.pids():
                print("[i] Tor is actually not running, starting a new instance ...", color = "yellow")
                Tor = tor.Tor()
                Tor.start(False, " -  ")
                print()
            controller = tor.Controller()
            if self.arguments.list:
                ehs_list = sorted(controller.list_ephemeral_hidden_services([], detached=True))
                num = len(ehs_list)
                print(f"[i] There {'is' if num == 1 else 'are'} {num or 'no'} ephemeral hidden service{'' if num == 1 else 's'} running at the momment.")
                for address in ehs_list:
                    hs = tor.HiddenService(address, controller)
                    print(f" -  {hs.address} ({hs.descriptor_id})", dark = True)
            elif self.arguments.close:
                for address in sorted(set(self.arguments.close)):
                    if address.endswith(".onion"):
                        address = address.split(".")[0]
                    try:
                        hs = tor.HiddenService(address, controller)
                        discontinued = controller.remove_ephemeral_hidden_service(address)
                        print(f"[+] {hs.address} ({hs.descriptor_id}):", ("Hidden Service not running in the first place ...", "yellow") if not discontinued else "Hidden Service successfully discontinued and closed.")
                    except Exception as e:
                        print(f"[!] {address}.onion: {e}", color = "red")
            elif self.arguments.ports:
                ports = {}
                for port in self.arguments.ports:
                    if "=" in port:
                        number, target = port.split("=", 1)
                        ports[int(number)] = target
                    else:
                        ports[int(port)] = int(port)
                print("[i] Creating Hidden Service ...")
                ehs = tor.EphemeralHiddenService(ports, self.arguments.discard_key, True, self.arguments.private_key, controller)
                print(f"[i] Hidden Service running on {ehs.address}:")
                print(f" -  Publish Date & Time: {ehs.published}")
                print(f" -  Descriptor Identifier: {ehs.descriptor_id}")
                print(f" -  Descriptor Hash: {ehs.secret_id_part}")
                print(f" -  Descriptor Version: {ehs.version}")
                print(" -  Permanent Key: ")
                print("    " + ehs.permanent_key.replace("\n", "\n    "), dark=True)
                print(" -  Signature: ")
                print("    " + ehs.signature.replace("\n", "\n    "), dark=True)
                print(" -  Introduction Points:")
                print(f"      {' Identifier '.center(32, '-')}  {' Address '.center(21, '-')}", dark=True)
                for introduction_point in sorted(ehs.introduction_points(), key=lambda x: x.identifier):
                    score = status = None
                    print(f"    - {introduction_point.identifier}: " + f"{introduction_point.address}:{introduction_point.port}", dark=True)
                print()
                print(" -  HS Port Map:")
                for port, target in ports.items():
                    print(f"    - {port}: {target}", dark=True)
            else:
                parser.print_help()
        except Exception as e:
            print(f"[!] {type(e).__name__}:", color = "red")
            print(f" -  {e}", color = "red", dark = True)
        except KeyboardInterrupt:
            print("[!] Keyboard Interrupted!", color = "red")
