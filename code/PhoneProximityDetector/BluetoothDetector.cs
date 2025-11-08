using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.Advertisement;

namespace PhoneProximityDetector
{
    public class BluetoothDetector
    {
        private BluetoothLEAdvertisementWatcher? _watcher;
        private bool _isScanning;
        private readonly Dictionary<string, DetectedDevice> _knownDevices;
        private readonly Dictionary<ulong, DateTime> _lastSeenTimes;

        public event EventHandler<DetectedDevice>? OnDeviceFound;
        public event EventHandler<DetectedDevice>? OnDeviceUpdated;
        public event EventHandler<string>? OnError;

        public BluetoothDetector()
        {
            _knownDevices = new Dictionary<string, DetectedDevice>();
            _lastSeenTimes = new Dictionary<ulong, DateTime>();
        }

        public async Task StartAsync()
        {
            if (_isScanning)
                return;

            try
            {
                _isScanning = true;

                // Create Bluetooth LE Advertisement Watcher
                _watcher = new BluetoothLEAdvertisementWatcher
                {
                    ScanningMode = BluetoothLEScanningMode.Active // Active scanning gets more device info
                };

                // Register event handlers
                _watcher.Received += OnAdvertisementReceived;
                _watcher.Stopped += OnWatcherStopped;

                // Start watching for advertisements
                _watcher.Start();

                Console.WriteLine("[Bluetooth] Started passive BLE scanning...");
                await Task.CompletedTask;
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"Bluetooth initialization error: {ex.Message}");
                _isScanning = false;
            }
        }

        public async Task StopAsync()
        {
            if (!_isScanning)
                return;

            _isScanning = false;

            if (_watcher != null)
            {
                _watcher.Received -= OnAdvertisementReceived;
                _watcher.Stopped -= OnWatcherStopped;
                _watcher.Stop();
                _watcher = null;
            }

            _knownDevices.Clear();
            _lastSeenTimes.Clear();
            
            await Task.Delay(100);
        }

        public async Task ScanAsync()
        {
            // With Advertisement Watcher, scanning is continuous
            // This method can be used to force refresh device names
            Console.WriteLine("[Bluetooth] Scan request - watcher is already running continuously");
            await Task.CompletedTask;
        }

        private void OnWatcherStopped(BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementWatcherStoppedEventArgs args)
        {
            if (args.Error != BluetoothError.Success)
            {
                OnError?.Invoke(this, $"Bluetooth watcher stopped with error: {args.Error}");
            }
        }

        private async void OnAdvertisementReceived(BluetoothLEAdvertisementWatcher sender, BluetoothLEAdvertisementReceivedEventArgs args)
        {
            try
            {
                var bluetoothAddress = args.BluetoothAddress;
                var rssi = args.RawSignalStrengthInDBm;
                
                // Update last seen time
                lock (_lastSeenTimes)
                {
                    _lastSeenTimes[bluetoothAddress] = DateTime.Now;
                }

                // Try to get device name and additional info
                await ProcessAdvertisement(bluetoothAddress, rssi, args.Advertisement);
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"Error processing Bluetooth advertisement: {ex.Message}");
            }
        }

        private async Task ProcessAdvertisement(ulong bluetoothAddress, short rssi, BluetoothLEAdvertisement advertisement)
        {
            try
            {
                var macAddress = FormatBluetoothAddress(bluetoothAddress);
                var deviceId = $"BT_{macAddress}";
                
                // Get local name from advertisement
                string name = advertisement.LocalName;
                if (string.IsNullOrWhiteSpace(name))
                {
                    name = "Unknown BT Device";
                    
                    // Try to get device name from BluetoothLEDevice (requires pairing/connection)
                    try
                    {
                        var device = await BluetoothLEDevice.FromBluetoothAddressAsync(bluetoothAddress);
                        if (device != null && !string.IsNullOrWhiteSpace(device.Name))
                        {
                            name = device.Name;
                        }
                        device?.Dispose();
                    }
                    catch
                    {
                        // Failed to get device name, use MAC address
                        name = $"BT Device {macAddress.Substring(macAddress.Length - 8)}";
                    }
                }

                // Detect if it's likely a phone
                bool isLikelyPhone = IsLikelyPhone(name, advertisement);
                
                lock (_knownDevices)
                {
                    if (_knownDevices.TryGetValue(deviceId, out var existingDevice))
                    {
                        // Update existing device
                        existingDevice.LastSeen = DateTime.Now;
                        existingDevice.SignalStrength = rssi;
                        if (!string.IsNullOrWhiteSpace(advertisement.LocalName) && existingDevice.Name.StartsWith("BT Device"))
                        {
                            existingDevice.Name = advertisement.LocalName;
                        }
                        OnDeviceUpdated?.Invoke(this, existingDevice);
                    }
                    else if (isLikelyPhone || rssi > -80) // Only report phones or strong signals
                    {
                        // New device found
                        var detectedDevice = new DetectedDevice
                        {
                            Id = deviceId,
                            Name = name,
                            Type = DeviceType.Bluetooth,
                            SignalStrength = rssi,
                            MacAddress = macAddress,
                            FirstSeen = DateTime.Now,
                            LastSeen = DateTime.Now,
                            AdditionalInfo = new Dictionary<string, string>
                            {
                                ["BluetoothAddress"] = macAddress,
                                ["RSSI"] = $"{rssi} dBm",
                                ["IsLikelyPhone"] = isLikelyPhone.ToString(),
                                ["ServiceUUIDs"] = string.Join(", ", advertisement.ServiceUuids.Select(u => u.ToString().Substring(0, 8)))
                            }
                        };

                        _knownDevices[deviceId] = detectedDevice;
                        OnDeviceFound?.Invoke(this, detectedDevice);
                    }
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"Error processing Bluetooth advertisement: {ex.Message}");
            }
        }

        private bool IsLikelyPhone(string name, BluetoothLEAdvertisement advertisement)
        {
            var lowerName = name.ToLower();
            
            // Check device name patterns
            if (lowerName.Contains("phone") || lowerName.Contains("iphone") || 
                lowerName.Contains("android") || lowerName.Contains("samsung") ||
                lowerName.Contains("pixel") || lowerName.Contains("oneplus") ||
                lowerName.Contains("xiaomi") || lowerName.Contains("huawei") ||
                lowerName.Contains("oppo") || lowerName.Contains("vivo") ||
                lowerName.Contains("motorola") || lowerName.Contains("nokia"))
            {
                return true;
            }

            // Check for common phone service UUIDs
            // Phone services often include Battery Service, Device Information, etc.
            foreach (var uuid in advertisement.ServiceUuids)
            {
                var uuidStr = uuid.ToString().ToLower();
                // Common phone service UUIDs
                if (uuidStr.StartsWith("0000180f") || // Battery Service
                    uuidStr.StartsWith("0000180a") || // Device Information Service
                    uuidStr.StartsWith("0000180d"))   // Heart Rate (fitness trackers/phones)
                {
                    return true;
                }
            }

            return false;
        }

        private string FormatBluetoothAddress(ulong bluetoothAddress)
        {
            var bytes = BitConverter.GetBytes(bluetoothAddress);
            Array.Reverse(bytes);
            return string.Join(":", bytes.Skip(2).Select(b => b.ToString("X2")));
        }
    }
}
