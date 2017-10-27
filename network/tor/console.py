import stem.interpreter, sys
from core.modules.base import Program
from core.modules.console import print


class TorConsole(Program):
    """Interactive interpreter for interacting with Tor directly."""
    def __init__(self):
        super().__init__()
    
    def run(self):
        del sys.argv[:2]
        stem.interpreter.main()
