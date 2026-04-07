# driver.py — the missing orchestrator
import threading
import time
from statistics import mean
from packet import generate_keypair
from mixnode import MixNode
from receiver import Receiver
from sender import Sender


def format_latency_stats(latencies):
    if not latencies:
        return "no latency samples"

    sorted_latencies = sorted(latencies)

    def percentile(percent):
        if len(sorted_latencies) == 1:
            return sorted_latencies[0]
        index = (len(sorted_latencies) - 1) * percent
        lower = int(index)
        upper = min(lower + 1, len(sorted_latencies) - 1)
        fraction = index - lower
        return sorted_latencies[lower] * (1 - fraction) + sorted_latencies[upper] * fraction

    return (
        f"count={len(sorted_latencies)} "
        f"avg={mean(sorted_latencies):.4f}s "
        f"p50={percentile(0.50):.4f}s "
        f"p95={percentile(0.95):.4f}s "
        f"p99={percentile(0.99):.4f}s "
        f"max={sorted_latencies[-1]:.4f}s"
    )

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

for node in [node1, node2, node3]:
    latencies = [
        entry['node_latency_seconds']
        for entry in node.stats['messages_by_id'].values()
    ]
    print(
        f"[node {node.port}] processed={node.stats['messages_processed']} "
        f"decrypt_failures={node.stats['decrypt_failures']} "
        f"duplicates={node.stats['duplicate_messages']} "
        f"latency={format_latency_stats(latencies)}"
    )


