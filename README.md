# Anonymity-Latency Trade-Off Analysis in Chaumian Mix Networks

A Python implementation of a Chaumian Mix Network for studying the trade-off between anonymity set size and end-to-end latency.

## Overview
This project models a Chaumian mix network where each message is onion-encrypted and forwarded through multiple mix nodes. Each mix node batches traffic, shuffles order, decrypts one layer, and forwards to the next hop.

Compared with immediate forwarding systems, this implementation intentionally delays forwarding to increase anonymity. It now supports mixed flush policies, randomized timing behavior, authenticated per-layer metadata, and runtime metrics.

## Implemented Features
1. Layered onion routing over UDP with per-hop decryption.
2. Mixed flush policy in mix nodes:
	- Count-based flush when `batch_size` is reached.
	- Timeout-based flush when buffered packets wait past `flush_timeout`.
3. Bounded forwarding jitter:
	- Random delay before batch forwarding to reduce timing correlation.
4. Authenticated metadata per layer:
	- Each layer includes `message_id` and `timestamp`.
	- Routing metadata + payload are signed and verified at each hop.
5. Replay/duplicate suppression in mix nodes.
6. Live receiver output while the driver is running.
7. Runtime metrics for sender, receiver, and mix nodes.

## Runtime Metrics
The following metric names are tracked in components:
- `sent_total`
- `recv_total`
- `dropped_total`
- `decrypt_fail_total`
- `batch_fill_time_ms`
- `queue_depth`
- `forward_latency_ms`

Notes:
- `batch_fill_time_ms` and `forward_latency_ms` are most meaningful on mix nodes.
- Metrics are printed on shutdown (Ctrl+C in continuous mode, or normal exit in bounded mode).

## Project Components
- `packet.py`: cryptographic primitives, header format, wrapping/unwrapping, metadata signing and verification.
- `mixnode.py`: batch queueing, mixed flush policy, jittered forwarding, duplicate filtering, per-node metrics.
- `sender.py`: message generation, onion construction, send logic, sender metrics.
- `receiver.py`: terminal sink for decrypted payloads and receiver metrics.
- `driver.py`: orchestration, CLI options, live message printing, and end-of-run stats.
- `test.py`: unit tests for core packet and node behavior.

## CLI: How To Run
Run from the repository root.

Basic continuous run:

```bash
python3 driver.py
```

Send a fixed number of messages and exit:

```bash
python3 driver.py -m 30
```

## CLI Flags ("tags")
The driver supports these options:

1. `-m`, `--messages <int>`
	- Send exactly this many messages, then exit.
	- If omitted, run continuously until interrupted.

2. `--interval <float>`
	- Fixed delay in seconds between generated messages.
	- Default is `0.0` (send as fast as possible unless random interval is used).

3. `-r`, `--random-interval-max <float>`
	- Randomize message generation interval between `1.0` and this max (seconds).
	- Must be `>= 1.0`.
	- Takes precedence over `--interval` when provided.

4. `--jitter-max <float>`
	- Max random delay in seconds before each mix node forwards a flushed batch.
	- Applied as a bounded random value in `[0, jitter_max]`.
	- Must be `>= 0`.

5. `--quiet`
	- Suppress per-message sender logs (default behavior).

6. `--verbose`
	- Enable per-message sender logs.

## Example Commands
Continuous run with randomized message generation up to 5 seconds:

```bash
python3 driver.py -r 5
```

Send 50 messages with randomized generation interval up to 5 seconds:

```bash
python3 driver.py -m 50 -r 5
```

Send 100 messages, fixed 0.2s interval, and add up to 0.5s forwarding jitter per batch:

```bash
python3 driver.py -m 100 --interval 0.2 --jitter-max 0.5
```

Continuous run with sender debug logs enabled:

```bash
python3 driver.py --verbose
```

## Shutdown Behavior
- In continuous mode, press `Ctrl+C` to stop.
- On exit, the driver prints endpoint and per-node statistics, including latency summaries.

## Cryptography
The implementation uses PyNaCl (Libsodium), including:
- `SealedBox` for layered public-key encryption.
- Ed25519 signatures for per-layer integrity/authentication of routing metadata and payload.

This combination protects confidentiality and helps prevent malformed routing metadata from silently propagating.
