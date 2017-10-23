from core.modules.base import Program
from core.modules.console import print
from network.modules import tor


class FingerprinTOR(Program):
    """Retrieves descriptive information from hidden service addresses (via .onion descriptors)."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("target", type=str, help="Target hidden service's address.")
    
    def run(self):
        process = None
        if not tor.pids():
            print("[i] Tor is actually not running, starting a new temporary instance ...", color = "yellow")
            process = tor.Tor()
            process.start(False, " -  ")
            print()
        service = tor.HiddenService(self.arguments.target)
        print("[i] Hidden Service Descriptive Info.:")
        print(f" -  Publish Date & Time: {service.published}")
        print(f" -  Descriptor Identifier: {service.descriptor_id}")
        print(f" -  Descriptor Hash: {service.secret_id_part}")
        print(f" -  Descriptor Version: {service.version}")
        print(f" -  Supported Versions: {', '.join(str(v) for v in service.protocol_versions)}")
        print(" -  Permanent Key: ")
        print("    " + service.permanent_key.replace("\n", "\n    "), dark = True)
        print(" -  Signature: ")
        print("    " + service.signature.replace("\n", "\n    "), dark = True)
        print(" -  Introduction Points:")
        print(f"      {' Identifier '.center(32, '-')}  {' Address '.center(21, '-')}")
        for introduction_point in sorted(service.introduction_points(), key=lambda x: x.identifier):
            score = status = None
            print(f"    - {introduction_point.identifier}: " + f"{introduction_point.address}:{introduction_point.port}", dark = True)
        if process:
            process.exit()
