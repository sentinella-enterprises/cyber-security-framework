from censys import certificates, websites, ipv4, export, query

__all__ = ["API"]

class API(object):
    ipv4: ipv4.CensysIPv4
    websites: websites.CensysWebsites
    certificates: certificates.CensysCertificates
    export: export.CensysExport
    def __init__(self, api_id: str = "", api_secret: str = ""):
        self.api_id = self.api_secret = ""
        if api_id:
            self.api_id = api_id
            self.api_secret = api_secret
        self.ipv4 = ipv4.CensysIPv4(self.api_id, self.api_secret)
        self.websites = websites.CensysWebsites(self.api_id, self.api_secret)
        self.certificates = certificates.CensysCertificates(self.api_id, self.api_secret)
        self.export = export.CensysExport(self.api_id, self.api_secret)
