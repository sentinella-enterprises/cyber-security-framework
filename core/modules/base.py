import argparse, pip, sys, os
from core.modules import console
from network.modules import socket
from enum import Enum


class exceptions(object):
    class Fail(Exception):
        pass
    class Unreachable(Exception):
        pass

class Program(object):
    notes: dict = {}
    credits: dict = {}
    references: dict = {}
    epilog: str = ""
    for dict in {"Notes": notes, "References": references, "Credits": credits}.items():
        if dict[1]:
            epilog += f"[i] {dict[0]}: ({len(dict[1])})\n"
            for key, value in dict[1].items():
                epilog += f" -  {key}: {value}\n"
            epilog += "\n"
    requirements: set = set()
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    def __init__(self):
        self.parser.prog = type(self).__name__
        self.parser.description = self.__doc__.split("\n", 1)[-1].strip()
        self.parser.epilog = self.epilog
    
    def parse_args(self, *args):
        self.arguments = self.parser.parse_args(args)
    
    def run(self):
        pass

"""
class Exploit(Program):
    class Category(Enum):
        Undefined = 0
        InformationDisclosure = 1
        BufferOverflow = 2
        CodeExecution = 3
        Bypass = 4
    category: Category = Category.Undefined
    __attrs__ = ["name", "description", "license", "notes", "credits", "references", "epilog", "category"]
"""
