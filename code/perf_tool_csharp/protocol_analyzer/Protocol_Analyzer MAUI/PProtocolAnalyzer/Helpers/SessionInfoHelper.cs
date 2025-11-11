using System;
using System.Diagnostics;
using System.Security.Principal;
using Microsoft.Extensions.Logging;

namespace PProtocolAnalyzer.Helpers
{
    public static class SessionInfoHelper
    {
    // Cached snapshot to avoid repeated environment/interop calls. Access synchronized via _cacheLock.
    private static (string sessionId, string clientName, string protocolVersion)? _cachedSnapshot;
        private static readonly object _cacheLock = new object();

        /// <summary>
        /// Gets session statistics - simplified version for MAUI
        /// In the original WinForms version, this used RdpNative.GetRdpStatistics()
        /// This implementation is conservative (best-effort): it caches a snapshot and uses multiple heuristics
        /// to detect remote sessions and resolve client information. Use ClearCache() in tests if needed.
        /// </summary>
        public static (string sessionId, string clientName, string protocolVersion) GetSessionInfo()
        {
            // Fast-path return cached snapshot
            var cached = _cachedSnapshot;
            if (cached.HasValue)
                return cached.Value;

            lock (_cacheLock)
            {
                if (_cachedSnapshot.HasValue)
                    return _cachedSnapshot.Value;

                try
                {
                    var sessionId = GetCurrentSessionId();
                    var clientName = Environment.MachineName;
                    var protocolVersion = "Local Session";

                    if (IsRemoteSession())
                    {
                        // prefer the CLIENTNAME env var when present
                        var cn = GetClientName();
                        if (!string.IsNullOrEmpty(cn))
                            clientName = cn;

                        // We cannot reliably detect exact RDP minor versions here; provide a helpful label.
                        protocolVersion = DetectRdpProtocolVersion() ?? "RDP (unknown)";
                    }

                    var snapshot = (sessionId, clientName, protocolVersion);
                    _cachedSnapshot = snapshot;
                    return snapshot;
                }
                catch (Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SessionInfoHelper));
                    try { lg?.LogError(ex, $"Error getting session info: {ex.Message}"); } catch { /* Logging should never crash the application */ }
                    return ("Unknown", "Unknown", "Unknown");
                }
            }
        }

        /// <summary>
        /// Clears the cached snapshot. Useful for unit tests or when environment changes at runtime.
        /// </summary>
        public static void ClearCache()
        {
            lock (_cacheLock)
            {
                _cachedSnapshot = null;
            }
        }

        /// <summary>
        /// Best-effort detection of RDP protocol version. Currently uses SESSIONNAME heuristics.
        /// Future improvement: use WTSQuerySessionInformation / QueryUserConfig APIs when available.
        /// </summary>
        private static string? DetectRdpProtocolVersion()
        {
            try
            {
                var sessionName = Environment.GetEnvironmentVariable("SESSIONNAME");
                if (string.IsNullOrEmpty(sessionName)) return null;

                // SESSIONNAME often contains RDP-Tcp#<n> or RDP-<something>. We can't reliably get exact minor version,
                // but if we see "RDP-Tcp" or "RDP-" we can at least return a generic RDP label.
                if (sessionName.StartsWith("RDP-", StringComparison.OrdinalIgnoreCase) || sessionName.StartsWith("RDP-Tcp", StringComparison.OrdinalIgnoreCase))
                    return "RDP";

                return null;
            }
            catch { return null; }
        }

        private static string GetCurrentSessionId()
        {
            try
            {
                using (var process = Process.GetCurrentProcess())
                {
                    return process.SessionId.ToString(System.Globalization.CultureInfo.InvariantCulture);
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
