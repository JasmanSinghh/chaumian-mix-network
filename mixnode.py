import socket
import threading
import random
import time
from packet import unwrap_layer

class MixNode(threading.Thread):
  def __init__(self, port, private_key, batch_size, flush_timeout=0.5):
    super().__init__()
    self.port = port
    self.private_key = private_key
    self.batch_size = batch_size
    self.flush_timeout = flush_timeout
    self.batch = []
    self.first_packet_time = None
    self.lock = threading.Lock()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(0.05)
    self.sock.bind(('127.0.0.1', self.port))

  def run(self):
    print(f"MixNode listening on {self.port}...")
    while True:
      try:
        data, _addr = self.sock.recvfrom(4096)
      except socket.timeout:
        with self.lock:
          should_flush = (
            self.batch
            and self.first_packet_time is not None
            and (time.time() - self.first_packet_time) >= self.flush_timeout
          )
          if should_flush:
            self.process_batch()
        continue

      with self.lock:
        if not self.batch:
          self.first_packet_time = time.time()
        self.batch.append(data)
        if len(self.batch) >= self.batch_size:
          self.process_batch()

  def process_batch(self):
    packets_to_process = self.batch[:]
    random.shuffle(packets_to_process)

    for encrypted_packet in packets_to_process:
      next_hop_ip, next_hop_port, decrypted_payload = unwrap_layer(
        encrypted_packet, 
        self.private_key
      )
      if next_hop_ip is None or next_hop_port is None or decrypted_payload is None:
        continue
      self.sock.sendto(decrypted_payload, (next_hop_ip, next_hop_port))

    self.batch.clear()
    self.first_packet_time = None