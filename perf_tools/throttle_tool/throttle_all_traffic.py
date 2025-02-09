"""A simple script to throttle all machine traffic using a token-bucket approach with WinDivert.

This script intercepts packets using pydivert, and re-injects them at a limited
rate specified by MAX_BYTES_PER_SECOND. Note that this throttle is applied system-wide.
"""

import time

import pydivert

MAX_BYTES_PER_SECOND = 5 * 1024  # 500*1024 KB/s total throughput
PRIORITY = 10  # WinDivert priority
FILTER = "true"  # Use "true" to capture ALL packets; or "ip" for only IP packets (TCP, UDP, ICMP, etc.)

def main():
    """Throttle ALL traffic on this machine (system-wide) using a simple token-bucket approach."""
    print(f"Starting WinDivert with filter={FILTER}")
    print(f"Throttling ALL traffic to {MAX_BYTES_PER_SECOND} bytes per second.")
    print("Press Ctrl+C to stop.\n")

    with pydivert.WinDivert(FILTER, priority=PRIORITY) as w:
        bytes_this_second = 0
        second_start = time.time()

        while True:
            packet = w.recv()
            packet_length = len(packet.raw)

            now = time.time()
            elapsed = now - second_start

            # Reset the "bucket" each second
            if elapsed >= 1.0:
                bytes_this_second = 0
                second_start = now

            # If we exceed our rate limit, sleep until the next second
            if bytes_this_second + packet_length > MAX_BYTES_PER_SECOND:
                sleep_time = 1.0 - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)

                second_start = time.time()
                bytes_this_second = 0

            w.send(packet)
            bytes_this_second += packet_length

if __name__ == "__main__":
    main()
