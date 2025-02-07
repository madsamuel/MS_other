import pydivert

def main():
    """
    This script blocks (drops) all inbound packets from remote TCP ports 80 or 443.
    That effectively disables most HTTP/HTTPS downloads.
    """

    # WinDivert filter for inbound traffic where the *source* port is 80 or 443.
    # i.e., traffic coming FROM the web server (port 80/443) TO your PC.
    filter_str = "inbound and tcp and (tcp.SrcPort == 80 or tcp.SrcPort == 443)"

    print(f"Starting WinDivert with filter: {filter_str}")
    print("All inbound HTTP/HTTPS traffic will be dropped. Press Ctrl+C to stop.")

    with pydivert.WinDivert(filter_str) as w:
        # The 'with' statement automatically opens the WinDivert handle.
        while True:
            packet = w.recv()  
            # We do NOT re-inject (w.send(packet)). This means the packet is dropped.
            # If you wanted to allow some packets, you'd add logic here and call w.send() conditionally.
            # Just dropping them all -> effectively blocking downloads.
            
            # Optionally, for debugging:
            # print(f"Dropped packet from {packet.src_addr}:{packet.src_port}")

if __name__ == "__main__":
    main()
