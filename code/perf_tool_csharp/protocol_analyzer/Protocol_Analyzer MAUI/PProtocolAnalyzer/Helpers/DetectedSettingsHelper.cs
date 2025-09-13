using System;
using System.Management;
using System.Runtime.InteropServices;

namespace PProtocolAnalyzer.Helpers
{
    public static class DetectedSettingsHelper
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
        public struct DEVMODE
        {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmDeviceName;
            public ushort dmSpecVersion;
            public ushort dmDriverVersion;
            public ushort dmSize;
            public ushort dmDriverExtra;
            public uint dmFields;
            public int dmPositionX;
            public int dmPositionY;
            public uint dmDisplayOrientation;
            public uint dmDisplayFixedOutput;
            public short dmColor;
            public short dmDuplex;
            public short dmYResolution;
            public short dmTTOption;
            public short dmCollate;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmFormName;
            public ushort dmLogPixels;
            public uint dmBitsPerPel;
            public uint dmPelsWidth;
            public uint dmPelsHeight;
            public uint dmDisplayFlags;
            public uint dmDisplayFrequency;
            public uint dmICMMethod;
            public uint dmICMIntent;
            public uint dmMediaType;
            public uint dmDitherType;
            public uint dmReserved1;
            public uint dmReserved2;
            public uint dmPanningWidth;
            public uint dmPanningHeight;
        }

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        public static extern bool EnumDisplaySettings(string? deviceName, int modeNum, ref DEVMODE devMode);
        [DllImport("user32.dll")]
        public static extern bool SetProcessDPIAware();
        [DllImport("gdi32.dll")]
        public static extern int GetDeviceCaps(IntPtr hdc, int nIndex);
        public const int ENUM_CURRENT_SETTINGS = -1;
        public const int LOGPIXELSX = 88;
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
        /// Gets visual quality setting based on display resolution - Enhanced dynamic version
        /// </summary>
        public static string GetVisualQuality()
        {
            try
            {
                DEVMODE devMode = new DEVMODE();
                devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));
                
                if (EnumDisplaySettings(string.Empty, ENUM_CURRENT_SETTINGS, ref devMode))
                {
                    int width = (int)devMode.dmPelsWidth;
                    int height = (int)devMode.dmPelsHeight;
                    if (height >= 2160 || width >= 3840) return "High";
                    if (height >= 1080 || width >= 1920) return "Medium";
                    return "Low";
                }
                return "Medium"; // fallback if API fails
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting visual quality: {ex.Message}");
                return "Unknown";
            }
        }

        /// <summary>
        /// Gets maximum FPS setting based on display refresh rate - Enhanced dynamic version
        /// </summary>
        public static int GetMaxFPS()
        {
            try
            {
                // 1) Prefer platform/runtime API that MAUI exposes (DeviceDisplay)
                try
                {
                    var runtimeRefresh = DisplayInfoHelper.GetDisplayRefreshRate();
                    if (runtimeRefresh > 0)
                    {
                        return Math.Min((int)Math.Round(runtimeRefresh), 120);
                    }
                }
                catch (Exception rex)
                {
                    System.Diagnostics.Debug.WriteLine($"Info: DisplayInfoHelper refresh read failed: {rex.Message}");
                }

                // 2) Try Win32 EnumDisplaySettings fallback which reads DEVMODE.dmDisplayFrequency
                try
                {
                    var winApiRefresh = GetRefreshRate();
                    if (winApiRefresh > 0)
                        return Math.Min(winApiRefresh, 120);
                }
                catch (Exception dex)
                {
                    System.Diagnostics.Debug.WriteLine($"Info: GetRefreshRate() failed: {dex.Message}");
                }

                // 3) Last resort: try WMI (may throw or be slow) - keep as fallback only
                try
                {
                    using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
                    {
                        foreach (ManagementObject obj in searcher.Get())
                        {
                            if (obj["CurrentRefreshRate"] is not null)
                            {
                                int refreshRate = 60;
                                var refreshRateObj = obj["CurrentRefreshRate"];
                                if (refreshRateObj != null && int.TryParse(refreshRateObj.ToString() ?? "60", out int rr))
                                    refreshRate = rr;
                                // Cap at 120 FPS as a reasonable maximum
                                return Math.Min(refreshRate, 120);
                            }
                        }
                    }
                }
                catch (Exception wex)
                {
                    System.Diagnostics.Debug.WriteLine($"Info: WMI refresh read failed: {wex.Message}");
                }

                // Final sensible default
                return 60;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting max FPS: {ex.Message}");
                return 60;
            }
        }

        /// <summary>
        /// Checks if hardware encoding is supported - Enhanced dynamic version
        /// </summary>
        public static bool IsHardwareEncodingSupported()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        if (obj["VideoProcessor"] is not null)
                        {
                            var videoProcessorObj = obj["VideoProcessor"];
                            string processor = videoProcessorObj != null ? videoProcessorObj.ToString() ?? string.Empty : string.Empty;
                            processor = processor.ToLowerInvariant();
                            // Check for common GPU vendors that support hardware encoding
                            if (processor.Contains("nvidia") || processor.Contains("amd") || processor.Contains("intel"))
                            {
                                return true;
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error checking hardware encoding: {ex.Message}");
            }
            return false;
        }

        /// <summary>
        /// Gets encoder type based on GPU capabilities - Enhanced dynamic version
        /// </summary>
        public static string GetEncoderType()
        {
            try
            {
                // Check for hardware acceleration support using WMI
                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        if (obj["AdapterRAM"] is not null)
                        {
                            // Modern GPUs with significant VRAM support hardware encoding
                            long adapterRAM = 0L;
                            var adapterRamObj = obj["AdapterRAM"];
                            if (adapterRamObj != null && long.TryParse(adapterRamObj.ToString() ?? "0", out long ram))
                                adapterRAM = ram;
                            if (adapterRAM >= 1073741824) // 1GB VRAM
                            {
                                return "H265 (Hardware)";
                            }
                        }
                    }
                }
                return "H265 (Software)";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting encoder type: {ex.Message}");
                return "Unknown";
            }
        }

        /// <summary>
        /// Gets display refresh rate using Win32 API - Enhanced dynamic version
        /// </summary>
        public static int GetRefreshRate()
        {
            try
            {
                DEVMODE devMode = new DEVMODE();
                devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));
                if (EnumDisplaySettings(string.Empty, ENUM_CURRENT_SETTINGS, ref devMode))
                {
                    return (int)devMode.dmDisplayFrequency;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting refresh rate: {ex.Message}");
            }
            return -1; // Unknown
        }
    }
}
