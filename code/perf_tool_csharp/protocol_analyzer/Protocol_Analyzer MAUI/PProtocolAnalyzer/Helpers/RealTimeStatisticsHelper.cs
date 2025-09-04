using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.Versioning;

namespace PProtocolAnalyzer.Helpers
{
    public class RemoteFXNetworkStats
    {
    // New bandwidth breakdown (Kbps)
    public float TotalBandwidthKbps { get; set; }
    // Sent (output) Kbps (derived from Bytes Total - Bytes Received)
    public float SentBandwidthKbps { get; set; }
    public float InputBandwidthKbps { get; set; }
    // (Link capacity removed)
    public string SentBandwidthFormatted { get; set; } = "";
    public string TotalBandwidthFormatted { get; set; } = "";
    public string InputBandwidthFormatted { get; set; } = "";
    // Available bandwidth (Kbps) = capacity - observed total when capacity known
    public float AvailableBandwidthKbps { get; set; }
    public string AvailableBandwidthFormatted { get; set; } = "Unknown";
    // Per-adapter throughput info
    public AdapterStats[] Adapters { get; set; } = Array.Empty<AdapterStats>();
        public SessionStats[] Sessions { get; set; } = Array.Empty<SessionStats>();
        public bool IsAvailable { get; set; }
        public string ErrorMessage { get; set; } = "";
    }

    public class AdapterStats
    {
        public string Name { get; set; } = "";
        // Kbps
        public float Kbps { get; set; }
        public string Formatted { get; set; } = "";
    }

    public class SessionStats
    {
        public string InstanceName { get; set; } = "";
    // Per-session: only RTT is tracked now
    public float RttMs { get; set; }
    }

    public static class RealTimeStatisticsHelper
    {
    // Removed per-protocol counters (UDP/TCP) - we no longer pull per-protocol bandwidth values here
        private static PerformanceCounter[]? _rfxRttCounters;
    private static PerformanceCounter[]? _networkBytesTotalCounters;
    private static PerformanceCounter[]? _networkBytesReceivedCounters;
    private static PerformanceCounter[]? _networkCurrentBandwidthCounters;
        private static string[]? _instances;
        private static bool _countersInitialized = false;
        private static string? _initializationError;
    // If we can detect which local NIC serves the session, prefer its counters instead of summing all adapters
        private static int? _preferredAdapterIndex = null;

