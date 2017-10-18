from remote.web.modules.session import Session


class API(Session):
    def __init__(self, key: str = "", version: int = 2):
        super().__init__(f"https://api.fullcontact.com/v{version}/")
        self.headers["X-FullContact-APIKey"] = key
        self.version = version
        self.key = key
    
    def stats(self, period: str = "", type: str = "json", prettyPrint: bool = False):
        return self.get(f"./stats.{type}?prettyPrint={str(prettyPrint).lower()}&period={period}")
    
    def person(self, query: str, method: str = "email", type: str = "json",
               style: str = "list", css: str = "", prettyPrint: bool = False,
               countryCode: str = "", confidence: str = "max", macromeasures: bool = True):
        method = method.lower()
        url = f"./person.{type}?{method}={query}&style={style}&prettyPrint={str(prettyPrint).lower()}&confidence={confidence}"
        if macromeasures: url += "&macromeasures=true"
        if css: url += "&css=" + css
        if method is "phone":
            if countryCode: url += "&countryCode=" + countryCode
        return self.get(url)
    
    def domain(self, query: str, keyPeople: bool = False, prettyPrint: bool = False):
        url = f"./company/lookup.json?domain={query}&prettyPrint={str(prettyPrint).lower()}"
        if keyPeople: url += "&keyPeople=true"
        return self.get(url)
    
    def company(self, query: str, sort: str = "relevance", location: str = "", locality: str = "", region: str = "", country: str = "", prettyPrint: bool = False):
        url = f"./company/search.json?companyName={query}&sort={sort}&prettyPrint={str(prettyPrint).lower()}"
        if location: url += "&location=" + location
        if locality: url += "&locality=" + locality
        if country: url += "&country=" + country
        if region: url += "&region=" + region
        return self.get(url)
