import machine, time, struct
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

def fetch(synch_with_rtc=True, timeout=10):
  ntp_host = "pool.ntp.org"

  if socket is None:
    print("NTP: Socket module not available")
    return None

  timestamp = None
  try:
    query = bytearray(48)
    query[0] = 0x1b
    address = socket.getaddrinfo(ntp_host, 123)[0][-1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    sock.sendto(query, address)
    data = sock.recv(48)
    sock.close()
    local_epoch = 2208988800 # selected by Chris - blame him. :-D
    timestamp = struct.unpack("!I", data[40:44])[0] - local_epoch
    timestamp = time.gmtime(timestamp)
  except Exception as e:
    print(f"NTP fetch error: {e}")
    return None

  # if requested set the machines RTC to the fetched timestamp
  if synch_with_rtc:
    machine.RTC().datetime((
      timestamp[0], timestamp[1], timestamp[2], timestamp[6], 
      timestamp[3], timestamp[4], timestamp[5], 0))      

  return timestamp