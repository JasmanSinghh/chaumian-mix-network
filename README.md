# Anonymity-Latency Trade-Off Analysis in Chaumian Mix Networks

A Python implementation of a Chaumian Mix Network studying the trade-off between anonymity set size and end-to-end communication latency. 

## Overview
This project implements a Chaumian Mix Network. It's an architecture designed for high-latency and privacy preserving communication. Mix nodes batch, shuffle, and forward messages to break timing correlation attacks, making it tough for outside observers to match incoming messages to outgoing ones. 

Similar to Tor, messages are encrypted multiple times in "layers," each containing the address of the chosen nodes in the path and decryption happening at each node with their own private key. Unlike Tor, which forwards packets immediately, mix nodes in this system hold messages in memory until a specific condition is met (e.g. 1000 messages), it then decrypts the layer for all 1000 messages, shuffles the order and transmits the batch. 

The research goal is to study the trade-off between the anonymity set and the end-to-end latency through traffic throughput analysis. 

## Components
- 
