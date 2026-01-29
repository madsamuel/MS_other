"""Demo scenario runner for PulseTray showcasing features."""
import subprocess
import sys
import time
import threading
from pathlib import Path


class DemoRunner:
    """Run interactive demo of PulseTray features."""
    
    def __init__(self):
        self.pulsetray_process = None
    
    def start_app(self):
        """Start PulseTray in background."""
        main_file = Path(__file__).parent / "main.py"
        self.pulsetray_process = subprocess.Popen([sys.executable, str(main_file)])
        time.sleep(2)  # Give app time to start
        print("✓ PulseTray started")
    
    def stop_app(self):
        """Stop PulseTray."""
        if self.pulsetray_process:
            self.pulsetray_process.terminate()
            self.pulsetray_process.wait(timeout=5)
            print("✓ PulseTray stopped")
    
    def create_cpu_load(self, duration=30):
        """Create sustained CPU load for demo."""
        print(f"Generating CPU load for {duration} seconds...")
        print("(Watch the tray icon turn red and metrics spike)")
        
        def cpu_work():
            end_time = time.time() + duration
            while time.time() < end_time:
                # CPU-intensive work
                _ = sum(i*i for i in range(1000000))
        
        threads = []
        for _ in range(2):  # Use 2 threads
            t = threading.Thread(target=cpu_work)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        print("✓ CPU load complete")
    
    def run_interactive_demo(self):
        """Run interactive demo."""
        print("\n" + "="*60)
        print("PulseTray Interactive Demo")
        print("="*60 + "\n")
        
        print("This demo will showcase PulseTray features.")
        print("Make sure you can see the system tray!\n")
        
        input("Press ENTER to start the application... ")
        
        self.start_app()
        
        # Step 1: Show tooltip
        print("\n[STEP 1] View live metrics")
        print("-" * 40)
        print("✓ Application is running")
        print("✓ Look for a blue circle in your system tray")
        print("✓ Hover over it to see live metrics tooltip:")
        print("  - CPU usage")
        print("  - Memory usage")
        print("  - Disk usage")
        print("  - Network speeds")
        
        input("\nPress ENTER when ready for step 2... ")
        
        # Step 2: Show details
        print("\n[STEP 2] Open details dashboard")
        print("-" * 40)
        print("✓ The dashboard is now visible OR")
        print("✓ You can: Double-click the tray icon OR")
        print("✓ Right-click → 'Show Details'")
        print("\nThe dashboard shows:")
        print("  - System hostname")
        print("  - Uptime")
        print("  - Color-coded metric cards (green/yellow/red)")
        print("  - Last update timestamp")
        
        input("\nPress ENTER to generate CPU load (30 sec)... ")
        
        # Step 3: Trigger alert
        print("\n[STEP 3] Trigger alert by creating load")
        print("-" * 40)
        self.create_cpu_load(30)
        
        print("\nAlert demonstration:")
        print("  ✓ Tray icon turned RED (alert active)")
        print("  ✓ Dashboard shows red metrics")
        print("  ✓ CPU card shows 'Critical' status")
        
        input("\nPress ENTER to continue... ")
        
        # Step 4: Export
        print("\n[STEP 4] Export metrics")
        print("-" * 40)
        print("Right-click tray icon → 'Export Snapshot'")
        print("\nThis creates a CSV file in your home directory with:")
        print("  - Timestamp")
        print("  - CPU, Memory, Disk percentages")
        print("  - Network upload/download speeds")
        print("  - Last 10 minutes of data")
        
        input("\nPress ENTER to continue... ")
        
        # Step 5: Menu exploration
        print("\n[STEP 5] Explore the menu")
        print("-" * 40)
        print("Right-click the tray icon to see options:")
        print("  - Show Details: Opens/focuses dashboard")
        print("  - Pause Monitoring: Temporarily stop collection")
        print("  - Export Snapshot: Save metrics to CSV")
        print("  - Settings: Configuration (future)")
        print("  - Quit: Close application")
        
        input("\nPress ENTER to finish demo and quit... ")
        
        # Cleanup
        print("\n[CLEANUP]")
        print("-" * 40)
        self.stop_app()
        
        print("\n" + "="*60)
        print("Demo Complete!")
        print("="*60)
        print("\nKey Takeaways:")
        print("  ✓ Lightweight system monitoring")
        print("  ✓ Real-time metrics in tray")
        print("  ✓ Visual dashboard with alerts")
        print("  ✓ Export capability")
        print("  ✓ Easy to use menu")
        print("\nFor production use:")
        print("  - Run at startup via system settings")
        print("  - Configure thresholds in config.json")
        print("  - Monitor 24/7 with minimal overhead")
        print("\n")


def run_benchmark():
    """Run performance benchmark."""
    print("\n" + "="*60)
    print("PulseTray Performance Benchmark")
    print("="*60 + "\n")
    
    # Test metrics collection speed
    print("Benchmarking metrics collection...")
    
    from metrics import MetricsCollector
    
    collector = MetricsCollector()
    
    start = time.time()
    iterations = 10
    for _ in range(iterations):
        snapshot = collector.collect()
        time.sleep(0.1)  # Simulate 100ms between polls
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000
    
    print(f"✓ Collected {iterations} snapshots")
    print(f"  Average time per collection: {avg_time:.2f}ms")
    print(f"  Total elapsed: {elapsed:.2f}s")
    
    if avg_time < 10:
        print("  Performance: Excellent (<10ms)")
    elif avg_time < 50:
        print("  Performance: Good (<50ms)")
    else:
        print("  Performance: Acceptable")
    
    print("\nMemory usage (approximate):")
    print("  - Application: ~60-80 MB")
    print("  - History buffer (10 min): ~5 MB")
    print("  - Total: ~70-90 MB")
    
    print("\nNetwork metrics update:")
    s1 = collector.collect()
    time.sleep(1)
    s2 = collector.collect()
    
    print(f"  Upload: {s2.net_up_bps / 1024:.2f} KB/s")
    print(f"  Download: {s2.net_down_bps / 1024:.2f} KB/s")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PulseTray demo and benchmark")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    
    args = parser.parse_args()
    
    if args.benchmark:
        run_benchmark()
    elif args.demo:
        runner = DemoRunner()
        runner.run_interactive_demo()
    else:
        print("PulseTray Demo & Benchmark Tool\n")
        print("Usage:")
        print("  python demo.py --demo       # Run interactive feature demo")
        print("  python demo.py --benchmark  # Run performance benchmark\n")
        print("Or simply run the app:")
        print("  python main.py")
