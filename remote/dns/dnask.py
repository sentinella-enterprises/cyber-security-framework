import dns.resolver, dns.message, argparse, random
from network.modules import socket
from core.modules.base import Program
from core.modules.console import print


class DNAsk(Program):
    """Utility to build and execute DNS queries ..."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("query", type=str, help="Query string.")
        self.parser.add_argument("-t", "--rdtype", type=str, default=1, help="Query type.")
        self.parser.add_argument("-c", "--rdclass", type=str, default=1, help="Query class.")
        self.parser.add_argument("-m", "--metaquery", action="store_true", help="Execute as MetaQuery.")
        self.parser.add_argument("-s", "--source", type=str, default=socket.gethostbyname(socket.gethostname()), help="Source address.")
        self.parser.add_argument("-sP", "--source-port", type=int, default=random.randint(1, 65535), help="Source port.")
        self.parser.add_argument("--tcp", action="store_true", help="Use TCP to make the query.")
        self.parser.add_argument("-ns", "--nameservers", nargs="+", type=str, help="A list of nameservers to query. Each nameserver is a string which contains the IP address of a nameserver.")
        self.parser.add_argument("-p", "--port", type=int, default=53, help="The port to which to send queries (Defaults to 53).")
        self.parser.add_argument("-T", "--timeout", type=int, default=8, help="The number of seconds to wait for a response from a server, before timing out.")
        self.parser.add_argument("-l", "--lifetime", type=int, default=8, help="The total number of seconds to spend trying to get an answer to the question. If the lifetime expires, a Timeout exception will occur.")
        self.parser.add_argument("-e", "--edns", type=int, default=-1, help="The EDNS level to use (Defaults to -1, no Edns).")
        self.parser.add_argument("-eF", "--edns-flags", type=int, help="The EDNS flags.")
        self.parser.add_argument("-eP", "--edns-payload", type=int, default=0, help="The EDNS payload size (Defaults to 0).")
        self.parser.add_argument("-S", "--want-dnssec", action="store_true", help="Indicate that DNSSEC is desired.")
        self.parser.add_argument("-f", "--flags", type=int, default=None, help="The message flags to use (Defaults to None (i.e. not overwritten)).")
        self.parser.add_argument("-r", "--retry-servfail", action="store_true", help="Retry a nameserver if it says SERVFAIL.")
        self.parser.add_argument("-R", "--one-rr-per-rrset", action="store_true", help="Put each RR into its own RRset (Only useful when executing MetaQueries).")
        self.parser.add_argument("--filename", type=argparse.FileType("r"), help="The filename of a configuration file in standard /etc/resolv.conf format. This parameter is meaningful only when I{configure} is true and the platform is POSIX.")
        self.parser.add_argument("--configure-resolver", action="store_false", help="If True (the default), the resolver instance is configured in the normal fashion for the operating system the resolver is running on. (I.e. a /etc/resolv.conf file on POSIX systems and from the registry on Windows systems.")

    def run(self):
        arguments = self.arguments.__dict__
        nameservers = arguments.get("nameservers")
        resolver = dns.resolver.Resolver(arguments.get("filename"), arguments.get("configure_resolver"))
        resolver.set_flags(arguments.get("flags"))
        resolver.use_edns(arguments.get("edns"), arguments.get("edns_flags"), arguments.get("edns_payload"))
        if nameservers:
            resolver.nameservers = nameservers
        resolver.port = arguments.get("port")
        resolver.timeout = arguments.get("timeout")
        resolver.lifetime = arguments.get("lifetime")
        resolver.retry_servfail = arguments.get("retry_servfail")
        if arguments.pop("metaquery"):
            kwargs = {v: arguments.get(k) for k, v in {"rdclass": "rdclass", "edns": "use_edns", "want_dnssec": "want_dnssec", "edns_flags": "ednsflags", "edns_payload": "request_payload"}.items()}
            message = dns.message.make_query(arguments.get("query"), arguments.get("rdtype"), **kwargs)
            kwargs = {k: arguments.get(k) for k in ["timeout", "port", "source", "source_port", "one_rr_per_rrset"]}
            if arguments.get("tcp"):
                resp = dns.query.tcp(message, resolver.nameservers[0], **kwargs)
            else:
                resp = dns.query.udp(message, resolver.nameservers[0], **kwargs)
            print(resp)
        else:
            kwargs = {k: arguments.get(k) for k in ["rdtype", "rdclass", "tcp", "source", "source_port"]}
            answer = resolver.query(arguments.pop("query"), **kwargs)
            print(answer.response)
