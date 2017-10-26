from core.modules import console, base
import os, sys, argparse, traceback


__all__ = ["Launcher"]

class CSF(object):
    location = os.path.abspath(os.path.dirname(__file__))
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        actions = self.parser.add_mutually_exclusive_group(required = True)
        actions.add_argument("-l", "--list", type = str, nargs = "?", const = "", metavar = "DIR", help = "List available programs.")
        self.parser.add_argument("-d", "--debug", action = "store_true", help = "Debug program listing (-l/--list must be specified).")
        actions.add_argument("-e", "--exec", "--execute", dest = "executable", metavar = "PROGRAM", type = str, help = "Execute the specified program.")
    
    def list(self, folder: str, debug: bool = True):
        tree = {}
        total = [0, 0]
        for root, dirnames, filenames in os.walk(os.path.join(self.location, folder)):
            basedir = os.path.basename(os.path.dirname(root))
            if not basedir.startswith("_") and basedir not in ["modules"]:
                for name in filter(lambda name: name.endswith(".py"), filenames):
                    fullname = os.path.join(root, name)
                    try:
                        module = console.load(fullname)
                        commands = set()
                        for attribute in map(lambda name: getattr(module, name), filter(lambda x: not x.startswith("_"), dir(module))):
                            try:
                                if callable(attribute) and issubclass(attribute, base.Program) and attribute != base.Program:
                                    commands.add(attribute)
                            except TypeError as e:
                                if str(e) != "issubclass() arg 1 must be a class":
                                    raise e
                        if commands:
                            for command in commands:
                                t = tree
                                for field in root.replace(self.location, "", 1)[1:].replace("\\", "/").split("/"):
                                    if field not in t:
                                        t[field] = {}
                                        total[1] += 1
                                    t = t[field]
                                t[os.path.splitext(os.path.basename(fullname))[0]] = (command.__doc__ or "No description available.").split("\n", 1)[0]
                                total[0] += 1
                                break
                    except Exception as e:
                        if debug:
                            filename, line, function, text = traceback.extract_tb(e.__traceback__)[-1]
                            console.print(f"[!] {fullname.replace(self.location, '.')}:", color = "red")
                            console.print(f" -  {type(e).__name__}: ({filename.replace(csf.location, '.')} line #{line} in {function})", color = "red")
                            console.print(f"    {repr(text)}", color = "red", dark = True, parse = False)
                            console.print(f" -  {e}", color = "red", dark = True)
                            exit(1)
        def pprint(obj, depth: int = 0):
            prefix = "|  " * depth
            for key, value in obj.items():
                if isinstance(value, str):
                    l1 = prefix + f"|--{key}"
                    prefix2 = (prefix + "|  ").ljust(24)
                    if len(l1) > 23:
                        console.print(l1)
                        console.print(prefix2, (value, True), prefix = prefix2)
                    else:
                        console.print(l1.ljust(24), (value, True), prefix = prefix2)
                else:
                    programs = len(list(filter(lambda x: isinstance(x[1], str), value.items())))
                    folders = len(value) - programs
                    console.print(f"{prefix}|--{key}: ({programs}/{folders})")
                    pprint(value, depth + 1)
        console.print(f"[i] There are {total[0] or 'no'} programs available {f'on {total[1]} folders' if total[1] else ''}!")
        pprint(tree)
    
    def execute(self, file: str, *args):
        fullname = os.path.join(self.location, file)
        if not fullname.endswith(".py"):
            fullname += ".py"
        module = console.load(fullname)
        commands = set()
        for attribute in map(lambda name: getattr(module, name), filter(lambda x: not x.startswith("_"), dir(module))):
            try:
                if callable(attribute) and issubclass(attribute, base.Program) and attribute != base.Program:
                    commands.add(attribute)
            except TypeError as e:
                if str(e) != "issubclass() arg 1 must be a class":
                    raise e
        assert commands, "Invalid executable Program!"
        for command in commands:
            try:
                command = command()
                command.parse_args(*args)
                command.run()
            except TypeError as e:
                if str(e) != "issubclass() arg 1 must be a class":
                    raise e
    
    def run(self, argv = sys.argv[1:]):
        args = self.parser.parse_args(argv[:2])
        if args.list != None:
            self.list(args.list, args.debug)
        elif args.executable:
            self.execute(args.executable, *argv[2:])

if __name__ == "__main__":
    csf = CSF
    try:
        csf = csf()
        csf.run()
    except Exception as e:
        filename, line, function, text = traceback.extract_tb(e.__traceback__)[-1]
        console.print(f"[!] {type(e).__name__}: ({filename.replace(csf.location, '.')} line #{line} in {function})", color = "red")
        console.print(f"    {repr(text)}", color = "red", dark = True, parse = False)
        console.print(f" -  {e}", color = "red", dark = True)
        #raise e
    except KeyboardInterrupt:
        console.print(f"[!] Keyboard Interrupted!", color = "red")
