"""Quick test to validate PulseTray can start without errors."""
import sys
from pathlib import Path

# Add PulseTray to path
pulsetray_path = Path(__file__).parent / "PulseTray"
sys.path.insert(0, str(pulsetray_path))

def test_imports():
    """Test that all modules can be imported."""
    try:
        print("Testing imports...")
        
        from config import Config
        print("✓ config module")
        
        from metrics import MetricsCollector, MetricSnapshot
        print("✓ metrics module")
        
        from state import MetricsStore
        print("✓ state module")
        
        from alerts import AlertManager, Alert
        print("✓ alerts module")
        
        print("\n✓ All core modules imported successfully!")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_metrics():
    """Test metrics collection."""
    try:
        print("\nTesting metrics collection...")
        from metrics import MetricsCollector
        
        collector = MetricsCollector()
        snapshot = collector.collect()
        
        print(f"✓ Collected snapshot: {snapshot}")
        print(f"  CPU: {snapshot.cpu_percent:.1f}%")
        print(f"  Memory: {snapshot.mem_percent:.1f}%")
        print(f"  Disk: {snapshot.disk_percent:.1f}%")
        return True
    except Exception as e:
        print(f"✗ Metrics test failed: {e}")
        return False


def test_config():
    """Test configuration system."""
    try:
        print("\nTesting configuration...")
        from config import Config
        
        config = Config()
        
        print(f"✓ Config loaded")
        print(f"  Poll interval: {config.get('poll_interval')}s")
        print(f"  CPU alert: {config.get('cpu_alert')}%")
        print(f"  Memory alert: {config.get('memory_alert')}%")
        print(f"  Disk alert: {config.get('disk_alert')}%")
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False


if __name__ == "__main__":
    results = [
        test_imports(),
        test_metrics(),
        test_config(),
    ]
    
    if all(results):
        print("\n" + "="*50)
        print("All tests passed! PulseTray is ready to run.")
        print("="*50)
        print("\nTo start the app, run:")
        print("  python PulseTray/main.py")
    else:
        print("\n" + "="*50)
        print("Some tests failed. Please check the errors above.")
        print("="*50)
        sys.exit(1)
