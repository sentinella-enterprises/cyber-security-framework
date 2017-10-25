# **CSF - Cyber Security Framework**
- #### By the **Black**Security Team
> The CyberSecurity Framework (CSF for short) is a local Python3 scripting package, where you can execute and create new programs for **any purpuse that goes under your own responsibility** to fit your needs.
> 
> This project aims directly on Cyber Security auditing, but you can also use/extend it to fit on any unrelated needs of your own.
> #### **Extending**
> To create an executable program, which can be ran through the `csf.py --execute` command, all you need to do is subclass the `core.modules.base.Program` class and implement a `run` method on it. Once this class is initialized you can access a `parser` attribute which holds an `argparse.ArgumentParser` object, used to define & parse command line arguments into your program ...
>
> **Example**:
> ```python
> # Import the class "Program" and function "print" from the core "base" and "console" modules.
> from core.modules.base import Program
> from core.modules.console import print
> 
> 
> class MyProgram(Program):
>     def __init__(self):
>         # Initialize the base class (core.modules.base.Program).
>         super().__init__()
>         self.parser.add_argument("foo", type = str, help = "Foo str.")
>         self.parser.add_argument("bar", type = int, help = "Bar int.")
>         self.parser.add_argument("-b", "--baz", type = str, help = "Baz str.")
>         self.parser.add_argument("-q", "--qux", type = str, default = "Quux", help = "Qux str.")
>     
>     def run(self):
>         print(f"foo = {self.arguments.foo}, bar = {self.arguments.bar}, baz = {self.arguments.baz}, qux = {self.arguments.qux}")> ```
