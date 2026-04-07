import nacl.exceptions
from nacl.public import PrivateKey, SealedBox
import time
import uuid

def generate_keypair():
  private_key = PrivateKey.generate()
  public_key = private_key.public_key
  return private_key, public_key

def generate_message_id():
  """Generate a unique message ID."""
  return str(uuid.uuid4())

def create_routing_header(ip, port, message_id=None, timestamp=None):
  """Create routing header with IP, port, message_id, and timestamp.
  
  Format: ip:port|timestamp|message_id|
  """
  if message_id is None:
    message_id = generate_message_id()
  if timestamp is None:
    timestamp = time.time()
  
  return f"{ip}:{port}|{timestamp}|{message_id}|".encode('utf-8')

def wrap_layer(payload, nexthop_ip, nexthop_port, dest_pub_key, message_id=None, timestamp=None):
  """Wrap payload with routing header and encrypt.
  
  message_id and timestamp are preserved across layers.
  """
  header = create_routing_header(nexthop_ip, nexthop_port, message_id, timestamp)
  full_payload = header + payload
  
  box = SealedBox(dest_pub_key)
  return box.encrypt(full_payload)

def _unwrap_layer_internal(encrypted_payload, private_key):
  """Unwrap one layer of encryption and return routing metadata."""
  box = SealedBox(private_key)

  try:
    decrypted = box.decrypt(encrypted_payload)
  except nacl.exceptions.CryptoError:
    return None, None, None, None, None
  
  parts = decrypted.split(b'|', 3)

  if len(parts) != 4:
    return None, None, None, None, None

  routing = parts[0].decode('utf-8')
  timestamp_raw = parts[1].decode('utf-8')
  message_id = parts[2].decode('utf-8')
  payload = parts[3]

  ip_port_parts = routing.split(':', 1)
  if len(ip_port_parts) != 2:
    return None, None, None, None, None
  
  nexthop_ip = ip_port_parts[0]

  try:
    nexthop_port = int(ip_port_parts[1])
    timestamp = float(timestamp_raw)
  except ValueError:
    return None, None, None, None, None

  return nexthop_ip, nexthop_port, payload, message_id, timestamp

def unwrap_layer(encrypted_payload, private_key):
  """Backward-compatible unwrap that returns only routing and payload."""
  nexthop_ip, nexthop_port, payload, _message_id, _timestamp = _unwrap_layer_internal(
    encrypted_payload,
    private_key,
  )
  return nexthop_ip, nexthop_port, payload

def unwrap_layer_with_metadata(encrypted_payload, private_key):
  """Unwrap a layer and return routing plus metadata."""
  return _unwrap_layer_internal(encrypted_payload, private_key)