from core.modules.base import Program
from core.modules.console import print
import requests


class Track(Program):
    """Host location tracker using the JSON API provided by ip-api.com."""
    def __init__(self):
        super().__init__()
        self.parser.add_argument("host", type = str, help = "Target hostname or address.")
    
    def run(self):
        response = requests.get(f"http://ip-api.com/json/{self.arguments.host}?fields=258047").json()
        assert response["status"] == "success", Exception(f"{' - '.join(f'{key.title()}: {value}' for key, value in response.items())}")
        print("""            ,,,,,,                 
        o#'9MMHb':'-,o,            --------- Tracking Results ---------
     .oH":HH$' "' ' -*R&o,                 IP Address {query}
    dMMM*""'`'      .oM"HM?.                  Country {country}/{countryCode}
  ,MMM'          "HLbd< ?&H                    Region {regionName}/{region}
 .:MH ."          ` MM  MM&b                     City {city}
. "*H    -        &MMMMMMMMMH:               Zip Code {zip}
.    dboo        MMMMMMMMMMMM.              Time Zone {timezone}
.   dMMMMMMb      *MMMMMMMMMP.           Organization {org}
.    MMMMMMMP        *MMMMMP .                    ISP {isp}
     `#MMMMM           MM6P ,                Latitude {lat}
 '    `MMMP"           HM*`,                Longitude {lon}
  '    :MM             .- ,                  Is Proxy {proxy}
   '.   `#?..  .       ..'                  Is Mobile {mobile}
      -.   .         .-                     {as}
        ''-.oo,oo.-''              """.format(**response))
