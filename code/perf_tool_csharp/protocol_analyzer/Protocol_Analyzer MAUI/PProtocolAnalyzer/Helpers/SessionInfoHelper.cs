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
    }
}
