# driver.py — the missing orchestrator
import threading
import time
from packet import generate_keypair
from mixnode import MixNode
from receiver import Receiver
from sender import Sender

priv1, pub1 = generate_keypair()
priv2, pub2 = generate_keypair()
priv3, pub3 = generate_keypair()

receiver = Receiver()
receiver.start()
print("Driver created receiver on port", receiver.port)

node1 = MixNode(port=5001, private_key=priv1, batch_size=3)
node2 = MixNode(port=5002, private_key=priv2, batch_size=3)
node3 = MixNode(port=5003, private_key=priv3, batch_size=3)
for n in [node1, node2, node3]:
    n.daemon = True
    n.start()
time.sleep(0.2)  

nodes = [
    ('127.0.0.1', 5001, pub1),
    ('127.0.0.1', 5002, pub2),
    ('127.0.0.1', 5003, pub3),
]
sender = Sender(nodes)
for i in range(10):
    sender.send(f"message number {i}".encode(), '127.0.0.1', 9000)
time.sleep(2)
print("Receiver got:")
for message in receiver.get_messages():
    print(message.decode("utf-8"))


