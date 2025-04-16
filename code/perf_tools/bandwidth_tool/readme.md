Command-line argument parsing - Allows for customizable monitoring with options like interval, interface selection, threshold warnings, and CSV logging.
Logging to CSV - Enables historical tracking of network usage.
Interface selection - Monitors a specific network interface if provided.
Threshold alerts - Alerts the user if bandwidth usage exceeds a specified limit.
Error handling - Gracefully handles cases where an invalid network interface is provided.
Code readability - Improved through docstrings and structured function definitions.
Graceful exit - Proper termination when the user interrupts with Ctrl+C.

| Command | Explanation |
|---------|-------------|
| `python speed_test_tool.py` | Runs the script with the default interval of `1.0` second, monitoring all network interfaces. No CSV logging or threshold alerts; output is displayed on the console. |
| `python speed_test_tool.py -i 2.0 -n eth0` | Sets the monitoring interval to `2.0` seconds and monitors the `eth0` network interface only. Useful for focusing on a particular network adapter. |
| `python speed_test_tool.py -t 50` | Runs with the default `1.0` second interval, monitoring all interfaces. If upload or download bandwidth exceeds `50 MB/s`, a warning will be displayed. Useful for detecting heavy network usage. |
| `python speed_test_tool.py -o bandwidth_log.csv` | Monitors all interfaces at the default `1.0` second interval and logs the timestamp, upload speed, and download speed to `bandwidth_log.csv`. Useful for long-term monitoring and analysis. |
| `python speed_test_tool.py -i 5.0 -n wlan0 -t 100 -o network_report.csv` | Monitors the `wlan0` interface every `5.0` seconds, logs data to `network_report.csv`, and displays a warning if bandwidth usage exceeds `100 MB/s`. Suitable for detailed tracking of Wi-Fi bandwidth usage. |

