from core.modules import base, console
from remote.web.apis.modules import censys as Censys
from argparse import ArgumentParser
from enum import Enum


__all__ = ["CloudSnarf"]

class CloudSnarf(base.Program):
    """Identify IPv4 hosts behind CDNs using certificate data.
       
       This program aims on uncovering CDN-protected domains
       by querying censys.io for its SSL/TLS certificate chain,
       filtering it from cloudflare-signed certificates and 'reverse searching'
       the left certificates back on censys.io for IPv4 hosts using them;
       as we receive the results from this query,
       we have a list of possible hosts managed by the
       same owner/maintainer of the target domain,
       which possibly include direct-connect addresses to
       the base servers that are hidden behind CDNs."""
    credits = {"Base": "chokepoint@github.com",
               "Module": "@blackviruscript"}
    references = {"Base Script": "https://gist.github.com/chokepoint/28bed027606c5086ed9eeb274f3b840a"}
    requirements = {"censys"}
    def __init__(self):
        super().__init__()
        self.parser.add_argument("domain", type = str, help = "Target domain name.")
        self.parser.add_argument("-i", "--api-id", type = str, default = "", help = "Censys API ID.")
        self.parser.add_argument("-s", "--api-secret", type = str, default = "", help = "Censys API Secret.")
    
    def run(self):
        censys = Censys.API(self.arguments.api_id, self.arguments.api_secret)
        fingerprints = {}
        fields = ["parsed.subject_dn", "parsed.names", "parsed.fingerprint_sha256", "parsed.subject.common_name"]
        certificates = [{key.rsplit(".", 1)[-1]: value for key, value in cert.items()} for cert in censys.certificates.search(f"{self.arguments.domain} and tags: trusted", fields = fields) if cert]
        for certificate in filter(lambda cert: self.arguments.domain in cert.get("names", []) and not any(map(lambda d: d.endswith(".cloudflaressl.com") or d.endswith(".cloudflare.com"), cert["common_name"])), certificates):
            hosts = set()
            fingerprint, common_name, names, sdn = (certificate["fingerprint_sha256"],
                                                    certificate.get("common_name", []),
                                                    certificate.get("names", []),
                                                    certificate.get("subject_dn"))
            results = censys.ipv4.search(f"{fingerprint}", fields = ["443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names", "443.https.tls.certificate.parsed.names", "ip"])
            if results:
                console.print(f"[+] {fingerprint}: {', '.join(common_name or names or [])}")
                if sdn:
                    console.print(f" -  {sdn}")
            for host in results:
                hosts.add(host["ip"])
                console.print(f" -  {host['ip']} [{', '.join(host.get('443.https.tls.certificate.parsed.names', host.get('443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names', [])))}]", dark = True)
            fingerprints[fingerprint] = hosts
        hosts = set()
        for value in fingerprints.values():
            hosts.update(value)
        console.print(f"[i] {len(fingerprints) or 'No'} fingerprints {f'and {len(hosts)}' if fingerprints else 'or'} hosts were found.")
