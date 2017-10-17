from core.modules import base
from crypto.modules import hkbit
import argparse, sys, os


class HKBit(base.Program):
    """Encrypt & Decrypt files using binary binary inversion cryptography based on hex-digits as "index keys" for the inversion process."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("input", type = argparse.FileType("rb"), help = "Input file.")
        self.parser.add_argument("-o", "--output", type = argparse.FileType("wb"), default = sys.stdout.buffer, help = "Output file.")
        self.parser.add_argument("-k", "--key", type = argparse.FileType("ab+"), default = open("./hkbit.key", "ab+"), help = "Key file.")
    
    def run(self):
        self.arguments.key.seek(0)
        self.arguments.key.size = os.fstat(self.arguments.key.fileno()).st_size
        if not self.arguments.key.size:
            self.arguments.key.write(os.urandom(0xFFFF))
            self.arguments.key.size = 0xFFFF
        self.arguments.key.seek(0)
        
        chunk = self.arguments.input.read(0xFFF)
        ran = 0
        while chunk:
            if ran >= self.arguments.key.size:
                ran = 0
                self.arguments.key.seek(0)
            self.arguments.output.write(hkbit.crypt(chunk, self.arguments.key.read(0xFFF))[0])
            self.arguments.output.flush()
            chunk = self.arguments.input.read(0xFFF)
            ran += 0xFFF

if __name__ == "__main__":
    parser = argparse.ArgumentParser("hkbit")
    
    args = parser.parse_args()
    hkb = HKBit(args.input, args.output, args.key)
    hkb.crypt()
    print()
    print(f"[i] Key file used: {args.key.name}")
