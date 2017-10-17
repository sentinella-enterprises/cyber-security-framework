from core.modules import console, base
import argparse, sys


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("script", type = argparse.FileType(), help = "Target script.")
    args = parser.parse_args()
    module = console.load(args.script.name)
    for name in filter(lambda x: not x.startswith("_"), dir(module)):
        attr = getattr(module, name)
        if callable(attr) and issubclass(attr, base.Program) and attr != base.Program:
            program = attr()
            program.parse_args(*sys.argv[2:])
            program.run()
