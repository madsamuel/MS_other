using System;
using System.Runtime.InteropServices;

namespace PProtocolAnalyzer.Helpers
{
    public static class GpuInformationHelper
    {
        [DllImport("gdi32.dll")]
        private static extern IntPtr CreateDC(string lpszDriver, string lpszDevice, string lpszOutput, IntPtr lpInitData);

        [DllImport("gdi32.dll")]
        private static extern bool DeleteDC(IntPtr hdc);

        [DllImport("gdi32.dll")]
        private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

        [DllImport("user32.dll")]
        private static extern IntPtr GetDC(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        private const int HORZRES = 8;
        private const int VERTRES = 10;
        private const int LOGPIXELSX = 88;

        /// <summary>
        /// Gets main display resolution and DPI scale similar to WinForms GPUInformation.GetMainDisplayInfo()
        /// </summary>
        public static (string resolution, string dpiScale) GetMainDisplayInfo()
        {
            try
            {
                IntPtr hdc = GetDC(IntPtr.Zero);
                if (hdc != IntPtr.Zero)
                {
                    int displayWidth = GetDeviceCaps(hdc, HORZRES);
                    int displayHeight = GetDeviceCaps(hdc, VERTRES);
                    int dpi = GetDeviceCaps(hdc, LOGPIXELSX);
                    ReleaseDC(IntPtr.Zero, hdc);

                    float dpiScale = dpi / 96f;
                    return ($"{displayWidth}x{displayHeight}", $"{dpiScale * 100:F0}%");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting display info: {ex.Message}");
            }

            // Fallback to DisplayInfoHelper for resolution
            var (width, height) = DisplayInfoHelper.GetDisplayResolution();
            var scalingFactor = DisplayInfoHelper.GetScalingFactor();
            return ($"{width}x{height}", $"{scalingFactor * 100:F0}%");
        }

        /// <summary>
        /// Gets graphics profile details - simplified version for MAUI
        /// </summary>
        public static (string sessionType, string gpuType, string encoderType, string hwEncode) GetGraphicsProfileDetails()
        {
            try
            {
                // For MAUI, we'll provide basic detection
                string sessionType = "Local Session"; // Default for desktop apps
                string gpuType = "iGPU"; // Could be enhanced with WMI queries
                string encoderType = "H265 (Hardware)"; // Default assumption
                string hwEncode = "Yes"; // Default assumption

                // TODO: Could be enhanced with System.Management for more detailed GPU detection
                // This would require adding System.Management NuGet package

                return (sessionType, gpuType, encoderType, hwEncode);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting graphics profile: {ex.Message}");
                return ("Unknown", "Unknown", "Unknown", "Unknown");
            }
        }
    }
}
