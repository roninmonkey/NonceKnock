#!/usr/bin/env python3 

import socket 
import re 
import sys 

# ====== CONFIGURE ====== 

TARGET_IP = "target"  # <-- change this 

TOTAL_STEPS = 14 

SOCKET_TIMEOUT = 2    # seconds 

# ===================== 

def connect_and_receive(ip, port, message=None): 

    """Connect to the given IP and port, optionally send a message, and receive response.""" 
    try: 
        with socket.create_connection((ip, port), timeout=SOCKET_TIMEOUT) as sock: 
            sock.settimeout(SOCKET_TIMEOUT) 
            if message: 
                sock.sendall((message + "\n").encode()) 
            data = sock.recv(4096).decode(errors="ignore") 
            return data.strip() 
    except Exception as e: 
        print(f"[!] Connection error on port {port}: {e}") 
        return "" 
  
def parse_response(response): 
    """Parse next port and nonce from server's message.""" 
    next_port = None 
    next_nonce = None 

    port_match = re.search(r"Next port:\s*(\d+)", response) 
    nonce_match = re.search(r"Next nonce:\s*([0-9a-fA-F]+)", response) 
  
    if port_match: 
        next_port = int(port_match.group(1)) 
    if nonce_match: 
        next_nonce = nonce_match.group(1) 
    return next_port, next_nonce 

def main(): 
    if len(sys.argv) != 2: 
        print(f"Usage: {sys.argv[0]} <start_port>") 
        sys.exit(1) 
    current_port = int(sys.argv[1]) 

    print(f"[*] Starting knock sequence on {TARGET_IP}...") 

    # First connection: get first port and nonce 

    response = connect_and_receive(TARGET_IP, current_port) 

    print(f"[*] Initial server response:\n{response}\n") 
    next_port, next_nonce = parse_response(response) 
    if not next_port or not next_nonce: 

        print("[!] Failed to parse next port or nonce from initial connection. Exiting.") 
        sys.exit(1) 
    for step in range(1, TOTAL_STEPS): 

        print(f"[*] Step {step}: Sending nonce {next_nonce} to port {next_port}...") 
        response = connect_and_receive(TARGET_IP, next_port, next_nonce) 

        print(f"[*] Server response:\n{response}\n") 
        next_port, next_nonce = parse_response(response) 
  
        if not next_port or not next_nonce: 
            print("[!] Failed to parse next port or nonce after sending. Exiting.") 
            sys.exit(1) 

if __name__ == "__main__": 
    main() 
