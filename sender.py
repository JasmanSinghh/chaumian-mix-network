from socket import *
from packet import generate_keypair, wrap_layer

class Sender:
    def __init__(self, nodes):
        self.nodes = nodes
        self.sock = socket(AF_INET, SOCK_DGRAM)

    def send(self, message, receiver_ip, receiver_port):
        payload = message
        for i, (ip, port, pub_key) in enumerate(reversed(self.nodes)):
            if i == 0:  
                payload = wrap_layer(payload, receiver_ip, receiver_port, pub_key)
            else:
                next_ip, next_port, _ = self.nodes[len(self.nodes) - i]
                payload = wrap_layer(payload, next_ip, next_port, pub_key)
        self.sock.sendto(payload, (self.nodes[0][0], self.nodes[0][1]))
        first_ip, first_port, _ = self.nodes[0]
        print(f"[sender] sent {len(payload)} bytes to first node {first_ip}:{first_port}")