using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.Versioning;
using Microsoft.Extensions.Logging;

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
        // Synchronize initialization
        private static readonly object _initLock = new object();
    // Sampling background worker
    private static CancellationTokenSource? _samplingCts;
    private static Task? _samplingTask;
    private static readonly object _statsLock = new object();
    private static RemoteFXNetworkStats? _latestStats;

        /// <summary>
        /// Initializes RemoteFX performance counters
        /// </summary>
        [SupportedOSPlatform("windows")]
        public static void InitializeRemoteFXCounters()
        {
            // Ensure only one thread initializes at a time and allow re-initialization after Dispose
            lock (_initLock)
            {
                if (_countersInitialized) return;

                // Reset previous error state
                _initializationError = null;

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

                    // Dispose any prior counters before re-creating
                    Dispose();

                    // Instantiate counters
                    _instances = category.GetInstanceNames();
                    // Only initialize RTT counters for per-session latency
                    _rfxRttCounters = _instances.Select(i => new PerformanceCounter(cat, rttCn, i, true)).ToArray();

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
                                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                                try { lg?.LogInformation(ex2, $"Info: Current Bandwidth counter not available for some adapters: {ex2.Message}"); } catch { }
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
                                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                                try { lg?.LogInformation(ex, $"Info: failed to detect preferred adapter: {ex.Message}"); } catch { }
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                        try { lg?.LogWarning(ex, $"Warning: Failed to initialize Network Interface counters: {ex.Message}"); } catch { }
                    }

                    _countersInitialized = true;
                    // Start the background sampler with a 1s interval if not already running
                    StartSampling(1000);
                }
                catch (Exception ex)
                {
                    _initializationError = $"Error initializing RemoteFX counters: {ex.Message}";
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                    try { lg?.LogError(ex, _initializationError); } catch { }
                }
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

                // Single-sample reads: sample each counter once to avoid inconsistent multi-call NextValue behavior
                float nicTotalBitsPerSec = 0f;
                float nicInputBitsPerSec = 0f;
                float nicCapacityBitsPerSec = 0f;
                bool capacityKnown = false;

                var adapterList = new System.Collections.Generic.List<AdapterStats>();

                // Sample bytes total counters
                float[]? bytesTotalSamples = null;
                if (_networkBytesTotalCounters != null && _networkBytesTotalCounters.Length > 0)
                {
                    bytesTotalSamples = new float[_networkBytesTotalCounters.Length];
                    for (int i = 0; i < _networkBytesTotalCounters.Length; i++)
                    {
                        try
                        {
                            bytesTotalSamples[i] = _networkBytesTotalCounters[i].NextValue();
                        }
                        catch (Exception ex)
                        {
                            bytesTotalSamples[i] = 0f;
                            var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                            try { lg?.LogWarning(ex, $"Warning: reading adapter total counter failed: {ex.Message}"); } catch { }
                        }
                    }
                }

                // Sample bytes received counters
                float[]? bytesReceivedSamples = null;
                if (_networkBytesReceivedCounters != null && _networkBytesReceivedCounters.Length > 0)
                {
                    bytesReceivedSamples = new float[_networkBytesReceivedCounters.Length];
                    for (int i = 0; i < _networkBytesReceivedCounters.Length; i++)
                    {
                        try
                        {
                            bytesReceivedSamples[i] = _networkBytesReceivedCounters[i].NextValue();
                        }
                        catch (Exception ex)
                        {
                            bytesReceivedSamples[i] = 0f;
                            var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                            try { lg?.LogWarning(ex, $"Warning: reading adapter received counter failed: {ex.Message}"); } catch { }
                        }
                    }
                }

                // Build adapter list and compute nic totals from samples
                if (bytesTotalSamples != null)
                {
                    for (int i = 0; i < bytesTotalSamples.Length; i++)
                    {
                        var bytesPerSec = bytesTotalSamples[i];
                        var bitsPerSec = bytesPerSec * 8f;
                        nicTotalBitsPerSec += bitsPerSec;
                        var kbps = bitsPerSec / 1000f;
                        var name = _networkBytesTotalCounters?[i].InstanceName ?? string.Empty;
                        adapterList.Add(new AdapterStats { Name = name, Kbps = kbps, Formatted = (kbps <= 999f ? ((int)Math.Round(kbps)).ToString() + " Kbps" : (kbps/1000f).ToString("F2") + " Mbps") });
                    }
                }

                if (bytesReceivedSamples != null)
                {
                    for (int i = 0; i < bytesReceivedSamples.Length; i++)
                    {
                        nicInputBitsPerSec += bytesReceivedSamples[i] * 8f;
                    }
                }

                // Compute sent as total - received using the sampled sums
                float sentBitsPerSec = Math.Max(0f, nicTotalBitsPerSec - nicInputBitsPerSec);

                // Sample current bandwidth counters (capacity) if present
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
                            // Sum up the reported capacities
                            float sum = 0f;
                            foreach (var c in _networkCurrentBandwidthCounters)
                            {
                                try { sum += c.NextValue(); } catch { }
                            }
                            nicCapacityBitsPerSec = sum;
                        }
                        capacityKnown = nicCapacityBitsPerSec > 0f;
                    }
                    catch (Exception ex)
                    {
                        var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                        try { lg?.LogWarning(ex, $"Warning: reading Current Bandwidth counters failed: {ex.Message}"); } catch { }
                        capacityKnown = false;
                        nicCapacityBitsPerSec = 0f;
                    }
                }

                // Populate stats using sampled values
                float totalBandwidthKbps = nicTotalBitsPerSec / 1000f;
                float nicInputKbps = nicInputBitsPerSec / 1000f;
                float sentKbps = sentBitsPerSec / 1000f;

                stats.Adapters = adapterList.ToArray();
                stats.TotalBandwidthKbps = (int)Math.Round(totalBandwidthKbps);
                stats.InputBandwidthKbps = (int)Math.Round(nicInputKbps);
                stats.SentBandwidthKbps = (int)Math.Round(sentKbps);
                stats.TotalBandwidthFormatted = $"{(int)Math.Round(totalBandwidthKbps)} Kbps";
                stats.InputBandwidthFormatted = $"{(int)Math.Round(nicInputKbps)} Kbps";
                stats.SentBandwidthFormatted = $"{(int)Math.Round(sentKbps)} Kbps";

                var availableKbps = 0f;
                if (capacityKnown)
                {
                    var availableBits = nicCapacityBitsPerSec - nicTotalBitsPerSec;
                    if (availableBits < 0f) availableBits = 0f;
                    availableKbps = availableBits / 1000f;
                }
                stats.AvailableBandwidthKbps = (int)Math.Round(availableKbps);
                stats.AvailableBandwidthFormatted = capacityKnown ? $"{(int)Math.Round(availableKbps)} Kbps" : "Unknown";

                // Debug output for troubleshooting
                var lg2 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                try { lg2?.LogDebug($"Total bandwidth: {totalBandwidthKbps:F1} Kbps"); } catch { }
                // Packet-splitting removed; no per-protocol packet debug output.

                // Get per-session statistics (only RTT is read per-session now)
                var sessionList = new System.Collections.Generic.List<SessionStats>();
                if (_instances != null && _rfxRttCounters != null)
                {
                    var count = Math.Min(_instances.Length, _rfxRttCounters.Length);
                    for (int i = 0; i < count; i++)
                    {
                        try
                        {
                            float rtt = _rfxRttCounters[i].NextValue();
                            sessionList.Add(new SessionStats
                            {
                                InstanceName = _instances[i],
                                RttMs = rtt
                            });
                        }
                        catch (Exception ex)
                        {
                            var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                            try { lg?.LogWarning(ex, $"Warning: reading RTT counter for instance {_instances[i]} failed: {ex.Message}"); } catch { }
                        }
                    }
                }
                stats.Sessions = sessionList.ToArray();
                stats.IsAvailable = true;
            }
            catch (Exception ex)
            {
                stats.ErrorMessage = $"Error reading RemoteFX stats: {ex.Message}";
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                try { lg?.LogError(ex, stats.ErrorMessage); } catch { }
            }

            return stats;
        }

        /// <summary>
        /// Returns the latest sampled stats produced by the background sampler, or null if none yet.
        /// </summary>
        public static RemoteFXNetworkStats? GetLatestStats()
        {
            lock (_statsLock)
            {
                return _latestStats; // snapshot reference is fine; callers should not mutate
            }
        }

        /// <summary>
        /// Starts a background sampling loop with the specified interval in milliseconds.
        /// Safe to call multiple times; subsequent calls will restart the sampler with the new interval.
        /// </summary>
        public static void StartSampling(int intervalMs = 1000)
        {
            lock (_initLock)
            {
                StopSampling();
                _samplingCts = new CancellationTokenSource();
                var token = _samplingCts.Token;
                _samplingTask = Task.Run(async () =>
                {
                    while (!token.IsCancellationRequested)
                    {
                        try
                        {
                            var s = SampleOnce();
                            lock (_statsLock)
                            {
                                _latestStats = s;
                            }
                        }
                        catch (OperationCanceledException) { break; }
                        catch (Exception ex)
                        {
                            var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                            try { lg?.LogWarning(ex, $"Sampler error: {ex.Message}"); } catch { }
                        }

                        try { await Task.Delay(intervalMs, token); } catch (OperationCanceledException) { break; }
                    }
                }, token);
            }
        }

        /// <summary>
        /// Stops the background sampler if running.
        /// </summary>
        public static void StopSampling()
        {
            lock (_initLock)
            {
                try
                {
                    _samplingCts?.Cancel();
                }
                catch { }
                try { _samplingTask?.Wait(500); } catch { }
                try { _samplingCts?.Dispose(); } catch { }
                _samplingCts = null;
                _samplingTask = null;
            }
        }

        /// <summary>
        /// Samples the counters once and returns a populated RemoteFXNetworkStats instance.
        /// This re-uses the same sampling logic as GetRemoteFXStats but avoids updating shared state.
        /// </summary>
        private static RemoteFXNetworkStats SampleOnce()
        {
            // Reuse GetRemoteFXStats internal logic but avoid side-effects; call the method and return its result.
            // Note: GetRemoteFXStats performs its own error handling and returns a fresh RemoteFXNetworkStats.
            return GetRemoteFXStats();
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
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                try { lg?.LogError(ex, $"Error getting encoder frames dropped: {ex.Message}"); } catch { }
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
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                try { lg?.LogError(ex, $"Error getting input frames per second: {ex.Message}"); } catch { }
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
                // Stop background sampler first
                StopSampling();
                // Dispose only counters that are still present
                _rfxRttCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesTotalCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesReceivedCounters?.ToList().ForEach(c => c.Dispose());
                _networkCurrentBandwidthCounters?.ToList().ForEach(c => c.Dispose());
                _rfxRttCounters = null;
                _networkBytesTotalCounters = null;
                _networkBytesReceivedCounters = null;
                _networkCurrentBandwidthCounters = null;
                _instances = null;
                _countersInitialized = false;
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(RealTimeStatisticsHelper));
                try { lg?.LogWarning(ex, $"Error disposing performance counters: {ex.Message}"); } catch { }
            }
        }
    }
}
