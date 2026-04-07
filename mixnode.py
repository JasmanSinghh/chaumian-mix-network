import socket
import threading
import random
import time
from collections import deque
from packet import unwrap_layer_with_metadata

class MixNode(threading.Thread):
  def __init__(self, port, private_key, batch_size, flush_timeout=0.5):
    super().__init__()
    self.port = port
    self.private_key = private_key
    self.batch_size = batch_size
    self.flush_timeout = flush_timeout
    self.batch = []
    self.first_packet_time = None
    self.recent_message_ids = deque(maxlen=1000)
    self.recent_message_id_set = set()
    self.lock = threading.Lock()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(0.05)
    self.sock.bind(('127.0.0.1', self.port))
    self.stats = {
      'messages_processed': 0,
      'duplicate_messages': 0,
      'decrypt_failures': 0,
      'messages_by_id': {}
    }

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
      next_hop_ip, next_hop_port, decrypted_payload, message_id, timestamp = unwrap_layer_with_metadata(
        encrypted_packet, 
        self.private_key
      )
      if next_hop_ip is None or next_hop_port is None or decrypted_payload is None:
        self.stats['decrypt_failures'] += 1
        continue

      if message_id in self.recent_message_id_set:
        self.stats['duplicate_messages'] += 1
        continue

      if len(self.recent_message_ids) == self.recent_message_ids.maxlen:
        evicted_message_id = self.recent_message_ids.popleft()
        self.recent_message_id_set.discard(evicted_message_id)

      self.recent_message_ids.append(message_id)
      self.recent_message_id_set.add(message_id)

      now = time.time()
      self.sock.sendto(decrypted_payload, (next_hop_ip, next_hop_port))
      self.stats['messages_processed'] += 1
      self.stats['messages_by_id'][message_id] = {
        'created_at': timestamp,
        'processed_at': now,
        'node': self.port,
        'node_latency_seconds': now - timestamp
      }

    self.batch.clear()
    self.first_packet_time = None