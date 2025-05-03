import psutil

# Get a list of all open connections
connections = psutil.net_connections()

# Collect open ports, associated processes, and remote addresses
open_ports = []
for conn in connections:
    if conn.status == 'LISTEN' or conn.status == 'ESTABLISHED':
        pid = conn.pid
        local_port = conn.laddr.port
        remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
        process_name = psutil.Process(pid).name() if pid else 'Unknown'
        open_ports.append((local_port, process_name, pid, remote_address))

# Print open ports
print(f"{'Port':<10}{'Process Name':<30}{'PID':<10}{'Remote Address':<30}")
print('-' * 80)
for port, process_name, pid, remote_address in sorted(open_ports):
    print(f"{port:<10}{process_name:<30}{pid:<10}{remote_address:<30}")
