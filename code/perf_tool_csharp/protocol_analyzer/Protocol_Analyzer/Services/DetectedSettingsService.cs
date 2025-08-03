using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class DetectedSettingsService : IDetectedSettingsService
    {
        public (int width, int height, int refreshRateValue, float scalingFactor) GetDisplayResolutionAndRefreshRate()
        {
            return DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
        }

        public string GetVisualQuality()
        {
            return DetectedSettingsHelper.GetVisualQuality();
        }

        public int GetMaxFPS()
        {
            return DetectedSettingsHelper.GetMaxFPS();
        }

        public bool IsHardwareEncodingSupported()
        {
            return DetectedSettingsHelper.IsHardwareEncodingSupported();
        }

        public string GetEncoderType()
        {
            return DetectedSettingsHelper.GetEncoderType();
        }
    }
}
