from core.modules import console, base
import os, sys, argparse


__all__ = ["Launcher"]

class Launcher(object):
    location = os.path.abspath(os.path.dirname(__file__))
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers(title = "Available Programs", dest = "command")
        subparsers.required = True
        for root, dirnames, filenames in os.walk(self.location):
            basedir = os.path.basename(os.path.dirname(root))
            if not basedir.startswith("_") and basedir != "modules":
                for name in filter(lambda name: name.endswith(".py"), filenames):
                    fullname = os.path.join(root, name)
                    try:
                        module = console.load(fullname)
                        for name in filter(lambda x: not x.startswith("_"), dir(module)):
                            attr = getattr(module, name)
                            if callable(attr) and issubclass(attr, base.Program):
                                name = os.path.splitext(fullname.replace(self.location, "", 1)[1:].replace("\\", "/"))[0]
                                command = attr
                                command.parser = subparsers.add_parser(name, help = command.__doc__.split("\n", 1)[0])
                                command.parser.set_defaults(_command = command())
                                command.parser.prog = os.path.basename(name)
                                break
                    except TypeError:
                        pass
                    except Exception as e:
                        pass
    
    def run(self, argv = sys.argv[1:]):
        args = self.parser.parse_args(argv)
        command = args._command
        command.parse_args(*argv[1:])
        command.run()

if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()
