using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.Versioning;

namespace PProtocolAnalyzer.Helpers
{
    public class RemoteFXNetworkStats
    {
        public float UdpSentRate { get; set; }
        public float UdpRecvRate { get; set; }
        public string UdpSentRateFormatted { get; set; } = "";
        public string UdpRecvRateFormatted { get; set; } = "";
    // New bandwidth breakdown (Kbps)
    public float TotalBandwidthKbps { get; set; }
    public float UdpBandwidthKbps { get; set; }
    public float TcpBandwidthKbps { get; set; }
    public float RdpBandwidthKbps { get; set; }
    public float InputBandwidthKbps { get; set; }
    public string TotalBandwidthFormatted { get; set; } = "";
    public string UdpBandwidthFormatted { get; set; } = "";
    public string TcpBandwidthFormatted { get; set; } = "";
    public string RdpBandwidthFormatted { get; set; } = "";
    public string InputBandwidthFormatted { get; set; } = "";
        public SessionStats[] Sessions { get; set; } = Array.Empty<SessionStats>();
        public bool IsAvailable { get; set; }
        public string ErrorMessage { get; set; } = "";
    }

    public class SessionStats
    {
        public string InstanceName { get; set; } = "";
        // Per-session bandwidth breakdown in MB/s
        public float UdpBandwidthMBps { get; set; }
        public float TcpBandwidthMBps { get; set; }
        public float RttMs { get; set; }
    }

    public static class RealTimeStatisticsHelper
    {
        private static PerformanceCounter[]? _udpSentCounters;
        private static PerformanceCounter[]? _udpRecvCounters;
        private static PerformanceCounter[]? _rfxBwCounters;
    private static PerformanceCounter[]? _rfxTcpBwCounters;
        private static PerformanceCounter[]? _rfxRttCounters;
    private static PerformanceCounter[]? _networkBytesTotalCounters;
    private static PerformanceCounter[]? _networkBytesReceivedCounters;
        private static string[]? _instances;
        private static bool _countersInitialized = false;
        private static string? _initializationError;

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
                const string sentCn = "UDP Sent Rate";
                const string recvCn = "UDP Received Rate";
                const string bwCn = "Current UDP Bandwidth";
                const string tcpBwCn = "Current TCP Bandwidth";
                const string rttCn = "Current UDP RTT";

                var category = new PerformanceCounterCategory(cat);
                var missingCounters = new System.Collections.Generic.List<string>();
                
                if (!category.CounterExists(sentCn)) missingCounters.Add($"'{sentCn}' in {cat}");
                if (!category.CounterExists(recvCn)) missingCounters.Add($"'{recvCn}' in {cat}");
                if (!category.CounterExists(bwCn)) missingCounters.Add($"'{bwCn}' in {cat}");
                if (!category.CounterExists(rttCn)) missingCounters.Add($"'{rttCn}' in {cat}");
                
                if (missingCounters.Count > 0)
                {
                    _initializationError = $"Missing counter(s): {string.Join(", ", missingCounters)}";
                    return;
                }

                // Instantiate counters
                _instances = category.GetInstanceNames();
                _udpSentCounters = _instances.Select(i => new PerformanceCounter(cat, sentCn, i, true)).ToArray();
                _udpRecvCounters = _instances.Select(i => new PerformanceCounter(cat, recvCn, i, true)).ToArray();
                _rfxBwCounters = _instances.Select(i => new PerformanceCounter(cat, bwCn, i, true)).ToArray();
                _rfxTcpBwCounters = _instances.Select(i => new PerformanceCounter(cat, tcpBwCn, i, true)).ToArray();
                _rfxRttCounters = _instances.Select(i => new PerformanceCounter(cat, rttCn, i, true)).ToArray();

                // Warm up counters for accurate readings
                foreach (var c in _udpSentCounters) c.NextValue();
                foreach (var c in _udpRecvCounters) c.NextValue();
                foreach (var c in _rfxBwCounters) c.NextValue();
                foreach (var c in _rfxTcpBwCounters) c.NextValue();
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
                        foreach (var c in _networkBytesTotalCounters) c.NextValue();
                        foreach (var c in _networkBytesReceivedCounters) c.NextValue();
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

                if (_udpSentCounters == null || _udpRecvCounters == null || 
                _rfxBwCounters == null || _rfxTcpBwCounters == null || _rfxRttCounters == null || _instances == null)
            {
                stats.ErrorMessage = "Performance counters not available";
                return stats;
            }

