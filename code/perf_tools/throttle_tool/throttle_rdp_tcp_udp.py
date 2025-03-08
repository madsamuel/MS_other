import time
import pydivert

#---------------------------------------
# Configure the throttling parameters
#---------------------------------------
MAX_BYTES_PER_SECOND = 50 * 1024  # 500 KB/s total throughput
PRIORITY = 10  # WinDivert priority

# Filter to capture both TCP and UDP traffic on port 3389 (RDP)
# This includes inbound and outbound.
FILTER = (
    "ip and (tcp or udp) and ("
    "  (tcp.SrcPort == 3389 or tcp.DstPort == 3389) or "
    "  (udp.SrcPort == 3389 or udp.DstPort == 3389)"
    ")"
)

def main():
    """
    Throttles all RDP traffic on port 3389, covering both TCP and UDP.
    """

    print(f"Starting WinDivert with filter={FILTER}")
    print(f"Throttling RDP (TCP/UDP) to {MAX_BYTES_PER_SECOND} bytes per second.")
    print("Press Ctrl+C to stop.\n")

    # Open the WinDivert handle with our filter
    with pydivert.WinDivert(FILTER, priority=PRIORITY) as w:
        bytes_this_second = 0
        second_start = time.time()

        while True:
            # Intercept a packet
            packet = w.recv()
            packet_len = len(packet.raw)

            now = time.time()
            elapsed = now - second_start

            # Reset the token bucket each second
            if elapsed >= 1.0:
                bytes_this_second = 0
                second_start = now

            # If adding this packet exceeds our limit, sleep until the next second
            if bytes_this_second + packet_len > MAX_BYTES_PER_SECOND:
                sleep_time = 1.0 - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # After sleeping, reset the bucket for the new second
                second_start = time.time()
                bytes_this_second = 0

            # Re-inject (send) the packet at our throttled pace
            w.send(packet)
            bytes_this_second += packet_len

if __name__ == "__main__":
    main()
