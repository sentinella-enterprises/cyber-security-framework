import dns.resolver, dns.message, argparse, sys
from core.modules.base import Program
from core.modules.console import print


class NSMap(dns.resolver.Resolver, Program):
    """Map DNS Records."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("query", type=str, help="The query.")
        self.parser.add_argument("-t", "--timeout", type=int, default=8, help="The number of seconds to wait before the query times out.")
        self.parser.add_argument("-p", "--port", type=int, default=53, help="The port to which to send the message. The default is 53.")
        self.parser.add_argument("-i", "--ignore-unexpected", action="store_true", default=None, help="If True, ignore responses from unexpected.")
        self.parser.add_argument("-o", "--one-rr-per-rrset", action="store_true", default=None, help="Put each RR into its own RRset.")
        self.parser.add_argument("-e", "--use-edns", type=int, default=-1, help="The EDNS level to use. The default is -1 (no EDNS).")
        self.parser.add_argument("-s", "--want-dnssec", action="store_true", default=None, help="Should the query indicate that DNSSEC is desired?")
        self.parser.add_argument("-a", "--any", action="store_true", help = "Try executing an ANY metaquery.")
        
        self._nameservers = self.nameservers
        self.rdclasses = dict(sorted([(k, v) for k, v in dns.rdataclass.__dict__.items() if k.isupper()], key=lambda x: x[0]))
        self.rdtypes = dict(sorted([(k, v) for k, v in dns.rdatatype.__dict__.items() if k.isupper()], key=lambda x: x[0]))
        self._max_rdclass_length = max([len(rdclass) for rdclass in self.rdclasses])
        self._max_rdtype_length = max([len(rdtype) for rdtype in self.rdtypes])
    
    def _iter(self, answer):
        for record in sorted(answer, key = lambda x: dns.rdatatype.to_text(x.rdtype)):
            string = f" -  {dns.rdatatype.to_text(record.rdtype).ljust(self._max_rdtype_length)}"
            print(string, end = "")
            extra = False
            for name in dir(record):
                value = getattr(record, name)
                if value is None or name.startswith("_") or callable(value) or name in ("rdtype", "rdclass"):
                    continue
                s = f"{(' ' * (len(string)+1)) if extra else ''}{name}: "
                if isinstance(value, bytes):
                    value = value.decode("ascii", errors="replace")
                elif isinstance(value, (list, tuple)):
                    value = ("\n" + (" " * len(s))).join(sorted([i.decode("ascii", errors="replace") if isinstance(i, bytes) else
                                                                 (("\n" + (" " * (len(s) + 1))).join(str(i).split(" ")) if record.rdtype == 16 else str(i))
                                                                for i in value]))
                print(s + f"{value}", dark = True)
                extra = True
    
    def metaquery(self, qname, rdtype, rdclass=1, use_edns=None, want_dnssec=False, ednsflags=None, payload=None, request_payload=None, options=None,
                  timeout=8, port=53, af=None, source=None, source_port=0, ignore_unexpected=False, one_rr_per_rrset=False, tcp=False):
        try:
            ns = self.query(self.query(qname, "NS")[0].to_text()[:-1])[0].to_text()
        except:
            ns = self.nameservers[0] if self.nameservers else "8.8.8.8"
        message = dns.message.make_query(qname, rdtype, rdclass, use_edns, want_dnssec, ednsflags, payload, request_payload, options)
        return (dns.query.tcp(message, ns, timeout=timeout, port=port, af=af, source=source, source_port=source_port, one_rr_per_rrset=one_rr_per_rrset)
                if tcp else
                dns.query.udp(message, ns, timeout=timeout, port=port, af=af, source=source, source_port=source_port, ignore_unexpected=ignore_unexpected, one_rr_per_rrset=one_rr_per_rrset))
    
    def scan(self, host, **kwargs):
        print(f"[i] NSMap results for host {repr(host)}:")
        answer = self.metaquery(host, "ANY", **kwargs).answer if kwargs.pop("any") else None
        if answer:
            self._iter(answer)
        else:
            for name, rdtype in self.rdtypes.items():
                if not dns.rdatatype.is_metatype(rdtype):
                    try:
                        answer = self.metaquery(host, rdtype, **kwargs).answer
                        if answer:
                            self._iter(answer)
                    except Exception as e:
                        print(f" -  {name.ljust(self._max_rdtype_length+1)}", (str(e), True), color = "red")
            else:
                print(f" -  No records are directly available for this host ...", color = "yellow", dark = True)
    
    def run(self):
        args = self.arguments.__dict__
        self.scan(args.pop("query"), **args)
