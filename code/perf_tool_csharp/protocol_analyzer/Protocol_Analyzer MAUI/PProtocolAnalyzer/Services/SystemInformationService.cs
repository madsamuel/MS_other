using PProtocolAnalyzer.Helpers;
using Microsoft.Extensions.Logging;
using PProtocolAnalyzer.Models;
using System.Threading.Tasks;

namespace PProtocolAnalyzer.Services
{
    public class SystemInformationService : ISystemInformationService
    {
        public async Task<SystemInformation> GetSystemInformationAsync()
        {
            var systemInfo = new SystemInformation();

            // Load all sections asynchronously
            var gpuTask = GetGpuInformationAsync();
            var detectedTask = GetDetectedSettingsAsync();
            var statsTask = GetRealTimeStatisticsAsync();
            var sessionTask = GetSessionInfoAsync();
            var customTask = GetCustomSettingsAsync();

            await Task.WhenAll(gpuTask, detectedTask, statsTask, sessionTask, customTask);

            systemInfo.GpuInformation = await gpuTask;
            systemInfo.DetectedSettings = await detectedTask;
            systemInfo.RealTimeStatistics = await statsTask;
            systemInfo.SessionInfo = await sessionTask;
            systemInfo.CustomSettings = await customTask;

            return systemInfo;
        }

        public async Task<GpuInformation> GetGpuInformationAsync()
        {
            return await Task.Run(() =>
            {
                var gpuInfo = new GpuInformation();

                try
                {
                    // Use the enhanced GPU information helper based on WinForms patterns
                    var (resolution, dpiScale) = GpuInformationHelper.GetMainDisplayInfo();
                    var (sessionType, gpuType, encoderType, hwEncode) = GpuInformationHelper.GetGraphicsProfileDetails();

                    gpuInfo.MainDisplayResolution = $"Main Display Resolution: {resolution}";
                    gpuInfo.DpiScale = $"DPI Scale: {dpiScale}";
                    gpuInfo.SessionType = $"Session Type: {sessionType}";
                    gpuInfo.GpuType = $"GPU Type: {gpuType}";
                    gpuInfo.Encoding = $"Encoding: {encoderType}";
                    gpuInfo.HwEncode = $"HW Encode: {hwEncode}";
                }
                catch (System.Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SystemInformationService));
                    try { lg?.LogError(ex, $"Error loading GPU information: {ex.Message}"); } catch { }
                    // Set fallback values
                    gpuInfo.MainDisplayResolution = "Main Display Resolution: Unknown";
                    gpuInfo.DpiScale = "DPI Scale: Unknown";
                    gpuInfo.SessionType = "Session Type: Unknown";
                    gpuInfo.GpuType = "GPU Type: Unknown";
                    gpuInfo.Encoding = "Encoding: Unknown";
                    gpuInfo.HwEncode = "HW Encode: Unknown";
                }

                return gpuInfo;
            });
        }

        public async Task<DetectedSettings> GetDetectedSettingsAsync()
        {
            return await Task.Run(() =>
            {
                var detectedSettings = new DetectedSettings();

                try
                {
                    // Use the existing working DisplayInfoHelper methods through DetectedSettingsHelper
                    var (width, height, refreshRate, scalingFactor) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
                    var visualQuality = DetectedSettingsHelper.GetVisualQuality();
                    var hwEncodeSupported = DetectedSettingsHelper.IsHardwareEncodingSupported();
                    var encoderType = DetectedSettingsHelper.GetEncoderType();

                    detectedSettings.DisplayResolution = $"Display Resolution: {(width > 0 && height > 0 ? $"{width} x {height}" : "Unknown")}";
                    detectedSettings.DisplayRefreshRate = $"Display Refresh Rate: {(refreshRate > 0 ? $"{refreshRate} Hz" : "Unknown")}";
                    detectedSettings.Scaling = $"Scaling: {scalingFactor * 100:F0}%";
                    detectedSettings.VisualQuality = $"Visual Quality: {visualQuality}";
                    // Max frames value removed from UI; GetMaxFPS() still available in helper if needed
                    detectedSettings.HardwareEncode = $"Hardware Encode: {(hwEncodeSupported ? "Active" : "Inactive")}";
                    detectedSettings.EncoderType = $"Encoder type: {encoderType}";
                }
                catch (System.Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SystemInformationService));
                    try { lg?.LogError(ex, $"Error loading detected settings: {ex.Message}"); } catch { }
                    // Set fallback values
                    detectedSettings.DisplayResolution = "Display Resolution: Unknown";
                    detectedSettings.DisplayRefreshRate = "Display Refresh Rate: Unknown";
                    detectedSettings.Scaling = "Scaling: Unknown";
                    detectedSettings.VisualQuality = "Visual Quality: Unknown";
                    // Max frames value removed from UI; no fallback needed
                    detectedSettings.HardwareEncode = "Hardware Encode: Unknown";
                    detectedSettings.EncoderType = "Encoder type: Unknown";
                }

                return detectedSettings;
            });
        }

        public async Task<RealTimeStatistics> GetRealTimeStatisticsAsync()
        {
            return await Task.Run(() =>
            {
                var stats = new RealTimeStatistics();

                try
                {
                    var framesDropped = RealTimeStatisticsHelper.GetEncoderFramesDropped();
                    var inputFps = RealTimeStatisticsHelper.GetInputFramesPerSecond();

                    stats.EncoderFramesDropped = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString() : "Unavailable")}";
                    stats.InputFramesPerSecond = $"Input Frames Per Second: {(inputFps >= 0 ? inputFps.ToString() : "Unavailable")}";
                }
                catch (System.Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SystemInformationService));
                    try { lg?.LogError(ex, $"Error loading real-time statistics: {ex.Message}"); } catch { }
                    stats.EncoderFramesDropped = "Encoder Frames Dropped: (waiting for data)";
                    stats.InputFramesPerSecond = "Input Frames Per Second: (waiting for data)";
                }

                return stats;
            });
        }

        public async Task<SessionInfo> GetSessionInfoAsync()
        {
            return await Task.Run(() =>
            {
                var sessionInfo = new SessionInfo();

                try
                {
                    var (sessionId, clientName, protocolVersion) = SessionInfoHelper.GetSessionInfo();

                    sessionInfo.SessionId = $"Session Id: {sessionId}";
                    sessionInfo.ClientName = $"Client Name: {clientName ?? "N/A"}";
                    sessionInfo.ProtocolVersion = $"Protocol Version: {protocolVersion ?? "N/A"}";
                }
                catch (System.Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SystemInformationService));
                    try { lg?.LogError(ex, $"Error loading session info: {ex.Message}"); } catch { }
                    sessionInfo.SessionId = "Session Id: Unknown";
                    sessionInfo.ClientName = "Client Name: Unknown";
                    sessionInfo.ProtocolVersion = "Protocol Version: Unknown";
                }

                return sessionInfo;
            });
        }

        public async Task<CustomSettings> GetCustomSettingsAsync()
        {
            return await Task.Run(() =>
            {
                var customSettings = new CustomSettings();

                try
                {
                    var settingsDisplay = CustomSettingsHelper.GetCustomSettingsDisplay();
                    customSettings.Settings = settingsDisplay;
                }
                catch (System.Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(SystemInformationService));
                    try { lg?.LogError(ex, $"Error loading custom settings: {ex.Message}"); } catch { }
                    customSettings.Settings = "No custom settings found.";
                }

                return customSettings;
            });
        }
    }
}
