import nacl.exceptions
from nacl.public import PrivateKey, SealedBox

def generate_keypair():
  private_key = PrivateKey.generate()
  public_key = private_key.public_key
  return private_key, public_key

def create_routing_header(ip, port):
  return f"{ip}:{port}|".encode('utf-8')

def wrap_layer(payload, nexthop_ip, nexthop_port, dest_pub_key):
  header = create_routing_header(nexthop_ip, nexthop_port)
  full_payload = header + payload
  
  box = SealedBox(dest_pub_key)
  return box.encrypt(full_payload)

def unwrap_layer(encrypted_payload, private_key):
  box = SealedBox(private_key)

  try:
    decrypted = box.decrypt(encrypted_payload)
  except nacl.exceptions.CryptoError:
    return None, None, None
  
  parts = decrypted.split(b'|', 1)

  if len(parts) != 2:
    return None, None, None
  
  routing = parts[0].decode('utf-8')
  payload = parts[1]

  ip_port = routing.split(':')
  if len(ip_port) != 2:
    return None, None, None
  
  nexthop_ip = ip_port[0]
  nexthop_port = int(ip_port[1])

  return nexthop_ip, nexthop_port, payload