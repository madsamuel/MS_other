This is a proof-of-concept throttling solution on Windows that requires admin privilates.  It uses WinDivert, a kernel driver with Python wrappers, for network packet shaping. This approach hooks into the Windows network stack at a low level, allowing you to capture all inbound/outbound packets, queue them, and release them at a controlled rate. It’s essentially building a small packet shaper in Python.

Prerequisites: pip install pydivert

How to test: Open a web browser (Chrome, Edge, Firefox, etc.) and try downloading a file over HTTP or HTTPS or simply load a news website with lots of images.


throttle_rdp_tcp_udp.py
    To test establish and RDP connection to a VM
    Open a browser and go to https://www.youtube.com/watch?v=ubFq-wV3Eic&ab_channel=ultrarelaxation
    Start the app

To confirm RDP
    netstat -ano | findstr 3389