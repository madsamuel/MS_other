using Protocol_Analyzer.Models;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class SystemInformationService : ISystemInformationService
    {
        private readonly IGpuInformationService _gpuService;
        private readonly IDetectedSettingsService _detectedSettingsService;
        private readonly IRealTimeStatisticsService _statisticsService;
        private readonly ISessionInfoService _sessionInfoService;
        private readonly ICustomSettingsService _customSettingsService;

        public SystemInformationService(
            IGpuInformationService gpuService,
            IDetectedSettingsService detectedSettingsService,
            IRealTimeStatisticsService statisticsService,
            ISessionInfoService sessionInfoService,
            ICustomSettingsService customSettingsService)
        {
            _gpuService = gpuService ?? throw new ArgumentNullException(nameof(gpuService));
            _detectedSettingsService = detectedSettingsService ?? throw new ArgumentNullException(nameof(detectedSettingsService));
            _statisticsService = statisticsService ?? throw new ArgumentNullException(nameof(statisticsService));
            _sessionInfoService = sessionInfoService ?? throw new ArgumentNullException(nameof(sessionInfoService));
            _customSettingsService = customSettingsService ?? throw new ArgumentNullException(nameof(customSettingsService));
        }

        public async Task<Models.SystemInformation> GetSystemInformationAsync()
        {
            return await Task.Run(() =>
            {
                var systemInfo = new Models.SystemInformation();

                // GPU Information
                var (resolution, dpiScale) = _gpuService.GetMainDisplayInfo();
                var (sessionType, gpuType, encoderType, hwEncode) = _gpuService.GetGraphicsProfileDetails();
                
                systemInfo.GpuInformation.Resolution = resolution;
                systemInfo.GpuInformation.DpiScale = dpiScale;
                systemInfo.GpuInformation.SessionType = sessionType;
                systemInfo.GpuInformation.GpuType = gpuType;
                systemInfo.GpuInformation.EncoderType = encoderType;
                systemInfo.GpuInformation.HardwareEncoding = hwEncode == "Yes";

                // Detected Settings
                var (width, height, refreshRateValue, scalingFactor) = _detectedSettingsService.GetDisplayResolutionAndRefreshRate();
                systemInfo.DetectedSettings.Width = width;
                systemInfo.DetectedSettings.Height = height;
                systemInfo.DetectedSettings.RefreshRate = refreshRateValue;
                systemInfo.DetectedSettings.ScalingFactor = scalingFactor;
                systemInfo.DetectedSettings.VisualQuality = _detectedSettingsService.GetVisualQuality();
                systemInfo.DetectedSettings.MaxFps = _detectedSettingsService.GetMaxFPS();
                systemInfo.DetectedSettings.HardwareEncodingSupported = _detectedSettingsService.IsHardwareEncodingSupported();
                systemInfo.DetectedSettings.EncoderType = _detectedSettingsService.GetEncoderType();

                // Session Info
                var sessionStats = _sessionInfoService.GetRdpStatistics();
                systemInfo.SessionInfo.SessionId = sessionStats.SessionId;
                systemInfo.SessionInfo.ClientName = sessionStats.ClientName ?? "N/A";
                systemInfo.SessionInfo.ProtocolVersion = sessionStats.ProtocolVersion ?? "N/A";

                // Custom Settings
                var customSettings = _customSettingsService.LoadCustomSettings("Resources/custom_registry_settings.json");
                if (customSettings != null)
                {
                    systemInfo.CustomSettings = customSettings;
                }

                return systemInfo;
            });
        }

        public async Task RefreshRealTimeStatisticsAsync(Models.SystemInformation systemInfo)
        {
            await Task.Run(() =>
            {
                systemInfo.RealTimeStatistics.EncoderFramesDropped = _statisticsService.GetEncoderFramesDropped();
                systemInfo.RealTimeStatistics.InputFramesPerSecond = _statisticsService.GetInputFramesPerSecond();
            });
        }
    }
}
