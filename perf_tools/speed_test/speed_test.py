import speedtest

def run_speed_test():
    # Create a Speedtest object
    st = speedtest.Speedtest()
    
    # Get list of servers
    st.get_servers()
    
    # Select the best server based on latency
    best = st.get_best_server()
    print(f"Connected to {best['host']} located in {best['name']}, {best['country']}")

    # Measure download speed
    download_speed = st.download()
    # Measure upload speed
    upload_speed = st.upload()
    # Ping (latency)
    ping_result = st.results.ping

    # Print results in Mbps
    print(f"Ping: {ping_result:.2f} ms")
    print(f"Download speed: {download_speed / 1024 / 1024:.2f} Mbps")
    print(f"Upload speed:   {upload_speed / 1024 / 1024:.2f} Mbps")

if __name__ == "__main__":
    run_speed_test()
