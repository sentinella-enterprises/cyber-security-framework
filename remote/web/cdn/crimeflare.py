from core.modules.console import print
from core.modules.base import Program
from dns.resolver import Resolver
from remote.web.modules.session import Session
import re, argparse


class CrimeFlare(Program):
    """Uncovering bad guys hiding behind CloudFlare ..."""
    def __init__(self):
        super().__init__()
        self.resolver = Resolver()
        self.session = Session("http://www.crimeflare.com/cgi-bin/")
        actions = self.parser.add_mutually_exclusive_group(required = True)
        actions.add_argument("-s", "-cfs", "--search", metavar="DOMAIN", type=str, help="CloudFlare-Protected-Domain Search ...")
        actions.add_argument("-l", "-cfl", "--list", metavar="CFL-ID", type=str, help="List CloudFlare domains using the specified Direct-Connect IP Address ...")
        self.parser.add_argument("-x", "--proxy", default="", type=str, help="Proxify session through this proxy ('proto://a.ddr.es.s:port/') ...")
    
    def cfsearch(self, domain: str):
        nameservers = [ns.to_text() for ns in self.resolver.query(domain, "NS")]
        page = self.session.post("cfsearch.cgi", data={"cfS": domain}).parsed()
        cfl_ids = [a.get("href") for a in page.findAll("a", attrs={"href": re.compile(r"^http://www.crimeflare.com/cgi-bin/cflist/.*$")})]
        
        print("[i] CloudFlare Search Results:")
        print(" -  Name Servers:")
        for ns in nameservers:
            print(f"    - {ns} [{', '.join(ip.to_text() for ip in self.resolver.query(ns, 'A'))}]", dark=True)
        print()
        if cfl_ids:
            print(" -  CFList (CFL) IDs: (Single use)")
            for id in cfl_ids:
                print("    - " + id.split("/")[-1], dark=True)
            print()
        if page.ul:
            print(" -  " + "\n -  ".join(page.ul.stripped_strings), dark=True)
        else:
            print(" -  No direct-connect IP addresses have been found for this domain ...", color = "red", dark = True)
    
    def cflist(self, cfl_id: str):
        page = self.session.get("cflist/" + cfl_id, headers={"Referer": "http://www.crimeflare.com/cgi-bin/cfsearch.cgi"}).parsed()
        if page.title.text.lower() == "cloudflare search results":
            domains = list(page.stripped_strings)[3:-4]
            print("[i] Some CloudFlare-User domains with a direct-connect IP address of {cfl_id.split('-')[1]}:")
            for i in range(0, len(domains), 2):
                print(" -  {:32}{:32}".format(*domains[i:i+2], ""), dark=True)
        else:
            raise Exception("Failed to list cloudflare-user domains using this CFL id ...")
    
    def run(self):
        if self.arguments.search:
            self.cfsearch(self.arguments.search)
        else:
            self.cflist(self.arguments.list)
