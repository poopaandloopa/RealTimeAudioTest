import socket
import wave


class RTPReceiver:
    def __init__(self, address, port, wav_output, raw_output):
        self.address = address
        self.port = port
        self.wav_output = wav_output
        self.raw_output = raw_output
        self.sock = None
        self.wav_file = None
        self.raw_file = None

    def connect(self):
        """Bind a socket and start listening on the specified address and port."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.address, self.port))
        print(f"Listening on {self.address}:{self.port}")

    def _extract_rtp_payload(self, data):
        """Extract the payload from an RTP packet."""
        first_byte = data[0]
        cc = first_byte & 0x0F  # Last 4 bits are CC
        x = (first_byte & 0x10) >> 4  # 5th bit is X

        header_length = 12 + cc * 4  # Base header + CSRCs

        if x:
            extension_length = int.from_bytes(data[header_length + 2:header_length + 4], "big") * 4
            header_length += 4 + extension_length

        return data[header_length:]

    def receive(self, buffer_size=2048):
        """Receive RTP packets, extract audio payload and save to specified files."""
        # Initialize WAV file for saving
        self.wav_file = wave.open(self.wav_output, 'wb')
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(2)  # 16-bit audio
        self.wav_file.setframerate(16000)  # 16000Hz sampling rate

        try:
            while True:
                data, _ = self.sock.recvfrom(buffer_size)
                payload = self._extract_rtp_payload(data)
                self.wav_file.writeframes(payload)
                yield payload
        except KeyboardInterrupt:
            print("Receiver stopped.")
        finally:
            self.wav_file.close()
            self.sock.close()
