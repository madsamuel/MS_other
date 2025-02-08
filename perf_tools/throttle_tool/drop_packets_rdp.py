import random
import pydivert

#---------------------------------------
# Adjust drop percentage here (0-100)
#---------------------------------------
DROP_PERCENTAGE = 2  # e.g., 50 means ~50% of packets are dropped

# Filter to capture both TCP and UDP traffic on port 3389 (RDP).
FILTER = (
    "ip and (tcp or udp) and ("
    "  (tcp.SrcPort == 3389 or tcp.DstPort == 3389) or "
    "  (udp.SrcPort == 3389 or udp.DstPort == 3389)"
    ")"
)

def main():
    """
    Randomly drops a percentage of all RDP packets on port 3389, covering both TCP and UDP.
    """

    print(f"Starting WinDivert with filter: {FILTER}")
    print(f"Randomly dropping ~{DROP_PERCENTAGE}% of RDP packets on port 3389.")
    print("Press Ctrl+C to stop.\n")

    with pydivert.WinDivert(FILTER, priority=10) as w:
        while True:
            packet = w.recv()
            # Generate a random float in [0.0, 1.0). If it's < (DROP_PERCENTAGE / 100), we drop.
            if random.random() < (DROP_PERCENTAGE / 100.0):
                # Drop the packet (do not re-inject).
                # If you want debug output, uncomment below:
                # print(f"Dropped packet: {packet.src_addr}:{packet.src_port} -> "
                #       f"{packet.dst_addr}:{packet.dst_port} (len={len(packet.raw)})")
                pass
            else:
                # Otherwise, allow the packet by re-injecting it.
                w.send(packet)

if __name__ == "__main__":
    main()
