# **CSF - Cyber Security Framework**
- #### By the **Black**Security Team
The CyberSecurity Framework (CSF for short) is a local Python3 scripting package which aims directly on Cyber Security auditing, where you can execute and create new programs for **any purpuse that go under your own responsibility** to fit your needs. (You can still use/extend it to fit on any unrelated needs of your own).

## NOTES:
- This project is maintained by a single person at the actual moment, but still being updated **at least** every 3 days ...
- This readme is still incomplete, there is not much info on it yet, but soon it is going to be updated.

### **Usage**
> ```
> $ csf.py --help
> usage: csf.py [-h] [-l [DIR]] [-d] [-e PROGRAM]
> 
> optional arguments:
>  -h, --help            show this help message and exit
>  -l [DIR], --list [DIR]
>                        List available programs.
>  -d, --debug           Debug program listing (-l/--list must be specified).
>  -e PROGRAM, --exec PROGRAM, --execute PROGRAM
>                        Execute the specified program.
> ```
> **Listing Programs**:
> - **List all working programs**:
>   
>   Command:
>   ```csf.py --list```
>   
>   Example:
>   ```
>   $ csf.py --list
>   [i] There are 16 programs available on 12 folders!
>   |--crypto: (1/0)
>   |  |--hkbit             Symmetric index based bit inversion cryptography.
>   |--network: (3/2)
>   |  |--client            Network Client.
>   |  |--sniffer           Sniff and parse IPv4 traffic reporting anomalies sent from and to the interface of
>   |  |                    the specified address.
>   |  |--whois             Query & output whois data.
>   |  |--link: (1/0)
>   |  |  |--mac-lookup     IEEE EUI (Extended Unique Identifier) lookup tool.
>   |  |--tor: (2/0)
>   |  |  |--eph-hs         Ephemeral Hidden Server (EPH-HS) management program.
>   |  |  |--fingerprintor  Retrieves descriptive information from hidden service addresses (via .onion
>   |  |  |                 descriptors).
>   |--remote: (0/5)
>   |  |--dns: (3/0)
>   |  |  |--dnask          Utility to build and execute DNS queries ...
>   |  |  |--dns-zt         Request a zone transfer (AXFR Query) from a DNS server.
>   |  |  |--nsmap          Map DNS Records.
>   |  |--rdp: (1/0)
>   |  |  |--rdp-c          Create simple RDP connection files.
>   |  |--snmp: (1/0)
>   |  |  |--snmpprint      SNMP data "walking" program.
>   |  |--ssl: (1/0)
>   |  |  |--heartbleed     Verify and exploit the heartbleed bug ...
>   |  |--web: (0/2)
>   |  |  |--apis: (1/0)
>   |  |  |  |--fullcontact Performs contact info queries against email-addresses, twitter usernames, phone
>   |  |  |  |              numbers, company names and domains ...
>   |  |  |--cdn: (2/0)
>   |  |  |  |--cloudsnarf  Identify IPv4 hosts behind CDNs using certificate data.
>   |  |  |  |--crimeflare  Uncovering bad guys hiding behind CloudFlare ...
>   ```
> - **List working programs on a specific folder**:
>   
>   Command:
>   ```csf.py --list FOLDER```
>   
>   Example:
>   ```
>   $ csf.py --list remote
>   [i] There are 9 programs available on 8 folders!
>   |--remote: (0/5)
>   |  |--dns: (3/0)
>   |  |  |--dnask          Utility to build and execute DNS queries ...
>   |  |  |--dns-zt         Request a zone transfer (AXFR Query) from a DNS server.
>   |  |  |--nsmap          Map DNS Records.
>   |  |--rdp: (1/0)
>   |  |  |--rdp-c          Create simple RDP connection files.
>   |  |--snmp: (1/0)
>   |  |  |--snmpprint      SNMP data "walking" program.
>   |  |--ssl: (1/0)
>   |  |  |--heartbleed     Verify and exploit the heartbleed bug ...
>   |  |--web: (0/2)
>   |  |  |--apis: (1/0)
>   |  |  |  |--fullcontact Performs contact info queries against email-addresses, twitter usernames, phone
>   |  |  |  |              numbers, company names and domains ...
>   |  |  |--cdn: (2/0)
>   |  |  |  |--cloudsnarf  Identify IPv4 hosts behind CDNs using certificate data.
>   |  |  |  |--crimeflare  Uncovering bad guys hiding behind CloudFlare ...
>   ```
> - **Debug program listing**:
>   
>   Command:
>   ```csf.py --list --debug```
>   
>   Example:
>   ```
>   $ csf.py --list --debug
>   [!] .\remote\test.py:
>    -  NameError: (.\remote\test.py line #18 in <module>)
>       'abc'
>    -  name 'abc' is not defined
>   ```
> 
> **Executing Programs**:
> Command:
> ```csf.py --execute PROGRAM [ARGUMENTS]```
> 
> Example:
> ```
> $ csf.py --execute remote/dns/dnask google.com --metaquery --rdtype ANY
> id 56855
> opcode QUERY
> rcode NOERROR
> flags QR RD RA
> ;QUESTION
> google.com. IN ANY
> ;ANSWER
> google.com. 216 IN AAAA 2800:3f0:4001:80a::200e
> google.com. 6 IN A 172.217.30.78
> google.com. 53467 IN NS ns2.google.com.
> google.com. 53467 IN NS ns4.google.com.
> google.com. 53467 IN NS ns3.google.com.
> google.com. 53467 IN NS ns1.google.com.
> ;AUTHORITY
> google.com. 53467 IN NS ns1.google.com.
> google.com. 53467 IN NS ns3.google.com.
> google.com. 53467 IN NS ns2.google.com.
> google.com. 53467 IN NS ns4.google.com.
> ;ADDITIONAL
> ns1.google.com. 260848 IN A 216.239.32.10
> ns2.google.com. 259410 IN A 216.239.34.10
> ns3.google.com. 259364 IN A 216.239.36.10
> ns4.google.com. 259280 IN A 216.239.38.10
> ```

### **Extending**
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
>         print(f"foo = {self.arguments.foo}, bar = {self.arguments.bar}, baz = {self.arguments.baz}, qux = {self.arguments.qux}")
> ```
> **TIP: You can also base on other program's code to roll your own, like so, you have something usable to base on.**
