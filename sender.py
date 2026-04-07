from socket import *
import time
from packet import generate_message_id, generate_signing_keypair, wrap_layer

class Sender:
    def __init__(self, nodes):
        self.nodes = nodes
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.metrics = {
            'sent_total': 0,
            'recv_total': 0,
            'dropped_total': 0,
            'decrypt_fail_total': 0,
            'batch_fill_time_ms': [],
            'queue_depth': 0,
            'forward_latency_ms': [],
        }

    def send(self, message, receiver_ip, receiver_port, verbose=False):
        message_id = generate_message_id()
        timestamp = time.time()
        signing_key, _verify_key = generate_signing_keypair()
        payload = message
        for i, (ip, port, pub_key) in enumerate(reversed(self.nodes)):
            if i == 0:  
                payload = wrap_layer(payload, receiver_ip, receiver_port, pub_key, message_id, timestamp, signing_key)
            else:
                next_ip, next_port, _ = self.nodes[len(self.nodes) - i]
                payload = wrap_layer(payload, next_ip, next_port, pub_key, message_id, timestamp, signing_key)
        try:
            self.sock.sendto(payload, (self.nodes[0][0], self.nodes[0][1]))
            self.metrics['sent_total'] += 1
        except OSError:
            self.metrics['dropped_total'] += 1
            return False

        if verbose:
            first_ip, first_port, _ = self.nodes[0]
            print(f"[sender] sent {len(payload)} bytes to first node {first_ip}:{first_port} message_id={message_id}")
        return True