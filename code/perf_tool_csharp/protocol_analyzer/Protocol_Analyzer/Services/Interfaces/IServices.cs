using System.Drawing;

namespace Protocol_Analyzer.Services.Interfaces
{
    public interface IGpuInformationService
    {
        (Size resolution, float dpiScale) GetMainDisplayInfo();
        (string sessionType, string gpuType, string encoderType, string hwEncode) GetGraphicsProfileDetails();
    }

    public interface IDetectedSettingsService
    {
        (int width, int height, int refreshRateValue, float scalingFactor) GetDisplayResolutionAndRefreshRate();
        string GetVisualQuality();
        int GetMaxFPS();
        bool IsHardwareEncodingSupported();
        string GetEncoderType();
    }

    public interface IRealTimeStatisticsService
    {
        int GetEncoderFramesDropped();
        int GetInputFramesPerSecond();
    }

    public interface ISessionInfoService
    {
        RdpStatsApp.RdpNative.RdpStatistics GetRdpStatistics();
    }

    public interface ICustomSettingsService
    {
        List<CustomRegistrySetting>? LoadCustomSettings(string path);
        string GetRegistryDisplay(CustomRegistrySetting setting);
    }

    public interface ISystemInformationService
    {
        Task<Models.SystemInformation> GetSystemInformationAsync();
        Task RefreshRealTimeStatisticsAsync(Models.SystemInformation systemInfo);
    }

    public interface ITrayIconService
    {
        void Initialize(Form parentForm);
        void Show();
        void Hide();
        void Dispose();
    }

    public interface IResourceService
    {
        Icon? LoadIcon(string path);
        T? LoadJsonResource<T>(string path) where T : class;
    }
}
