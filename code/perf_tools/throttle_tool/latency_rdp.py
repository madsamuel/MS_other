import time
import heapq
import threading
import pydivert

# ---------------------------------------
# Configure artificial latency (in ms)
# ---------------------------------------
LATENCY_MS = 50  # e.g. 200 ms

# Filter for both TCP and UDP traffic on port 3389 (RDP), inbound and outbound
FILTER = (
    "ip and (tcp or udp) and ("
    "  (tcp.SrcPort == 3389 or tcp.DstPort == 3389) or "
    "  (udp.SrcPort == 3389 or udp.DstPort == 3389)"
    ")"
)

def injector_thread(divert_handle, packet_queue):
    """
    Continuously checks the packet_queue for packets whose release_time <= now.
    If a packet is ready, it is popped from the heap and re-injected.
    Otherwise, we sleep briefly and check again.
    """
    while True:
        try:
            if packet_queue:
                # Peek at the earliest packet
                release_time, packet = packet_queue[0]  # don't pop yet

                now = time.time()
                if now >= release_time:
                    # It's time to re-inject this packet
                    heapq.heappop(packet_queue)  # remove from the queue
                    divert_handle.send(packet)
                else:
                    # Not ready yet, sleep until the release time or a short fraction
                    time.sleep(min(release_time - now, 0.01))
            else:
                # No packets in queue, sleep briefly
                time.sleep(0.01)
        except Exception as e:
            print(f"[!] Injector thread error: {e}")
            time.sleep(0.1)

def main():
    print(f"Applying {LATENCY_MS} ms latency to RDP packets (TCP/UDP) on port 3389.\n")
    print(f"Filter: {FILTER}")
    print("Press Ctrl+C to stop.\n")

    # Open WinDivert with our filter
    with pydivert.WinDivert(FILTER, priority=10) as w:
        # This queue holds (release_time, packet) tuples.
        packet_queue = []
        heapq.heapify(packet_queue)

        # Start the injector in a separate thread
        t = threading.Thread(target=injector_thread, args=(w, packet_queue), daemon=True)
        t.start()

        # Main loop: capture each packet, schedule it for future injection
        while True:
            packet = w.recv()
            capture_time = time.time()
            # We'll release (inject) the packet after LATENCY_MS.
            release_time = capture_time + (LATENCY_MS / 1000.0)
            heapq.heappush(packet_queue, (release_time, packet))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting. WinDivert handle closed. RDP latency injection stopped.")
