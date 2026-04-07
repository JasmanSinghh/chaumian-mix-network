# driver.py — the missing orchestrator
import argparse
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


def print_node_stats(nodes):
    for node in nodes:
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


def start_receiver_printer(receiver):
    stop_event = threading.Event()

    def printer():
        last_index = 0
        while not stop_event.is_set():
            while last_index < len(receiver.messages):
                print(receiver.messages[last_index].decode("utf-8"), flush=True)
                last_index += 1
            time.sleep(0.05)

    thread = threading.Thread(target=printer, daemon=True)
    thread.start()
    return stop_event


def build_runtime():
    priv1, pub1 = generate_keypair()
    priv2, pub2 = generate_keypair()
    priv3, pub3 = generate_keypair()

    receiver = Receiver()
    receiver.start()
    print("Driver created receiver on port", receiver.port)

    node1 = MixNode(port=5001, private_key=priv1, batch_size=3)
    node2 = MixNode(port=5002, private_key=priv2, batch_size=3)
    node3 = MixNode(port=5003, private_key=priv3, batch_size=3)
    for node in [node1, node2, node3]:
        node.daemon = True
        node.start()

    time.sleep(0.2)

    nodes = [
        ('127.0.0.1', 5001, pub1),
        ('127.0.0.1', 5002, pub2),
        ('127.0.0.1', 5003, pub3),
    ]
    sender = Sender(nodes)
    return receiver, [node1, node2, node3], sender


def run_sender_loop(sender, receiver, message_count, interval_seconds, verbose=False):
    sent_messages = 0
    try:
        while message_count is None or sent_messages < message_count:
            payload = f"message number {sent_messages}".encode()
            sender.send(payload, '127.0.0.1', 9000, verbose=verbose)
            sent_messages += 1
            if interval_seconds > 0:
                time.sleep(interval_seconds)
    except KeyboardInterrupt:
        pass

    wait_time = 2.0 if message_count is None else 1.0
    receiver.wait_for_messages(sent_messages, timeout=wait_time)


def main():
    parser = argparse.ArgumentParser(description="Run the Chaumian mix network demo")
    parser.add_argument(
        "-m",
        "--messages",
        type=int,
        default=None,
        help="Send this many messages and exit; omit for continuous running",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.0,
        help="Seconds to wait between messages in continuous mode or bounded runs",
    )
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-message sender logs (default)",
    )
    verbosity_group.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-message sender logs",
    )
    args = parser.parse_args()

    receiver, nodes, sender = build_runtime()
    receiver_printer_stop = start_receiver_printer(receiver)

    try:
        run_sender_loop(
            sender,
            receiver,
            args.messages,
            args.interval,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        pass
    finally:
        receiver_printer_stop.set()
        time.sleep(0.1)
        print_node_stats(nodes)
        receiver.stop()


if __name__ == "__main__":
    main()


