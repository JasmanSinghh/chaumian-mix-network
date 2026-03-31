import socket
import threading
import random
from packet import unwrap_layer

class MixNode(threading.Thread):
  def __init__(self, port, private_key, batch_size):
    super().__init__()
    self.port = port
    self.private_key = private_key
    self.batch_size = batch_size
    self.batch = []
    self.lock = threading.Lock()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('127.0.0.1', self.port))

  def run(self):
    print(f"MixNode listening on {self.port}...")
    while True:
      data, addr = self.sock.recvfrom(4096)

      with self.lock:
        self.batch.append(data)
        if len(self.batch) >= self.batch_size:
          self.process_batch()

  def process_batch(self):
    random.shuffle(self.batch)

    for encrypted_packet in self.batch:
      next_hop_ip, next_hop_port, decrypted_payload = unwrap_layer(
        encrypted_packet, 
        self.private_key
      )
      self.sock.sendto(decrypted_payload, (next_hop_ip, next_hop_port))

    self.batch.clear()