        /// <summary>
        /// Initializes RemoteFX performance counters
        /// </summary>
        [SupportedOSPlatform("windows")]
        public static void InitializeRemoteFXCounters()
        {
            if (_countersInitialized) return;

            try
            {
                // Guard: Windows only
                if (!OperatingSystem.IsWindows())
                {
                    _initializationError = "RemoteFX counters only available on Windows";
                    return;
                }

                const string cat = "RemoteFX Network";
                const string rttCn = "Current UDP RTT";

                var category = new PerformanceCounterCategory(cat);
                var missingCounters = new System.Collections.Generic.List<string>();
                
                if (!category.CounterExists(rttCn)) missingCounters.Add($"'{rttCn}' in {cat}");
                
                if (missingCounters.Count > 0)
                {
                    _initializationError = $"Missing counter(s): {string.Join(", ", missingCounters)}";
                    return;
                }

                // Instantiate counters
                _instances = category.GetInstanceNames();
                // Only initialize RTT counters for per-session latency
                _rfxRttCounters = _instances.Select(i => new PerformanceCounter(cat, rttCn, i, true)).ToArray();

                // Warm up counters for accurate readings
                // Warm up RTT counters
                foreach (var c in _rfxRttCounters) c.NextValue();

                // Initialize Network Interface "Bytes Total/sec" counters for all adapters
                try
                {
                    var netCategory = new PerformanceCounterCategory("Network Interface");
                    var netInstances = netCategory.GetInstanceNames()
                        .Where(n => !string.IsNullOrWhiteSpace(n) &&
                                    !n.Contains("Loopback", StringComparison.OrdinalIgnoreCase) &&
                                    !n.Contains("isatap", StringComparison.OrdinalIgnoreCase) &&
                                    !n.Contains("Teredo", StringComparison.OrdinalIgnoreCase))
                        .ToArray();

                    if (netInstances.Length > 0)
                    {
                        _networkBytesTotalCounters = netInstances.Select(i => new PerformanceCounter("Network Interface", "Bytes Total/sec", i, true)).ToArray();
                        _networkBytesReceivedCounters = netInstances.Select(i => new PerformanceCounter("Network Interface", "Bytes Received/sec", i, true)).ToArray();
                        // Try to read Current Bandwidth (reported link capacity in bits/sec) when available
                        try
                        {
                            _networkCurrentBandwidthCounters = netInstances.Select(i => new PerformanceCounter("Network Interface", "Current Bandwidth", i, true)).ToArray();
                            foreach (var c in _networkCurrentBandwidthCounters) c.NextValue();
                        }
                        catch (Exception ex2)
                        {
                            System.Diagnostics.Debug.WriteLine($"Info: Current Bandwidth counter not available for some adapters: {ex2.Message}");
                            _networkCurrentBandwidthCounters = null;
                        }
                        foreach (var c in _networkBytesTotalCounters) c.NextValue();
                        foreach (var c in _networkBytesReceivedCounters) c.NextValue();

                        // Try to detect the NIC used by the current session (client IP) and pick a preferred adapter instance if possible.
                        try
                        {
                            var clientIp = SessionInfoHelper.GetClientIpAddress();
                            if (clientIp != null && clientIp.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                            {
                                var clientBytes = clientIp.GetAddressBytes();
                                var nics = System.Net.NetworkInformation.NetworkInterface.GetAllNetworkInterfaces();
                                System.Net.NetworkInformation.NetworkInterface? matchNic = null;
                                foreach (var nic in nics)
                                {
                                    var props = nic.GetIPProperties();
                                    foreach (var ua in props.UnicastAddresses)
                                    {
                                        if (ua.Address.AddressFamily != System.Net.Sockets.AddressFamily.InterNetwork) continue;
                                        var addrBytes = ua.Address.GetAddressBytes();
                                        // heuristic: same /24 subnet (first 3 octets) - common case for LAN RDP sessions
                                        if (addrBytes.Length == 4 && clientBytes.Length == 4 &&
                                            addrBytes[0] == clientBytes[0] && addrBytes[1] == clientBytes[1] && addrBytes[2] == clientBytes[2])
                                        {
                                            matchNic = nic;
                                            break;
                                        }
                                    }
                                    if (matchNic != null) break;
                                }

                                if (matchNic != null)
                                {
                                    // Try to map NIC to performance counter instance name using description or name
                                    var desc = (matchNic.Description ?? string.Empty).ToLowerInvariant();
                                    var name = (matchNic.Name ?? string.Empty).ToLowerInvariant();
                                    for (int i = 0; i < netInstances.Length; i++)
                                    {
                                        var inst = netInstances[i].ToLowerInvariant();
                                        if (inst.Contains(desc) || inst.Contains(name))
                                        {
                                            _preferredAdapterIndex = i;
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Info: failed to detect preferred adapter: {ex.Message}");
                        }
                    }
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Warning: Failed to initialize Network Interface counters: {ex.Message}");
                }

                _countersInitialized = true;
            }
            catch (Exception ex)
            {
                _initializationError = $"Error initializing RemoteFX counters: {ex.Message}";
                System.Diagnostics.Debug.WriteLine(_initializationError);
            }
        }

        /// <summary>
        /// Gets current RemoteFX network statistics
        /// </summary>
        [SupportedOSPlatform("windows")]
        public static RemoteFXNetworkStats GetRemoteFXStats()
        {
            var stats = new RemoteFXNetworkStats();

            if (!_countersInitialized)
            {
                stats.ErrorMessage = _initializationError ?? "Counters not initialized";
                return stats;
            }

                if (_rfxRttCounters == null || _instances == null)
            {
                stats.ErrorMessage = "Performance counters not available";
                return stats;
            }

            try
            {
                // We no longer pull per-protocol (UDP/TCP) bandwidth values here. Rely on NIC-level counters for totals.

                // Compute per-adapter throughput and NIC total bandwidth (Bytes/sec -> bits/sec)
                float nicTotalBitsPerSec = 0f;
                var adapterList = new System.Collections.Generic.List<AdapterStats>();
                if (_networkBytesTotalCounters != null && _networkBytesTotalCounters.Length > 0)
                {
                    for (int a = 0; a < _networkBytesTotalCounters.Length; a++)
                    {
                        try
                        {
                            float bytesPerSec = _networkBytesTotalCounters[a].NextValue();
                            float bitsPerSec = bytesPerSec * 8f;
                            nicTotalBitsPerSec += bitsPerSec;
                            float kbps = bitsPerSec / 1000f;
                            adapterList.Add(new AdapterStats { Name = _networkBytesTotalCounters[a].InstanceName, Kbps = kbps, Formatted = $"{(kbps <= 999f ? ((int)Math.Round(kbps)).ToString() + " Kbps" : (kbps/1000f).ToString("F2") + " Mbps")}" });
                        }
                        catch (Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Warning: reading adapter counter failed: {ex.Message}");
                        }
                    }
                }

                // Compute input bits/sec from Bytes Received/sec counters
                float nicInputBitsPerSec = 0f;
                if (_networkBytesReceivedCounters != null && _networkBytesReceivedCounters.Length > 0)
                {
                    try
                    {
                        nicInputBitsPerSec = _networkBytesReceivedCounters.Sum(c => c.NextValue()) * 8f;
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: reading network interface received counters failed: {ex.Message}");
                        nicInputBitsPerSec = 0f;
                    }
                }

                float nicInputKbps = nicInputBitsPerSec / 1000f;

                float nicTotalKbps = nicTotalBitsPerSec / 1000f;

                // Compute sent (output) as Bytes Total/sec - Bytes Received/sec (bytes/sec -> bits/sec)
                float bytesTotalSum = 0f;
                if (_networkBytesTotalCounters != null && _networkBytesTotalCounters.Length > 0)
                {
                    try { bytesTotalSum = _networkBytesTotalCounters.Sum(c => c.NextValue()); }
                    catch { bytesTotalSum = 0f; }
                }

                float bytesReceivedSum = 0f;
                if (_networkBytesReceivedCounters != null && _networkBytesReceivedCounters.Length > 0)
                {
                    try { bytesReceivedSum = _networkBytesReceivedCounters.Sum(c => c.NextValue()); }
                    catch { bytesReceivedSum = 0f; }
                }

                float sentBytesPerSec = bytesTotalSum - bytesReceivedSum;
                if (sentBytesPerSec < 0f) sentBytesPerSec = 0f;
                float sentBitsPerSec = sentBytesPerSec * 8f;
                float sentKbps = sentBitsPerSec / 1000f;

                // Link-capacity logic removed per user request.

                // Attach adapters
                stats.Adapters = adapterList.ToArray();

                // Use observed NIC totals for TotalBandwidth so the UI reacts immediately to traffic.
                float totalBandwidthKbps = nicTotalKbps > 0 ? nicTotalKbps : 0f;

                // Compute capacity (bits/sec) from Current Bandwidth counters if available.
                float nicCapacityBitsPerSec = 0f;
                bool capacityKnown = false;
                if (_networkCurrentBandwidthCounters != null && _networkCurrentBandwidthCounters.Length > 0)
                {
                    try
                    {
                        if (_preferredAdapterIndex.HasValue && _preferredAdapterIndex.Value >= 0 && _preferredAdapterIndex.Value < _networkCurrentBandwidthCounters.Length)
                        {
                            nicCapacityBitsPerSec = _networkCurrentBandwidthCounters[_preferredAdapterIndex.Value].NextValue();
                        }
                        else
                        {
                            nicCapacityBitsPerSec = _networkCurrentBandwidthCounters.Sum(c => c.NextValue());
                        }
                        capacityKnown = nicCapacityBitsPerSec > 0f;
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: reading Current Bandwidth counters failed: {ex.Message}");
                        capacityKnown = false;
                        nicCapacityBitsPerSec = 0f;
                    }
                }

                // Available = capacity - observed (use bits/sec values), fall back to Unknown if capacity not known.
                float availableKbps = 0f;
                if (capacityKnown)
                {
                    float availableBits = nicCapacityBitsPerSec - nicTotalBitsPerSec;
                    if (availableBits < 0f) availableBits = 0f;
                    availableKbps = availableBits / 1000f;
                }

                // Do not populate per-protocol bandwidth fields here.
                stats.TotalBandwidthKbps = (int)Math.Round(totalBandwidthKbps);
                stats.InputBandwidthKbps = (int)Math.Round(nicInputKbps);
                stats.SentBandwidthKbps = (int)Math.Round(sentKbps);
                stats.TotalBandwidthFormatted = $"{(int)Math.Round(totalBandwidthKbps)} Kbps";
                stats.InputBandwidthFormatted = $"{(int)Math.Round(nicInputKbps)} Kbps";
                stats.SentBandwidthFormatted = $"{(int)Math.Round(sentKbps)} Kbps";
                // Populate available bandwidth if capacity known
                stats.AvailableBandwidthKbps = (int)Math.Round(availableKbps);
                stats.AvailableBandwidthFormatted = capacityKnown ? $"{(int)Math.Round(availableKbps)} Kbps" : "Unknown";

                // Debug output for troubleshooting
                System.Diagnostics.Debug.WriteLine($"Total bandwidth: {totalBandwidthKbps:F1} Kbps");
                // Packet-splitting removed; no per-protocol packet debug output.

                // Get per-session statistics (only RTT is read per-session now)
                var sessionList = new System.Collections.Generic.List<SessionStats>();
                for (int i = 0; i < _instances.Length; i++)
                {
                    float rtt = _rfxRttCounters[i].NextValue();
                    sessionList.Add(new SessionStats
                    {
                        InstanceName = _instances[i],
                        // Per-protocol session bandwidth removed - only RTT retained
                        RttMs = rtt
                    });
                }
                stats.Sessions = sessionList.ToArray();
                stats.IsAvailable = true;
            }
            catch (Exception ex)
            {
                stats.ErrorMessage = $"Error reading RemoteFX stats: {ex.Message}";
                System.Diagnostics.Debug.WriteLine(stats.ErrorMessage);
            }

            return stats;
        }

        /// <summary>
        /// Gets encoder frames dropped - simplified version for MAUI
        /// In the original WinForms version, this used WMI queries
        /// </summary>
        public static int GetEncoderFramesDropped()
        {
            try
            {
                if (!OperatingSystem.IsWindows()) return -1;

                // Candidate category names to try first (common RemoteFX/encoder related categories)
                var preferredCategories = new[]
                {
                    "RemoteFX Video Encoder",
                    "RemoteFX Graphics",
                    "RemoteFX Graphics Encoder",
                    "RemoteFX",
                    "Terminal Services",
                    "Remote Desktop Services"
                };

                // Helper to probe a category for counters that look like frames-dropped
                int ProbeCategory(PerformanceCounterCategory cat)
                {
                    try
                    {
                        // Check non-instance counters
                        foreach (var c in cat.GetCounters())
                        {
                            var name = c.CounterName?.ToLowerInvariant() ?? string.Empty;
                            if (name.Contains("drop") || name.Contains("dropped") || (name.Contains("frame") && name.Contains("drop")))
                            {
                                try { return (int)Math.Round(c.NextValue()); } catch { }
                            }
                        }

                        // Check instance counters
                        var instances = cat.GetInstanceNames();
                        if (instances != null && instances.Length > 0)
                        {
                            foreach (var inst in instances)
                            {
                                try
                                {
                                    foreach (var c in cat.GetCounters(inst))
                                    {
                                        var name = c.CounterName?.ToLowerInvariant() ?? string.Empty;
                                        if (name.Contains("drop") || name.Contains("dropped") || (name.Contains("frame") && name.Contains("drop")))
                                        {
                                            try { return (int)Math.Round(c.NextValue()); } catch { }
                                        }
                                    }
                                }
                                catch { /* ignore instance probing errors */ }
                            }
                        }
                    }
                    catch { /* ignore category probing errors */ }

                    return -1;
                }

                // Try preferred categories first
                foreach (var catName in preferredCategories)
                {
                    try
                    {
                        if (PerformanceCounterCategory.Exists(catName))
                        {
                            var cat = new PerformanceCounterCategory(catName);
                            var v = ProbeCategory(cat);
                            if (v >= 0) return v;
                        }
                    }
                    catch { }
                }

                // Fall back to scanning all categories for likely counters
                foreach (var cat in PerformanceCounterCategory.GetCategories())
                {
                    var v = ProbeCategory(cat);
                    if (v >= 0) return v;
                }

                // If nothing found, return -1 to indicate unavailable
                return -1;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting encoder frames dropped: {ex.Message}");
                return -1;
            }
        }

        /// <summary>
        /// Gets input frames per second - simplified version for MAUI
        /// In the original WinForms version, this used WMI queries
        /// </summary>
        public static int GetInputFramesPerSecond()
        {
            try
            {
                // TODO: Could be enhanced with actual WMI queries or performance counters
                // For now, return a placeholder value based on display refresh rate
                var refreshRate = DisplayInfoHelper.GetDisplayRefreshRate();
                return refreshRate > 0 ? (int)refreshRate : 60;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting input frames per second: {ex.Message}");
                return -1;
            }
        }

        /// <summary>
        /// Disposes performance counters
        /// </summary>
        public static void Dispose()
        {
            try
            {
                // Dispose only counters that are still present
                _rfxRttCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesTotalCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesReceivedCounters?.ToList().ForEach(c => c.Dispose());
                _networkCurrentBandwidthCounters?.ToList().ForEach(c => c.Dispose());
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error disposing performance counters: {ex.Message}");
            }
        }
    }
}
