| Test Case     | Command                                                  | Expected Behavior                                                                              |
| :------------ | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------- |
| Default       | `python drop_packets_rdp.py`                             | Intercepts packets on port 3389, drops ~2% of them.                                           |
| Custom Drop % | `python drop_packets_rdp.py --drop 50`                   | Intercepts packets on port 3389, drops ~50% of them.                                          |
| Custom Port   | `python drop_packets_rdp.py --port 8080`                 | Intercepts packets on port 8080, drops ~2% (default) of them.                                 |
| Both Custom   | `python drop_packets_rdp.py --drop 25 --port 8080`       | Intercepts packets on port 8080, drops ~25% of them.                                          |
| Verbose Mode  | `python drop_packets_rdp.py --verbose`                   | Logs each dropped packet's details (source, destination, length).                             |
| All Options   | `python drop_packets_rdp.py --drop 75 --port 12345 --verbose` | Logs details for each dropped packet, drops ~75% of packets on port 12345.                  |
| Invalid Drop  | `python drop_packets_rdp.py --drop abc`                  | Program raises a validation error for invalid input (non-numeric).                           |
| Invalid Port  | `python drop_packets_rdp.py --port xyz`                  | Program raises a validation error for invalid input (non-numeric).                           |
| Help          | `python drop_packets_rdp.py --help`                      | Displays usage instructions for all available options.                                        |
