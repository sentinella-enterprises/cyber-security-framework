import importlib.util, zipimport
import readline, colorama, termcolor
import threading
import argparse, sys, os
colorama.init(autoreset=True)
lock = threading.Lock()


__all__ = ["lock", "load", "fit", "print", "input", "hexdump",
           "stdin", "stdout", "stderr"]
global stdin, stdout, stderr
stdin, stdout, stderr = sys.stdin, sys.stdout, sys.stderr


def load(file: str, module: str = "__main__"):
    file = os.path.abspath(file)
    if file.endswith(".zip"):
        importer = zipimport.zipimporter(file)
        sys.path.insert(0, file)
        module = importer.load_module(os.path.splitext(os.path.basename(file))[0])
        sys.path.remove(file)
    else:
        spec = importlib.util.spec_from_file_location(os.path.basename(file).rsplit(".", 1)[0], file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return module

def fit(string, prefix: str = "    "):
    columns = os.get_terminal_size().columns
    output = ""
    for word in string.split(" "):
        if (len(output.split("\n")[-1]) >= (columns - 1)) or (len(output.split("\n")[-1] + word + " ") >= (columns - 1)):
            output += "\n" + prefix
        
        if len(word) > (columns - 1) - len(output.split("\n")[-1]):
            while word:
                index = (columns - 1) - len(output.split("\n")[-1])
                output += word[:index] + "\n" + prefix
                word = word[index:]
            output += " "
        else:
            output += word + " "
    return output

_print = print
def print(*messages, color: str = "white", dark: bool = False, prefix: str = "", parse: bool = True, **kwargs):
    if "file" not in kwargs:
        kwargs["file"] = stdout
    #try:
    columns = os.get_terminal_size().columns
    #except ValueError:
    #    columns = None
    string = ""
    for message in messages:
        if isinstance(message, (tuple, list, set)):
            if isinstance(message[-1], bool):
                *message, dark = message
            if message[-1] in termcolor.COLORS.keys():
                *message, color = message
            message = " ".join(map(str, message))
        string += termcolor.colored(message, color, attrs=["dark"] if dark else [])
    #if columns:
    _print((fit(string, prefix) if parse else string), **kwargs)
    #else:
    #    _print(string, **kwargs)

def input(prompt, stdin = sys.stdin, size: int = -1, **kwargs):
    if "end" not in kwargs:
        kwargs["end"] = ""
    print(prompt, **kwargs)
    return stdin.read(size = size)

def hexdump(data: bytes, prefix="", **pkwargs):
    for b in range(0, len(data), 16):
        line = [char for char in data[b: b + 16]]
        print(prefix + "{:04x}: {:48} |{}|".format(b, " ".join(f"{char:02x}" for char in line), "".join((chr(char) if 32 <= char <= 126 else ".") for char in line).ljust(16)), **pkwargs)

def pprint(obj: object, depth: int = 0, excluded_keys: list = [], pretty_keys: bool = True, **pkwargs):
    prefix = "" if depth == 0 else (" -  " if depth == 1 else ("    - " if depth == 2 else ("  " * depth) + "- "))
    if isinstance(obj, dict):
        for key, value in filter(lambda x: x not in excluded_keys, obj.copy().items()):
            if pretty_keys:
                key = key.replace("_", "-")
                if key.islower():
                    key = key.title()
                else:
                    key = key[0].upper() + key[1:]
            if isinstance(value, (dict, list, set, tuple)):
                print(f"{prefix}{key}:", **pkwargs)
                pprint(value, depth + 1, excluded_keys, pretty_keys, **pkwargs)
            elif isinstance(value, (bytes, bytearray)):
                print(f"{prefix}{key}:", **pkwargs)
                hexdump(value, prefix, **pkwargs)
            else:
                print(f"{prefix}{key}: {value}", **pkwargs)
    elif isinstance(obj, (list, tuple, set)):
        for value in obj:
            pprint(value, depth, excluded_keys, pretty_keys, **pkwargs)
            if obj.index(value) < len(obj) - 1:
                print()
    elif isinstance(obj, (bytes, bytearray)):
        hexdump(value, prefix, **pkwargs)
    else:
        print(f"{prefix}{obj}", **pkwargs)

"""
class Command(argparse.ArgumentParser):
    console = None
    def __init__(self, name: str, usage: str = None, description: str = None, epilog: str = None, formatter_class = argparse.HelpFormatter, add_help: bool = True):
        assert self.console, "No parent console specified! (parent = None)"
        super().__init__(name, usage, description, epilog, formatter_class, self.console.prefix_chars, None,
                         self.console.argument_default, self.console.conflict_handler, add_help, self.console.allow_abbrev)
    
    def __eq__(self, obj):
        return self.prog == obj or self == obj

class Console(object):
    prompt: str = "-{name}> "
    prefix_chars: str = "-"
    argument_default: str = None
    conflict_handler: str = "error"
    allow_abbrev: bool = True
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    commands: parser.add_subparsers(required = True)
    def __init__(self):
        self.parser.prog = self.__name__
        Console.Command.console = self
        self.prompt = self.prompt.format(name = self.__name__)
        self.commands.add_parser(Command("help", description = "Displays help information on commands."))
    
    def execute(self, command: str, *args):
        assert command in self.commands.choices, ValueError(f"No command named {repr(command)}.")
        arguments = self.parser.parse_args([command, *args])
        getattr(self, command)(arguments)
"""
