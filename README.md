# Anonymity-Latency Trade-Off Analysis in Chaumian Mix Networks

A Python implementation of a Chaumian Mix Network studying the trade-off between anonymity set size and end-to-end communication latency. 

## Overview
This project implements a Chaumian Mix Network. It's an architecture designed for high-latency and privacy preserving communication. Mix nodes batch, shuffle, and forward messages to break timing correlation attacks, making it tough for outside observers to match incoming messages to outgoing ones. 

Similar to Tor, messages are encrypted multiple times in "layers," each containing the address of the chosen nodes in the path and decryption happening at each node with their own private key. Unlike Tor, which forwards packets immediately, mix nodes in this system hold messages in memory until a specific condition is met (e.g. 1000 messages), it then decrypts the layer for all 1000 messages, shuffles the order and transmits the batch. 

The research goal is to study the trade-off between the anonymity set and the end-to-end latency through traffic throughput analysis. 

## Components
- `packet.py`: The shared cryptographic and routing infrastructure. Handles the PyNaCl (Libsodium) wrapping and unwrapping functions, key generation, and standardized routing header formatting.
- `mixnode.py`: The core router implementation. Operates as a multithreaded server that receives incoming packets, holds them in a buffer until a specific batch size is reached, shuffles the batch to prevent timing correlation, peels off the outer cryptographic layer, and forwards the payload to the next hop.
- `sender.py`: The client application responsible for generating the test traffic. Constructs the "onion" by taking a plaintext message and wrapping it in multiple layers of encryption corresponding to the reverse order of the chosen mix node path.
- `receiver.py`: The final destination server that receives the fully decrypted payload from the exit node.
- `driver.py`: The network orchestrator. Spins up multiple instances of mix nodes on different local ports to simulate the network topology, spawns concurrent sender threads to trigger batching thresholds, and handles the timing functions required for latency and throughput measurement.
- `test.py`: The testing module uses pytest to certify the functionality of system components, including mix nodes, receivers, packet handling, and end-to-end communication. Additional test cases can be used to verify reliability and performance as the system evolves. 

## Cryptography
This project utilizes `PyNaCl` (Libsodium) and its `SealedBox` construct for layered public-key encryption. This approach leverages elliptic curve cryptography (Curve25519) to keep ciphertexts and keys extremely small, avoiding packet fragmentation while guaranteeing anonymous encryption that leaves no cryptographic trace of the sender. 
