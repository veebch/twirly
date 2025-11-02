import uasyncio
try:
    # Try modern socket import first
    import socket
except ImportError:
    try:
        # Fall back to old usocket for older MicroPython
        import usocket as socket
    except ImportError:
        print("WARNING: No socket module available")
        socket = None
from . import logging

async def _handler(socket_obj, ip_address):
  while True:
    try:
      # Simple approach - poll for data availability
      await uasyncio.sleep_ms(10)  # Small delay to prevent busy loop
      try:
        request, client = socket_obj.recvfrom(256)
      except OSError:
        # No data available, continue loop
        continue
        
      response = request[:2] # request id
      response += b"\x81\x80" # response flags
      response += request[4:6] + request[4:6] # qd/an count
      response += b"\x00\x00\x00\x00" # ns/ar count
      response += request[12:] # origional request body
      response += b"\xC0\x0C" # pointer to domain name at byte 12
      response += b"\x00\x01\x00\x01" # type and class (A record / IN class)
      response += b"\x00\x00\x00\x3C" # time to live 60 seconds
      response += b"\x00\x04" # response length (4 bytes = 1 ipv4 address)
      response += bytes(map(int, ip_address.split("."))) # ip address parts
      socket_obj.sendto(response, client)
    except Exception as e:
      logging.error(f"DNS handler error: {e}")
      await uasyncio.sleep_ms(100)  # Prevent tight error loops

def run_catchall(ip_address, port=53):
  if socket is None:
    logging.error("No socket module available - DNS server cannot start")
    return
    
  logging.info("> starting catch all dns server on port {}".format(port))

  try:
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.setblocking(False)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _socket.bind(socket.getaddrinfo(ip_address, port, 0, socket.SOCK_DGRAM)[0][-1])

    loop = uasyncio.get_event_loop()
    loop.create_task(_handler(_socket, ip_address))
    logging.info(f"DNS catchall server started on {ip_address}:{port}")
  except Exception as e:
    logging.error(f"Failed to start DNS server: {e}")
    return