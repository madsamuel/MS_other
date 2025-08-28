using System;
using System.Diagnostics;
using System.Security.Principal;

namespace PProtocolAnalyzer.Helpers
{
    public static class SessionInfoHelper
    {
        /// <summary>
        /// Gets session statistics - simplified version for MAUI
        /// In the original WinForms version, this used RdpNative.GetRdpStatistics()
        /// </summary>
        public static (string sessionId, string clientName, string protocolVersion) GetSessionInfo()
        {
            try
            {
                // Get session ID from current process
                string sessionId = GetCurrentSessionId();
                
                // For desktop MAUI apps, client name is typically the local machine
                string clientName = Environment.MachineName;
                
                // Default protocol version for local sessions
                string protocolVersion = "Local Session";

                // Check if we're in an RDP session
                if (IsRemoteSession())
                {
                    clientName = GetClientName() ?? "Remote Client";
                    protocolVersion = "RDP 8.1+";
                }

                return (sessionId, clientName, protocolVersion);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting session info: {ex.Message}");
                return ("Unknown", "Unknown", "Unknown");
            }
        }

        private static string GetCurrentSessionId()
        {
            try
            {
                using (var process = Process.GetCurrentProcess())
                {
                    return process.SessionId.ToString();
                }
            }
            catch
            {
                return "1"; // Default session ID
            }
        }

        private static bool IsRemoteSession()
        {
            try
            {
                // Check if running in a remote session
                var sessionName = Environment.GetEnvironmentVariable("SESSIONNAME");
                return !string.IsNullOrEmpty(sessionName) && sessionName.StartsWith("RDP-");
            }
            catch
            {
                return false;
            }
        }

        private static string? GetClientName()
        {
            try
            {
                // Try to get client name from environment variables
                return Environment.GetEnvironmentVariable("CLIENTNAME");
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Attempts to resolve the client IP address for the current session. This is best-effort:
        /// - For RDP sessions, uses CLIENTNAME environment variable and DNS to resolve to an IPv4 address.
        /// - Returns null if resolution fails.
        /// </summary>
        public static System.Net.IPAddress? GetClientIpAddress()
        {
            try
            {
                var clientName = GetClientName();
                if (string.IsNullOrEmpty(clientName)) return null;

                // Try to resolve DNS A records for the client name
                var addresses = System.Net.Dns.GetHostAddresses(clientName);
                var ipv4 = addresses.FirstOrDefault(a => a.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork);
                return ipv4;
            }
            catch
            {
                return null;
            }
        }
    }
}
