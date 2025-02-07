import time
import pydivert

MAX_BYTES_PER_SECOND = 10 * 1024  # 100 KB/s
filter_str = "inbound and tcp and (tcp.SrcPort == 80 or tcp.SrcPort == 443)"

def main():
    with pydivert.WinDivert(filter_str) as w:
        bytes_this_second = 0
        second_start = time.time()

        while True:
            packet = w.recv()
            packet_len = len(packet.raw)

            now = time.time()
            elapsed = now - second_start

            # If a second has passed, reset the bucket
            if elapsed >= 1.0:
                bytes_this_second = 0
                second_start = now

            # If adding this packet would exceed the cap, wait
            if bytes_this_second + packet_len > MAX_BYTES_PER_SECOND:
                sleep_time = 1.0 - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                # Reset for the new second
                second_start = time.time()
                bytes_this_second = 0

            w.send(packet)
            bytes_this_second += packet_len

if __name__ == "__main__":
    main()
