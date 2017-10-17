from stem.util import term
import stem.util.connection, stem.util.system, stem.connection, stem.process, stem.control
import colorama, socket, socks, os


__doc__ = "Multi class module to interact with tor processes, hidden services, sockets, etc ..."

colorama.init(autoreset=True)

pids = lambda: stem.util.system.pid_by_name("tor", multiple = True)
resolvers = stem.util.connection.system_resolvers()
connections = lambda pid=None, resolver=None: stem.util.connection.get_connections(resolver if resolver else self.resolvers[0], process_pid = pid if pid else self.pids()[0], process_name = "tor") if self.resolvers and self.pids else None

class Controller(stem.control.Controller):
    def __init__(self, address: str = "127.0.0.1", port: int = "default", password: str = None, chroot_path: str = None, protocolinfo_response=None):
        if not stem.util.connection.is_valid_ipv4_address(address):
            raise ValueError("Invalid IP address: %s" % address)
        elif port != "default" and not stem.util.connection.is_valid_port(port):
            raise ValueError("Invalid port: %s" % port)
        
        if port == "default":
            control_port = stem.connection._connection_for_default_port(address)
        else:
            control_port = stem.socket.ControlPort(address, port)
        super(Controller, self).__init__(control_port)
        self.authenticate(password=password, chroot_path=chroot_path, protocolinfo_response=protocolinfo_response)

class Tor(object):
    def __init__(self):
        self.process = None
        self.config = {"SocksPort": 9150, "ControlPort": 9151}
    
    def _handle_line(self, line):
        if "Bootstrapped" in line:
            print(line)
    
    def start(self, quiet: bool = True, msg_prefix: str = "", msg_color: str = "yellow", **config):
        """Start this Tor instance and a new tor process ...
           Argumments:
           - quiet: If True, print bootstrap lines.
           - **config: Config to pass to the process at its initialization."""
        if not self.process:
            for key, value in self.config.items():
                if key not in config:
                    config[key] = str(value)
            self.process = stem.process.launch_tor_with_config(config = config, init_msg_handler = None if quiet else lambda line: self._handle_line(term.format(f"{msg_prefix}{line}", msg_color)))
            self.config = config
    
    def exit(self):
        """Kill this Tor process only if it already have successfully started, otherwise, pass."""
        if self.process:
            self.process.kill()

class HiddenService(object):
    def __init__(self, address, controller: Controller = None):
        self.controller = controller if controller else Controller()
        
        self.address = (address + ".onion" if len(address) == 16 else address).lower()
        self.descriptor = self.controller.get_hidden_service_descriptor(address)
        self.introduction_points = self.descriptor.introduction_points
        for key in self.descriptor.ATTRIBUTES:
            setattr(self, key, getattr(self.descriptor, key))

class EphemeralHiddenService(HiddenService):
    def __init__(self, ports: dict = {80: 80}, discard_key: bool = False, detached: bool = False, private_key = None, controller: Controller = None):
        controller = controller if controller else Controller()
        
        kwargs = {"await_publication": True, "discard_key": discard_key, "detached": detached}
        if private_key:
            data = chunk = private_key.read(0xFFF)
            while chunk:
                chunk = private_key.read(0xFFF)
                data += chunk
            ktype, kcontent = data.split(":", 1)
            self.private_key = {"type": ktype, "content": kcontent}
            kwargs.update({"key_type": ktype, "key_content": kcontent})
        service = controller.create_ephemeral_hidden_service(ports, **kwargs)
        for key, value in service.__dict__.items():
            setattr(self, key, value)
        super(EphemeralHiddenService, self).__init__(self.service_id, controller)
    
    def discontinue(self):
        return self.controller.remove_ephemeral_hidden_service(self.service_id)
