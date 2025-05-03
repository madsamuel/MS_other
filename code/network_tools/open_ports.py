import psutil

# Get a list of all open connections
connections = psutil.net_connections()

# Collect open ports and associated processes
open_ports = []
for conn in connections:
    if conn.status == 'LISTEN':
        pid = conn.pid
        port = conn.laddr.port
        process_name = psutil.Process(pid).name() if pid else 'Unknown'
        open_ports.append((port, process_name, pid))

# Print open ports
print(f"{'Port':<10}{'Process Name':<30}{'PID':<10}")
print('-' * 50)
for port, process_name, pid in sorted(open_ports):
    print(f"{port:<10}{process_name:<30}{pid:<10}")
