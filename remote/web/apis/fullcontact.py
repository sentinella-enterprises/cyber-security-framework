from remote.web.apis.modules import fullcontact
from core.modules.base import Program
from core.modules.console import print, pprint

_print = print
def print(*messages, color: str = "white", dark: bool = False, prefix: str = "", **kwargs):
    _print(*messages, color = color, dark = dark, prefix = prefix, parse = False, **kwargs)

class FullContact(Program):
    """Performs contact info queries against email-addresses, twitter usernames, phone numbers, company names and domains ..."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("-k", "--api-key", type = str, help = "The API key assigned to you by FullContact. It is used to identify and authorize your request. Your API key should be kept private, and should never be displayed publicly.", required = True)
        actions = self.parser.add_mutually_exclusive_group(required = True)
        actions.add_argument("-s", "--stats", type = str, metavar = "period", const = "", nargs = "?", help = "Query FullContact to view your API account usage for the current month or a previous month defined by you. The format is YYYY-MM (e.g: --stats 2017-10).")
        actions.add_argument("-e", "--email", type = str, metavar = "address", help = "Request information about a specific person by email.")
        actions.add_argument("-p", "--phone", type = str, metavar = "number", help = "Request information about a specific person by phone.")
        actions.add_argument("-t", "--twitter", type = str, metavar = "username", help = "Request information about a specific person by twitter.")
        actions.add_argument("-d", "--domain", type = str, metavar = "name", help = "Request information about a specific company by domain.")
        actions.add_argument("-c", "--company", type = str, metavar = "name", help = "Request information about a specific company by name.")
        
        person = self.parser.add_argument_group("Person API")
        person.add_argument("--stylesheet", type = str, metavar = "url", default = "", help = "CSS file used to customize the look of person.html.")
        person.add_argument("--confidence", type = str, default = "high", choices = ["low", "med", "high", "max"], help = "A confidence of max will return less data than usual, however, the data that is returned will have a higher likelihood of being correct. On the other hand, a confidence of low will return more data than usual, but makes the possibility of a mistake in that data more likely. med returns more data than high and less than low, with an error rate between the two.")
        person.add_argument("--macromeasures", action = "store_true", help = "Power the Person API's ability for providing affinity data about individuals.")
        phone = self.parser.add_argument_group("Phone Lookup")
        phone.add_argument("--country-code", type = str, metavar = "code", default = "", help = "This parameter must be passed when using non US/Canada based phone numbers. Use the ISO-3166 two-digit country code (Great Britain = GB). If not entered it defaults to US.")
        
        domain = self.parser.add_argument_group("Domain Lookup")
        domain.add_argument("--key-people", action = "store_true", help = "List Executive and VP level employees at this company.")
        name = self.parser.add_argument_group("Name Lookup")
        name.add_argument("--sort", type = str, metavar = "option", default = "traffic", choices = ["traffic", "relevance", "employees"], help = "Controls how results will be sorted. There are three options: traffic (default): Sort high-traffic domains to the top; relevance: Sort by how closely the company name matches; employees: Sort companies with many employees to the top.")
        name.add_argument("--location", type = str, help = "If supplied, only companies matching given location will be returned. The location is a general location where one can include any combination of locality, region or country as input. For example, --location=Denver, CO.")
        name.add_argument("--locality", type = str, help = "If supplied, only companies matching given locality/city will be returned. For example, --locality=New York or --locality=Dallas.")
        name.add_argument("--country", type = str, help = "If supplied, only companies matching given country will be returned. For example, country=United States or country=US.")
        name.add_argument("--region", type = str, help = "If supplied, only companies matching given region/state will be returned. For example, --region=New York or --region=NY.")
        
        #self.parser.add_argument("-x", "--export", type = str, choices = ["html", "xml", "json"], help = "Export received data to the specified file type.")
        self.parser.epilog = "Note: The Stats (-s/--stats) endpoint is rate-limited to 30 calls per hour."
    
    def run(self):
        kwargs = {"type": "json"}
        pkwargs = {"css": self.arguments.stylesheet, "confidence": self.arguments.confidence, "macromeasures": self.arguments.macromeasures}
        api = fullcontact.API(self.arguments.api_key)
        if self.arguments.stats != None:
            print(f"[i] Request results for Account Statistics endpoint:")
            response = api.stats(self.arguments.stats, **kwargs)
        elif self.arguments.email:
            print(f"[i] Request results for E-Mail Address based Person Lookup:")
            response = api.person(self.arguments.email, "email", **kwargs, **pkwargs)
        elif self.arguments.phone:
            print(f"[i] Request results for Phone Number based Person Lookup:")
            response = api.person(self.arguments.phone, "phone", countryCode = self.arguments.country_code, **kwargs, **pkwargs)
        elif self.arguments.twitter:
            print(f"[i] Request results for Twitter Username based Person Lookup:")
            response = api.person(self.arguments.twitter, "twitter", **kwargs, **pkwargs)
        elif self.argument.domain:
            print(f"[i] Request results for Domain Name based Company Lookup:")
            response = api.domain(self.arguments.domain, keyPeople = self.arguments.key_people)
        else:
            print(f"[i] Request results for Name based Company Lookup:")
            response = api.company(self.arguments.company, location = self.arguments.location, locality = self.arguments.locality,
                                   country = self.arguments.country, region = self.arguments.region)
        pprint(response.json(), 1)
