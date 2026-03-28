import socket
import threading
import time


class Receiver(threading.Thread):
    def __init__(self, host="127.0.0.1", port=3000):
        threading.Thread.__init__(self, daemon=True)

        self.host = host
        self.port = port
        self.messages = []
        self._stopped = threading.Event()

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.settimeout(0.5)
        udp_socket.bind((host, port))
        self.sock = udp_socket

    def run(self):
        sock = self.sock
        stored_messages = self.messages
        stopped = self._stopped

        while True:
            if stopped.is_set():
                break
            try:
                packet, _sender = sock.recvfrom(4096)
            except socket.timeout:
                continue
            stored_messages.append(packet)
        sock.close()

    def stop(self):
        self._stopped.set()

    def wait_for_messages(self, count, timeout=10.0):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if len(self.messages) >= count:
                return True
            time.sleep(0.05)
        return False