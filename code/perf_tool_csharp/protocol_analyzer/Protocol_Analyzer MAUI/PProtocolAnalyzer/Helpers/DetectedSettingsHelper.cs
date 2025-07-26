using System;

namespace PProtocolAnalyzer.Helpers
{
    public static class DetectedSettingsHelper
    {
        /// <summary>
        /// Gets display resolution and refresh rate using existing DisplayInfoHelper
        /// Preserves the working functionality while providing structured access
        /// </summary>
        public static (int width, int height, int refreshRate, float scalingFactor) GetDisplayResolutionAndRefreshRate()
        {
            try
            {
                // Use existing working DisplayInfoHelper methods
                var (widthDouble, heightDouble) = DisplayInfoHelper.GetDisplayResolution();
                var refreshRateDouble = DisplayInfoHelper.GetDisplayRefreshRate();
                var scalingFactorDouble = DisplayInfoHelper.GetScalingFactor();

                return ((int)widthDouble, (int)heightDouble, (int)refreshRateDouble, (float)scalingFactorDouble);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting display settings: {ex.Message}");
                return (0, 0, 0, 1.0f);
            }
        }

        /// <summary>
        /// Gets visual quality setting - simplified for MAUI
        /// </summary>
        public static string GetVisualQuality()
        {
            try
            {
                // Default quality setting - could be enhanced with registry reading
                return "Medium";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting visual quality: {ex.Message}");
                return "Unknown";
            }
        }

        /// <summary>
        /// Gets maximum FPS setting - simplified for MAUI
        /// </summary>
        public static string GetMaxFPS()
        {
            try
            {
                // Could be enhanced to read from system settings or registry
                var refreshRate = DisplayInfoHelper.GetDisplayRefreshRate();
                return (refreshRate > 0 ? ((int)refreshRate - 1).ToString() : "59");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting max FPS: {ex.Message}");
                return "Unknown";
            }
        }

        /// <summary>
        /// Checks if hardware encoding is supported - simplified for MAUI
        /// </summary>
        public static bool IsHardwareEncodingSupported()
        {
            try
            {
                // Default assumption - could be enhanced with actual hardware detection
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error checking hardware encoding: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Gets encoder type - simplified for MAUI
        /// </summary>
        public static string GetEncoderType()
        {
            try
            {
                // Default encoder type - could be enhanced with actual detection
                return "H265 (Hardware)";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting encoder type: {ex.Message}");
                return "Unknown";
            }
        }
    }
}
