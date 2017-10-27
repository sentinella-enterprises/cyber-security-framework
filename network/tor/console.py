import stem.interpreter
from core.modules.base import Program
from core.modules.console import print


class TorConsole(Program):
    """Interactive interpreter for interacting with Tor directly."""
    def __init__(self):
        super().__init__()
    
    def run(self):
        stem.interpreter.main()
