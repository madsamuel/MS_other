#!/usr/bin/env python3
"""Installation and setup helper for PulseTray."""
import subprocess
import sys
from pathlib import Path


def install_dependencies():
    """Install required packages."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    print("Installing PulseTray dependencies...")
    print("This may take a minute...\n")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("\n✓ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Installation failed: {e}")
        return False


def run_tests():
    """Run setup tests."""
    print("\nRunning setup tests...")
    test_file = Path(__file__).parent / "test_setup.py"
    
    try:
        subprocess.check_call([sys.executable, str(test_file)])
        return True
    except subprocess.CalledProcessError:
        return False


def start_app():
    """Start the main application."""
    main_file = Path(__file__).parent / "main.py"
    
    print("\nStarting PulseTray...\n")
    try:
        subprocess.call([sys.executable, str(main_file)])
    except KeyboardInterrupt:
        print("\n\nPulseTray stopped.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install-only":
        if install_dependencies():
            print("\nYou can now run: python main.py")
    else:
        # Full setup and run
        if install_dependencies() and run_tests():
            start_app()
        else:
            print("\nSetup failed. Please check the errors above.")
            sys.exit(1)
