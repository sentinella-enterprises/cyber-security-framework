import hashlib, uuid, struct, os

class XPacket(object):
    source: uuid.UUID
    destination: uuid.UUID
    identification: uuid.UUID
    verification: uuid.UUID
    chunks: int
    data: bytes
    def __init__(self, source: uuid.UUID, destination: uuid.UUID, data: bytes = b""):
        self.source = source
        self.destination = destination
        self.data = data

    def pack(self):
        self.chunks = (len(self.data) // 0xFFFF) + 1
        packet = struct.pack("!BQQQQB", 88, # X! Packet Identification
                                        (self.source.int >> 64) & 0xFFFFFFFFFFFFFFFF, self.source.int & 0xFFFFFFFFFFFFFFFF, # Source UUID
                                        (self.destination.int >> 64) & 0xFFFFFFFFFFFFFFFF, self.destination.int & 0xFFFFFFFFFFFFFFFF, # Destination UUID
                                         self.chunks) # Chunk ID
        self.identification = uuid.UUID(bytes = hashlib.sha1(self.source.bytes + packet + hashlib.sha1(self.data).digest()).digest()[:16], version = 5)
        packet += struct.pack("!QQ", (self.identification.int >> 64) & 0xFFFFFFFFFFFFFFFF, self.identification.int & 0xFFFFFFFFFFFFFFFF) # Identification UUID
        self.chunks -= 1
        if self.data:
            _, chunk, data = self.data.partition(self.data[:0xFFFF - len(packet) - 16])
            verification = hashlib.sha1(chunk)
            vuuid = uuid.UUID(bytes = verification.digest()[:16])
            chunk += struct.pack("!QQB", (vuuid.int >> 64) & 0xFFFFFFFFFFFFFFFF, vuuid.int & 0xFFFFFFFFFFFFFFFF, self.chunks)
            packet += chunk
            self.chunks -= 1
            while chunk:
                chunk = data[:0xFFFF - 17]
                if chunk:
                    _, chunk, data = data.partition(chunk)
                    verification.update(chunk)
                    vuuid = uuid.UUID(bytes = verification.digest()[:16])
                    chunk += struct.pack("!QQB", (vuuid.int >> 64) & 0xFFFFFFFFFFFFFFFF, vuuid.int & 0xFFFFFFFFFFFFFFFF, self.chunks)
                    packet += chunk
                    self.chunks -= 1
            self.verification = vuuid
        return packet
    
    @staticmethod
    def load(self, socket, verify: bool = True):
        packet = socket.recv(0xFFFF)
        _, header, data = packet.partition(packet[:50])
        x, s1, s2, d1, d2, chunks, i1, i2 = struct.unpack("!BQQQQBQQ", header)
        if verify:
            assert bytes([x]) == b"X", ValueError("Not a valid X-Packet!")
        source = uuid.UUID(int = (s1 << 64) | s2, version = 5)
        destination = uuid.UUID(int = (d1 << 64) | d2, version = 5)
        identification = uuid.UUID(int = (i1 << 64) | i2, version = 5)
        content = b""
        if chunks:
            if verify:
                assert data, ValueError("Invalid chunking header!")
            chunk, field, _ = data.partition(data[-17:])
            check = hashlib.sha1(chunk)
            vuuid = uuid.UUID(bytes = check.digest()[:16])
            v1, v2, id = struct.unpack("!QQB")
            verification = uuid.UUID(int = (v1 << 64) | v2)
            if verify:
                assert vuuid == verification, ValueError(f"Invalid verification UUID on chunk #{chunks}!")
                assert id == chunks, ValueError(f"Invalid data-chunk identification number on chunk #{chunks}!")
            content += chunk
            chunks -= 1
            while chunks:
                data = socket.recv(0xFFFF)
                chunk, field, _ = data.partition(data[-17:])
                check.update(chunk)
                vuuid = uuid.UUID(bytes = check.digest()[:16])
                v1, v2, id = struct.unpack("!QQB")
                verification = uuid.UUID(int = (v1 << 64) | v2)
                if verify:
                    assert vuuid == verification, ValueError(f"Invalid verification UUID on chunk #{chunks}!")
                    assert id == chunks, ValueError(f"Invalid data-chunk identification number on chunk #{chunks}!")
                content += chunk
                chunks -= 1
        if verify:
            data_hash = hashlib.sha1(content).digest()
            assert data_hash == check, ValueError(f"Invalid data checksum!")
            assert uuid.UUID(bytes = hashlib.sha1(source.bytes + header + data_hash).digest()[:16], version = 5) == identification, ValueError(f"Invalid identification header!")
        packet = XPacket(source, destination, content)
        packet.pack()
        return packet
