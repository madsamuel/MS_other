import time
import pydivert

MAX_BYTES_PER_SECOND = 100 * 1024  # 100 KB/s
FILTER = "outbound and ip"        # For outbound IPv4

def main():
    print(f"Starting WinDivert with filter={FILTER}, limit={MAX_BYTES_PER_SECOND} B/s")

    # Using 'with' automatically opens the handle
    with pydivert.WinDivert(FILTER, priority=10) as w:
        bytes_this_second = 0
        second_start = time.time()

        while True:
            packet = w.recv()
            packet_len = len(packet.raw)

            now = time.time()
            if now - second_start >= 1.0:
                bytes_this_second = 0
                second_start = now

            if bytes_this_second + packet_len > MAX_BYTES_PER_SECOND:
                sleep_time = 1.0 - (now - second_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                second_start = time.time()
                bytes_this_second = 0

            w.send(packet)
            bytes_this_second += packet_len

if __name__ == "__main__":
    main()
