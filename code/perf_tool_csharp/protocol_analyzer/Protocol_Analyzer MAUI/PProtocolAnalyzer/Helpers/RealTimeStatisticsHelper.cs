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
        public SessionStats[] Sessions { get; set; } = Array.Empty<SessionStats>();
        public bool IsAvailable { get; set; }
        public string ErrorMessage { get; set; } = "";
    }

    public class SessionStats
    {
        public string InstanceName { get; set; } = "";
        public float BandwidthMBps { get; set; }
        public float RttMs { get; set; }
    }

    public static class RealTimeStatisticsHelper
    {
        private static PerformanceCounter[]? _udpSentCounters;
        private static PerformanceCounter[]? _udpRecvCounters;
        private static PerformanceCounter[]? _rfxBwCounters;
        private static PerformanceCounter[]? _rfxRttCounters;
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
                _rfxRttCounters = _instances.Select(i => new PerformanceCounter(cat, rttCn, i, true)).ToArray();

                // Warm up counters for accurate readings
                foreach (var c in _udpSentCounters) c.NextValue();
                foreach (var c in _udpRecvCounters) c.NextValue();
                foreach (var c in _rfxBwCounters) c.NextValue();
                foreach (var c in _rfxRttCounters) c.NextValue();

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
                _rfxBwCounters == null || _rfxRttCounters == null || _instances == null)
            {
                stats.ErrorMessage = "Performance counters not available";
                return stats;
            }

            try
            {
                // Get UDP packet rates
                float sentPackets = _udpSentCounters.Sum(c => c.NextValue());
                float recvPackets = _udpRecvCounters.Sum(c => c.NextValue());

                // Convert to bandwidth (assume 1472 bytes per UDP packet for Ethernet)
                const float bytesPerPacket = 1472f;
                float sentKbps = (sentPackets * bytesPerPacket * 8) / 1024f;
                float recvKbps = (recvPackets * bytesPerPacket * 8) / 1024f;

                stats.UdpSentRate = sentKbps;
                stats.UdpRecvRate = recvKbps;
                stats.UdpSentRateFormatted = $"{sentKbps:F1} kbps";
                stats.UdpRecvRateFormatted = $"{recvKbps:F1} kbps";

                // Get per-session statistics
                var sessionList = new System.Collections.Generic.List<SessionStats>();
                for (int i = 0; i < _instances.Length; i++)
                {
                    float bwBits = _rfxBwCounters[i].NextValue();
                    float bwMB = (bwBits / 8f) / (1024f * 1024f);
                    float rtt = _rfxRttCounters[i].NextValue();
                    
                    sessionList.Add(new SessionStats
                    {
                        InstanceName = _instances[i],
                        BandwidthMBps = bwMB,
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
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error disposing performance counters: {ex.Message}");
            }
        }
    }
}
