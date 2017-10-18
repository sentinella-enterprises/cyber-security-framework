import urllib.parse, requests, bs4
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


__all__ = ["Session", "parse"]

def parse(response: requests.Response):
    ct = response.headers.get("Content-Type", "text/html").split(";")[0]
    if ct == "application/json":
        return response.json()
    elif ct.split("/")[0] == "text" and ct.endswith("+xml"):
        return bs4.BeautifulSoup(response.content, "lxml")
    elif ct.split("/")[0] == "text" and ct.endswith("html"):
        return bs4.BeautifulSoup(response.content, "html.parser")
    raise Exception(f"Cannot parse {ct} data.")

class Session(requests.Session):
    def __init__(self, url: str, headers: dict = {}):
        super().__init__()
        self.headers.update(headers)
        self.base_url = urllib.parse.urlparse(url)
    
    def request(self, method: str, path: str = "", **kwargs):
        response = super().request(method, urllib.parse.urljoin(self.base_url.geturl(), path), **kwargs)
        response.parsed = lambda: parse(response)
        return response