            try
            {
                // Read per-protocol bandwidth (bits per second)
                float totalUdpBitsPerSec = _rfxBwCounters.Sum(c => c.NextValue());
                float totalTcpBitsPerSec = _rfxTcpBwCounters.Sum(c => c.NextValue());
                float totalRdpBitsPerSec = totalUdpBitsPerSec + totalTcpBitsPerSec;

                float totalUdpKbps = totalUdpBitsPerSec / 1000f;
                float totalTcpKbps = totalTcpBitsPerSec / 1000f;
                float totalRdpKbps = totalRdpBitsPerSec / 1000f; // Convert bits/sec to Kbps

                // Compute NIC total bandwidth from Network Interface counters (Bytes/sec -> bits/sec)
                float nicTotalBitsPerSec = 0f;
                if (_networkBytesTotalCounters != null && _networkBytesTotalCounters.Length > 0)
                {
                    try
                    {
                        // Bytes/sec to bits/sec = *8
                        nicTotalBitsPerSec = _networkBytesTotalCounters.Sum(c => c.NextValue()) * 8f;
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: reading network interface counters failed: {ex.Message}");
                        nicTotalBitsPerSec = 0f;
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

                // Decide which value to treat as TotalBandwidth: NIC total when available, otherwise RDP total
                float totalBandwidthKbps = nicTotalKbps > 0 ? nicTotalKbps : totalRdpKbps;

                // Get packet rates to determine sent/received traffic split
                float sentPacketsPerSec = _udpSentCounters.Sum(c => c.NextValue());
                float recvPacketsPerSec = _udpRecvCounters.Sum(c => c.NextValue());
                float totalPacketsPerSec = sentPacketsPerSec + recvPacketsPerSec;

                // Split total bandwidth based on packet ratios
                float sentKbps, recvKbps;
                if (totalPacketsPerSec > 0)
                {
                    sentKbps = totalBandwidthKbps * (sentPacketsPerSec / totalPacketsPerSec);
                    recvKbps = totalBandwidthKbps * (recvPacketsPerSec / totalPacketsPerSec);
                }
                else
                {
                    // No traffic - show zero
                    sentKbps = recvKbps = 0f;
                }

                // Convert to integers for display (no decimal points)
                int sentKbpsInt = (int)Math.Round(sentKbps);
                int recvKbpsInt = (int)Math.Round(recvKbps);

                stats.UdpSentRate = sentKbpsInt;
                stats.UdpRecvRate = recvKbpsInt;
                stats.UdpSentRateFormatted = $"{sentKbpsInt} Kbps";
                stats.UdpRecvRateFormatted = $"{recvKbpsInt} Kbps";

                // Fill bandwidth breakdown
                stats.UdpBandwidthKbps = (int)Math.Round(totalUdpKbps);
                stats.TcpBandwidthKbps = (int)Math.Round(totalTcpKbps);
                stats.RdpBandwidthKbps = (int)Math.Round(totalRdpKbps);
                stats.TotalBandwidthKbps = (int)Math.Round(totalBandwidthKbps);
                stats.InputBandwidthKbps = (int)Math.Round(nicInputKbps);
                stats.UdpBandwidthFormatted = $"{(int)Math.Round(totalUdpKbps)} Kbps";
                stats.TcpBandwidthFormatted = $"{(int)Math.Round(totalTcpKbps)} Kbps";
                stats.RdpBandwidthFormatted = $"{(int)Math.Round(totalRdpKbps)} Kbps";
                stats.TotalBandwidthFormatted = $"{(int)Math.Round(totalBandwidthKbps)} Kbps";
                stats.InputBandwidthFormatted = $"{(int)Math.Round(nicInputKbps)} Kbps";

                // Debug output for troubleshooting
                System.Diagnostics.Debug.WriteLine($"Total bandwidth: {totalBandwidthKbps:F1} Kbps");
                System.Diagnostics.Debug.WriteLine($"Packet rates - Sent: {sentPacketsPerSec:F1} pps, Recv: {recvPacketsPerSec:F1} pps");
                System.Diagnostics.Debug.WriteLine($"Final rates - Sent: {sentKbpsInt} Kbps, Recv: {recvKbpsInt} Kbps");

                // Get per-session statistics
                var sessionList = new System.Collections.Generic.List<SessionStats>();
                for (int i = 0; i < _instances.Length; i++)
                {
                    float bwUdpBits = _rfxBwCounters[i].NextValue();
                    float bwTcpBits = _rfxTcpBwCounters[i].NextValue();
                    float bwBits = bwUdpBits + bwTcpBits;
                    float bwMB = (bwBits / 8f) / (1024f * 1024f);
                    float bwUdpMB = (bwUdpBits / 8f) / (1024f * 1024f);
                    float bwTcpMB = (bwTcpBits / 8f) / (1024f * 1024f);
                    float rtt = _rfxRttCounters[i].NextValue();
                    
                    sessionList.Add(new SessionStats
                    {
                        InstanceName = _instances[i],
                        UdpBandwidthMBps = bwUdpMB,
                        TcpBandwidthMBps = bwTcpMB,
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
                // TODO: Could be enhanced with actual WMI queries or performance counters
                // For now, return a placeholder value
                return 0;
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
                _udpSentCounters?.ToList().ForEach(c => c.Dispose());
                _udpRecvCounters?.ToList().ForEach(c => c.Dispose());
                _rfxBwCounters?.ToList().ForEach(c => c.Dispose());
                _rfxRttCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesTotalCounters?.ToList().ForEach(c => c.Dispose());
                _networkBytesReceivedCounters?.ToList().ForEach(c => c.Dispose());
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error disposing performance counters: {ex.Message}");
            }
        }
    }
}
