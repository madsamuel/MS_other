using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ManagedNativeWifi;

namespace PhoneProximityDetector
{
    public class WiFiDetector
    {
        private CancellationTokenSource? _cancellationTokenSource;
        private bool _isScanning;
        private readonly Dictionary<string, DetectedDevice> _knownDevices;

        public event EventHandler<DetectedDevice>? OnDeviceFound;
        public event EventHandler<string>? OnError;

        public WiFiDetector()
        {
            _knownDevices = new Dictionary<string, DetectedDevice>();
        }

        public async Task StartAsync()
        {
            if (_isScanning)
                return;

            _cancellationTokenSource = new CancellationTokenSource();
            _isScanning = true;

            try
            {
                // Check if WiFi interfaces are available
                var interfaces = NativeWifi.EnumerateInterfaces();
                if (!interfaces.Any())
                {
                    OnError?.Invoke(this, "No WiFi interfaces found on this system");
                    _isScanning = false;
                    return;
                }

                // Start continuous scanning in background
                _ = Task.Run(() => ContinuousScanAsync(_cancellationTokenSource.Token));
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"WiFi initialization error: {ex.Message}");
                _isScanning = false;
            }
        }

        public async Task StopAsync()
        {
            if (!_isScanning)
                return;

            _isScanning = false;
            _cancellationTokenSource?.Cancel();
            _knownDevices.Clear();
            
            await Task.Delay(100);
        }

        public async Task ScanAsync()
        {
            try
            {
                await PerformScanAsync();
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"WiFi scan error: {ex.Message}");
            }
        }

        private async Task ContinuousScanAsync(CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    await PerformScanAsync();
                    await Task.Delay(8000, cancellationToken); // Scan every 8 seconds
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    OnError?.Invoke(this, $"WiFi continuous scan error: {ex.Message}");
                    await Task.Delay(15000, cancellationToken); // Wait longer on error
                }
            }
        }

        private async Task PerformScanAsync()
        {
            try
            {
                // Request a scan (this triggers the OS to scan for networks on all interfaces)
                try
                {
                    await NativeWifi.ScanNetworksAsync(timeout: TimeSpan.FromSeconds(4));
                }
                catch
                {
                    // Scan may fail if already in progress or interfaces are busy
                }
                
                // Wait a bit for scan results
                await Task.Delay(1000);
                
                // Get BSS networks (includes BSSID/MAC address information)
                var networks = NativeWifi.EnumerateBssNetworks();
                
                foreach (var network in networks)
                {
                    ProcessNetwork(network);
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"WiFi scan execution error: {ex.Message}");
            }
        }

        private void ProcessNetwork(BssNetworkPack network)
        {
            try
            {
                // Use BSSID (MAC address of access point) as unique identifier
                var bssid = network.Bssid.ToString(); // BssNetworkPack uses Bssid property (PhysicalAddress type)
                var ssid = network.Ssid.ToString();
                var rssi = network.SignalStrength; // In version 2.2.0, it's called SignalStrength (renamed to Rssi in 3.0+)
                
                var deviceId = $"WiFi_{bssid}";
                
                lock (_knownDevices)
                {
                    if (!_knownDevices.ContainsKey(deviceId))
                    {
                        // Check if this might be a phone's hotspot
                        var isLikelyPhone = IsLikelyPhoneHotspot(ssid);
                        
                        var detectedDevice = new DetectedDevice
                        {
                            Id = deviceId,
                            Name = string.IsNullOrWhiteSpace(ssid) ? "Hidden Network" : ssid,
                            Type = DeviceType.WiFi,
                            SignalStrength = rssi,
                            MacAddress = bssid,
                            FirstSeen = DateTime.Now,
                            LastSeen = DateTime.Now,
                            AdditionalInfo = new Dictionary<string, string>
                            {
                                ["SSID"] = ssid,
                                ["BSSID"] = bssid,
                                ["RSSI"] = $"{rssi} dBm",
                                ["LinkQuality"] = network.LinkQuality.ToString(),
                                ["Frequency"] = $"{network.Frequency} kHz",
                                ["Channel"] = network.Channel.ToString(),
                                ["LikelyPhone"] = isLikelyPhone.ToString()
                            }
                        };

                        _knownDevices[deviceId] = detectedDevice;
                        
                        // Report if it's likely a phone hotspot OR has strong signal (close proximity)
                        // Strong signal (>-60 dBm) indicates device is very close, likely in same room
                        if (isLikelyPhone || rssi > -60)
                        {
                            OnDeviceFound?.Invoke(this, detectedDevice);
                        }
                    }
                    else
                    {
                        // Update last seen time
                        _knownDevices[deviceId].LastSeen = DateTime.Now;
                        _knownDevices[deviceId].SignalStrength = rssi;
                    }
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke(this, $"Error processing WiFi network: {ex.Message}");
            }
        }

        private bool IsLikelyPhoneHotspot(string ssid)
        {
            if (string.IsNullOrWhiteSpace(ssid))
                return false;

            var lowerSsid = ssid.ToLower();
            
            // Common patterns for phone hotspots
            return lowerSsid.Contains("iphone") ||
                   lowerSsid.Contains("android") ||
                   lowerSsid.Contains("samsung") ||
                   lowerSsid.Contains("pixel") ||
                   lowerSsid.Contains("oneplus") ||
                   lowerSsid.Contains("xiaomi") ||
                   lowerSsid.Contains("huawei") ||
                   lowerSsid.Contains("phone") ||
                   lowerSsid.Contains("mobile") ||
                   lowerSsid.Contains("hotspot") ||
                   lowerSsid.Contains("'s phone") ||
                   lowerSsid.Contains("'s iphone");
        }
    }
}
