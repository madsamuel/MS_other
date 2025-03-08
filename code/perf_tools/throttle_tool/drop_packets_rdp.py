import random
import pydivert
import argparse
import signal
import sys

# Constants
DEFAULT_DROP_PERCENTAGE = 2
DEFAULT_PORT = 3389

def create_filter(port):
    return (
        f"ip and (tcp or udp) and ("
        f"  (tcp.SrcPort == {port} or tcp.DstPort == {port}) or "
        f"  (udp.SrcPort == {port} or udp.DstPort == {port})"
        f")"
    )

def signal_handler(sig, frame):
    print("\nStopping packet interception. Exiting...")
    sys.exit(0)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Randomly drop RDP packets.")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to intercept (default: {DEFAULT_PORT})")
    parser.add_argument("-d", "--drop", type=float, default=DEFAULT_DROP_PERCENTAGE,
                        help=f"Drop percentage (0-100, default: {DEFAULT_DROP_PERCENTAGE})")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    return parser.parse_args()

def main():
    args = parse_arguments()
    filter_string = create_filter(args.port)

    print(f"Starting WinDivert with filter: {filter_string}")
    print(f"Randomly dropping ~{args.drop}% of packets on port {args.port}.")
    print("Press Ctrl+C to stop.\n")

    signal.signal(signal.SIGINT, signal_handler)

    try:
        with pydivert.WinDivert(filter_string, priority=10) as w:
            while True:
                packet = w.recv()
                if random.random() < (args.drop / 100.0):
                    if args.verbose:
                        print(f"Dropped packet: {packet.src_addr}:{packet.src_port} -> "
                              f"{packet.dst_addr}:{packet.dst_port} (len={len(packet.raw)})")
                else:
                    w.send(packet)
    except pydivert.WinDivertException as e:
        print(f"Error: {e}")
        print("Make sure you're running this script with administrator privileges.")
        sys.exit(1)

if __name__ == "__main__":
    main()
