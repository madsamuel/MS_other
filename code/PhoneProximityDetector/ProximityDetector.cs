using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace PhoneProximityDetector
{
    public class ProximityDetector
    {
        private readonly BluetoothDetector _bluetoothDetector;
        private readonly WiFiDetector _wifiDetector;
        private readonly Dictionary<string, DetectedDevice> _detectedDevices;
        private bool _isRunning;

        public event EventHandler<DetectedDevice>? OnDeviceDetected;
        public event EventHandler<DetectedDevice>? OnDeviceLost;
        public event EventHandler<string>? OnError;

        public ProximityDetector()
        {
            _bluetoothDetector = new BluetoothDetector();
            _wifiDetector = new WiFiDetector();
            _detectedDevices = new Dictionary<string, DetectedDevice>();

            // Wire up events
            _bluetoothDetector.OnDeviceFound += HandleDeviceFound;
            _bluetoothDetector.OnDeviceUpdated += HandleDeviceUpdated;
            _bluetoothDetector.OnError += HandleError;

            _wifiDetector.OnDeviceFound += HandleDeviceFound;
            _wifiDetector.OnError += HandleError;
        }

        public async Task StartAsync()
        {
            if (_isRunning)
            {
                OnError?.Invoke(this, "Detection is already running");
                return;
            }

            _isRunning = true;

            try
            {
                await _bluetoothDetector.StartAsync();
                await _wifiDetector.StartAsync();
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"Failed to start detection: {ex.Message}");
                _isRunning = false;
            }
        }

        public async Task StopAsync()
        {
            if (!_isRunning)
                return;

            _isRunning = false;

            await _bluetoothDetector.StopAsync();
            await _wifiDetector.StopAsync();

            _detectedDevices.Clear();
        }

        public async Task ScanNowAsync()
        {
            if (!_isRunning)
            {
                OnError?.Invoke(this, "Detection is not running");
                return;
            }

            await _bluetoothDetector.ScanAsync();
            await _wifiDetector.ScanAsync();
        }

        public void ListDetectedDevices()
        {
            Console.WriteLine("\n=== Currently Detected Devices ===");
            
            if (_detectedDevices.Count == 0)
            {
                Console.WriteLine("No devices detected.");
                return;
            }

            foreach (var device in _detectedDevices.Values.OrderBy(d => d.Name))
            {
                Console.WriteLine($"  {device}");
            }
            Console.WriteLine($"Total: {_detectedDevices.Count} device(s)\n");
        }

        private void HandleDeviceFound(object? sender, DetectedDevice device)
        {
            lock (_detectedDevices)
            {
                if (!_detectedDevices.ContainsKey(device.Id))
                {
                    _detectedDevices[device.Id] = device;
                    OnDeviceDetected?.Invoke(this, device);
                }
            }
        }

        private void HandleDeviceUpdated(object? sender, DetectedDevice device)
        {
            lock (_detectedDevices)
            {
                if (_detectedDevices.ContainsKey(device.Id))
                {
                    _detectedDevices[device.Id] = device;
                }
            }
        }

        private void HandleError(object? sender, string error)
        {
            OnError?.Invoke(this, error);
        }
    }
}
