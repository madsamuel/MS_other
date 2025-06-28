using System;
using System.Runtime.InteropServices;
using System.Text;

namespace RdpStatsApp
{
    public class RdpNative
    {
        // WTS API constants, info classes, and native API declarations go here

        // RDP Statistics structure based on MS-RDPBCGR specification
        [StructLayout(LayoutKind.Sequential)]
        public struct RdpStatistics
        {
            public ulong BytesSent;
            public ulong BytesReceived;
            public ulong FramesSent;
            public ulong FramesReceived;
            public ulong SendRate;
            public ulong ReceiveRate;
            public int SessionId;
            public string ClientName;
            public string ProtocolVersion;
            public int RoundTripTime;
            public ulong BandwidthAvailable;
            public string ConnectionQuality;
        }

        public static RdpStatistics GetRdpStatistics()
        {
            var stats = new RdpStatistics();
            try
            {
                // Get current session ID
                int processId = GetCurrentProcessId();
                if (ProcessIdToSessionId(processId, out int sessionId))
                {
                    stats.SessionId = sessionId;
                    // Get session information
                    stats.ClientName = GetSessionInfo(sessionId, 10); // WTSClientName
                    stats.ProtocolVersion = "RDP 8.1+"; // Default assumption
                    // Get connection state to determine if it's an RDP session
                    bool isRdpSession = IsRdpSession(sessionId);
                    if (isRdpSession)
                    {
                        // Get RDP-specific statistics
                        stats.BytesSent = GetSessionUlong(sessionId, 20); // WTSOutgoingBytes
                        stats.BytesReceived = GetSessionUlong(sessionId, 19); // WTSIncomingBytes
                        stats.FramesSent = GetSessionUlong(sessionId, 22); // WTSOutgoingFrames
                        stats.FramesReceived = GetSessionUlong(sessionId, 21); // WTSIncomingFrames
                        // Calculate rates (this would need to be done over time)
                        stats.SendRate = 0; // Will be calculated by the main app
                        stats.ReceiveRate = 0; // Will be calculated by the main app
                        // Estimate connection quality based on available data
                        stats.ConnectionQuality = EstimateConnectionQuality(stats);
                    }
                }
            }
            catch (Exception ex)
            {
                // Handle exceptions gracefully
                stats.ClientName = "Error: " + ex.Message;
            }
            return stats;
        }

        private static string GetSessionInfo(int sessionId, int infoClass)
        {
            try
            {
                IntPtr buffer;
                uint bytesReturned;
                if (WTSQuerySessionInformation(IntPtr.Zero, sessionId, infoClass, out buffer, out bytesReturned))
                {
                    if (buffer != IntPtr.Zero)
                    {
                        string result = Marshal.PtrToStringAnsi(buffer);
                        WTSFreeMemory(buffer);
                        return result ?? "";
                    }
                }
            }
            catch { }
            return "";
        }

        private static ulong GetSessionUlong(int sessionId, int infoClass)
        {
            try
            {
                IntPtr buffer;
                uint bytesReturned;
                if (WTSQuerySessionInformation(IntPtr.Zero, sessionId, infoClass, out buffer, out bytesReturned))
                {
                    if (buffer != IntPtr.Zero && bytesReturned >= sizeof(ulong))
                    {
                        ulong result = (ulong)Marshal.ReadInt64(buffer);
                        WTSFreeMemory(buffer);
                        return result;
                    }
                    WTSFreeMemory(buffer);
                }
            }
            catch { }
            return 0;
        }

        private static bool IsRdpSession(int sessionId)
        {
            try
            {
                string winStationName = GetSessionInfo(sessionId, 6); // WTSWinStationName
                return !string.IsNullOrEmpty(winStationName) &&
                       (winStationName.StartsWith("RDP", StringComparison.OrdinalIgnoreCase) ||
                        winStationName.Contains("rdp", StringComparison.OrdinalIgnoreCase));
            }
            catch { return false; }
        }

        private static string EstimateConnectionQuality(RdpStatistics stats)
        {
            if (stats.BandwidthAvailable > 10000000)
                return "Excellent";
            else if (stats.BandwidthAvailable > 5000000)
                return "Good";
            else if (stats.BandwidthAvailable > 1000000)
                return "Fair";
            else
                return "Poor";
        }

        // Native API declarations
        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern bool WTSQuerySessionInformation(
            IntPtr hServer,
            int sessionId,
            int wtsInfoClass,
            out IntPtr ppBuffer,
            out uint pBytesReturned);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern void WTSFreeMemory(IntPtr pMemory);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern int GetCurrentProcessId();

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool ProcessIdToSessionId(
            int dwProcessId,
            out int pSessionId);
    }
}
