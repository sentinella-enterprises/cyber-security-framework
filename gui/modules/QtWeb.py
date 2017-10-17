from PyQt5 import QtWidgets, QtNetwork, QtCore, QtGui


__all__ = ["QWebSession"]

class QWebSession(QtCore.QObject):
    authenticationRequired = QtNetwork.QNetworkAccessManager.authenticationRequired
    encrypted = QtNetwork.QNetworkAccessManager.encrypted
    finished = QtNetwork.QNetworkAccessManager.finished
    networkAccessibleChanged = QtNetwork.QNetworkAccessManager.networkAccessibleChanged
    preSharedKeyAuthenticationRequired = QtNetwork.QNetworkAccessManager.preSharedKeyAuthenticationRequired
    proxyAuthenticationRequired = QtNetwork.QNetworkAccessManager.proxyAuthenticationRequired
    sslErrors = QtNetwork.QNetworkAccessManager.sslErrors
    
    downloadProgress = QtCore.pyqtSignal(QtNetwork.QNetworkReply, "qint64", "qint64")
    error            = QtCore.pyqtSignal(QtNetwork.QNetworkReply, QtNetwork.QNetworkReply.NetworkError)
    metaDataChanged  = QtCore.pyqtSignal(QtNetwork.QNetworkReply)
    redirectAllowed  = QtCore.pyqtSignal(QtNetwork.QNetworkReply)
    redirected       = QtCore.pyqtSignal(QtNetwork.QNetworkReply, QtCore.QUrl)
    uploadProgress   = QtCore.pyqtSignal(QtNetwork.QNetworkReply, "qint64", "qint64")
    def __init__(self,
                 headers: dict = {}, attributes: dict = {},
                 maxRedirectsAllowed: int = 0,
                 priority: QtNetwork.QNetworkRequest.Priority = QtNetwork.QNetworkRequest.NormalPriority,
                 originatingObject: QtCore.QObject = None):
        super().__init__()
        self.accessManager = QtNetwork.QNetworkAccessManager()
        for signal in ["authenticationRequired", "encrypted", "finished", "networkAccessibleChanged", "preSharedKeyAuthenticationRequired", "proxyAuthenticationRequired", "sslErrors"]:
            getattr(self.accessManager, signal).connect(lambda *args: getattr(self, signal).emit(*args))
        self.baseRequest = QtNetwork.QNetworkRequest()
        self.baseRequest.setPriority(priority)
        for key, value in headers.items():
            self.setHeader(key, value)
        for code, value in attributes.items():
            self.setAttribute(code, value)
        if maxRedirectsAllowed:
            self.setMaxRedirectsAllowed(maxRedirectsAllowed)
        if originatingObject:
            self.setOriginatingObject(originatingObject)
    
    @QtCore.pyqtSlot(QtCore.QObject)
    def setOriginatingObject(self, originatingObject: QtCore.QObject):
        self.baseRequest.setOriginatingObject(originatingObject)
    
    @QtCore.pyqtSlot(QtNetwork.QAbstractNetworkCache)
    def setCache(self, cache: QtNetwork.QAbstractNetworkCache):
        self.accessManager.setCache(cache)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkConfiguration)
    def setConfiguration(self, config: QtNetwork.QNetworkConfiguration):
        self.accessManager.setConfiguration(config)
    
    @QtCore.pyqtSlot(QtCore.QByteArray, QtCore.QByteArray)
    def setHeader(self, key: QtCore.QByteArray, value: QtCore.QByteArray):
        self.baseRequest.setRawHeader(key, value)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkRequest.Attribute, QtCore.QVariant)
    def setAttribute(self, code: QtNetwork.QNetworkRequest.Attribute, value: QtCore.QVariant):
        self.baseRequest.setAttribute(code, value)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkRequest.RedirectPolicy)
    def setRedirectPolicy(self, policy: QtNetwork.QNetworkRequest.RedirectPolicy):
        self.accessManager.setRedirectPolicy(policy)
    
    @QtCore.pyqtSlot(int)
    def setMaximumRedirectsAllowed(self, maxRedirectsAllowed: int):
        self.baseRequest.setMaximumRedirectsAllowed(maxRedirectsAllowed)
    
    @QtCore.pyqtSlot(QtNetwork.QSslConfiguration)
    def setSslConfiguration(self, sslConfiguration: QtNetwork.QSslConfiguration):
        self.baseRequest.setSslConfiguration(sslConfiguration)
    
    @QtCore.pyqtSlot(bool)
    def setStrictTransportSecurityEnabled(self, enabled: bool):
        self.accessManager.setStrictTransportSecurityEnabled(enabled)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkCookieJar)
    def setCookieJar(self, cookieJar: QtNetwork.QNetworkCookieJar):
        self.accessManager.setCookieJar(cookieJar)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkProxy)
    def setProxy(self, proxy: QtNetwork.QNetworkProxy):
        self.accessManager.setProxy(proxy)
    
    @QtCore.pyqtSlot(QtNetwork.QNetworkProxyFactory)
    def setProxyFactory(self, factory: QtNetwork.QNetworkProxyFactory):
        self.accessManager.setProxyFactory(factory)
    
    @QtCore.pyqtSlot()
    def clearAccessCache(self):
        self.accessManager.clearAccessCache()
    
    @QtCore.pyqtSlot()
    def clearConnectionCache(self):
        self.accessManager.clearConnectionCache()
    
    @QtCore.pyqtSlot(QtCore.QVector)
    def addStrictTransportSecurityHosts(knownHosts: QtCore.QVector):
        self.accessManager.addStrictTransportSecurityHosts(knownHosts)
    
    @QtCore.pyqtSlot(QtCore.QString, int, bool, QtNetwork.QSslConfiguration)
    def connect(self, hostName: QtCore.QString, port: int = 80, secure: bool = False, sslConfiguration: QtNetwork.QSslConfiguration = QtNetwork.QSslConfiguration.defaultConfiguration()):
        if secure:
            self.accessManager.connectToHostEncrypted(hostName, port, sslConfiguration = sslConfiguration)
        else:
            self.accessManager.connect(hostName, port)
    
    @QtCore.pyqtSlot(QtCore.QByteArray, QtCore.QUrl, QtCore.QByteArray, dict, dict, int, QtNetwork.QNetworkRequest.Priority, QtCore.QObject, callable, result = QtNetwork.QNetworkReply)
    def request(self, method: QtCore.QByteArray, url: QtCore.QUrl, data: QtCore.QByteArray = b"",
                headers: dict = {}, attributes: dict = {},
                maxRedirectsAllowed: int = 0,
                priority: QtNetwork.QNetworkRequest.Priority = QtNetwork.QNetworkRequest.NormalPriority,
                originatingObject: QtCore.QObject = None,
                callback: callable = None):
        request = QtNetwork.QNetworkRequest(self.baseRequest)
        request.setUrl(url)
        request.setPriority(priority)
        for key, value in headers.items():
            request.setRawHeader(key, value)
        for code, value in attributes.items():
            request.setAttribute(code, value)
        if maxRedirectsAllowed:
            request.setMaxRedirectsAllowed(maxRedirectsAllowed)
        if originatingObject:
            request.setOriginatingObject(originatingObject)
        reply = self.accessManager.sendCustomRequest(request, method, data)
        for signal in ["downloadProgress", "error", "metaDataChanged", "redirectAllowed", "redirected", "uploadProgress"]:
            getattr(reply, signal).connect(lambda *args: getattr(self, signal).emit(*args))
        if callback:
            reply.readyRead.connect(callback)
        return reply
