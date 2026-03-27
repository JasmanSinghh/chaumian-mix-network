import time
import socket
import pytest
from packet import generate_keypair, wrap_layer, unwrap_layer
# from receiver import Receiver
from mixnode import MixNode

mix_node_port = 5001
receiver_port = 3000
test_message = b"payload to  receiver"
test_ip = "127.0.0.1"

#Fixtures - defined context for the tests.

@pytest.fixture
def keypair():
    return generate_keypair()

@pytest.fixture
def mix_node():
    "Start a single mix node"
    priv, _ = generate_keypair()
    node = MixNode(port=mix_node_port, private_key=priv, batch_size=3)
    node.daemon = True
    node.start()
    time.sleep(0.1)
    yield node

@pytest.fixture
def receiver():
    "Start receiver on fixed port"
    r = Receiver(port=receiver_port)
    r.start()
    yield r
    r.stop()
    r.join(timeout=2)




#Tests for mix nodes

def test_mixnode_starts(mix_node):
    "After starting the mix node must stay alive"
    assert mix_node.is_alive()


def test_mixnode_unwraps_layer(keypair):
    "unwrap_layer should take  off one layer and return the original payload"
    
    priv, pub = keypair
    payload = b"This is a mix network"
    wrapped = wrap_layer(payload, test_ip, receiver_port, pub)

    ip, port, recovered = unwrap_layer(wrapped, priv)

    assert ip == test_ip
    assert port == receiver_port
    assert recovered == payload


#Tests for receiver

def test_receiver_starts(receiver):
    "After starting the receiver thread must stay alive"
    assert receiver.is_alive()


def test_receiver_gets_message(receiver):
    "A UDP packet sent to the receiver should appear in get_messages()"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(test_message, (test_ip, receiver_port))

    arrived = receiver.wait_for_messages(count=1, timeout=3)

    assert arrived
    assert test_message in receiver.get_messages()