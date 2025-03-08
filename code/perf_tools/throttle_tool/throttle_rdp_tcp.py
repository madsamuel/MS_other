import time
import pydivert

#---------------------------------------
# Configure the throttling parameters
#---------------------------------------
MAX_BYTES_PER_SECOND = 5 * 1024  # e.g. 5 KB/s total throughput
FILTER = "tcp and (tcp.SrcPort == 3389 or tcp.DstPort == 3389)"
PRIORITY = 10  # WinDivert priority

def main():
    """
    Throttles all traffic (inbound + outbound) on TCP port 3389,
    i.e., typical RDP traffic.
    """

    print(f"Starting WinDivert with filter={FILTER}")
    print(f"Throttling RDP to {MAX_BYTES_PER_SECOND} bytes per second.")
    print("Press Ctrl+C to stop.\n")

    # Open the WinDivert handle with our filter
    with pydivert.WinDivert(FILTER, priority=PRIORITY) as w:
        bytes_this_second = 0
        second_start = time.time()

        while True:
            packet = w.recv()
            packet_len = len(packet.raw)

            now = time.time()
            elapsed = now - second_start

            # If a second has passed, reset the counter
            if elapsed >= 1.0:
                bytes_this_second = 0
                second_start = now

            # If adding this packet would exceed our limit, wait
            if bytes_this_second + packet_len > MAX_BYTES_PER_SECOND:
                sleep_time = 1.0 - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                # Start a new second after sleeping
                second_start = time.time()
                bytes_this_second = 0

            # Re-inject (send) the packet after the delay
            w.send(packet)
            bytes_this_second += packet_len

if __name__ == "__main__":
    main()
