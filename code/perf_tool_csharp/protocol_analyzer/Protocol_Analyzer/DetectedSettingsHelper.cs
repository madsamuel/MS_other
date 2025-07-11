using System;
using System.Management;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public static class DetectedSettingsHelper
    {
        public static string GetVisualQuality()
        {
            DEVMODE devMode = new DEVMODE();
            devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));
            // Use EnumDisplaySettings to get the current display settings
            
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

        public static int GetMaxFPS()
        {
            // Get display refresh rate
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
            return 60; // Default to 60 FPS if cannot determine
        }

        public static string GetEncoderType()
        {
            // Check for hardware acceleration support
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
            catch
            {
                // If we can't determine, assume software encoding
            }
            return false;
        }

        public static int GetRefreshRate()
        {
            // Use Win32 API to get display refresh rate for the main display
            try
            {
                DEVMODE devMode = new DEVMODE();
                devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));
                if (EnumDisplaySettings(string.Empty, ENUM_CURRENT_SETTINGS, ref devMode))
                {
                    return (int)devMode.dmDisplayFrequency;
                }
            }
            catch { }
            return -1; // Unknown
        }

        public static (int width, int height, int refreshRate, float scalingFactor) GetDisplayResolutionAndRefreshRate()
        {
            try
            {
                // Ensure process is DPI aware
                SetProcessDPIAware();

                // 1) Get primary screen resolution
                int width = -1, height = -1;
                var screen = System.Windows.Forms.Screen.PrimaryScreen;
                if (screen != null)
                {
                    width = screen.Bounds.Width;
                    height = screen.Bounds.Height;
                }

                // 2) Get scaling factor (DPI awareness)
                float scalingFactor = 1.0f;
                try
                {
                    using (var g = System.Drawing.Graphics.FromHwnd(IntPtr.Zero))
                    {
                        IntPtr hdc = g.GetHdc();
                        int dpiX = GetDeviceCaps(hdc, LOGPIXELSX); // Get horizontal DPI
                        if (dpiX > 0)
                        {
                            scalingFactor = dpiX / 96.0f; // 96 DPI is 100% scaling
                        }
                        g.ReleaseHdc(hdc);
                    }
                }
                catch { scalingFactor = 1.0f; }

                // 3) Get refresh rate using EnumDisplaySettings
                int refreshRate = -1;
                DEVMODE devMode = new DEVMODE();
                devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));
                bool success = EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref devMode);
                if (success && devMode.dmDisplayFrequency > 0)
                {
                    refreshRate = (int)devMode.dmDisplayFrequency;
                }
                return (width, height, refreshRate, scalingFactor);
            }
            catch { }
            return (-1, -1, -1, 1.0f);
        }

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
    }

    // Place this outside DetectedSettingsHelper
    public static class DisplayRefreshRateUtility
    {
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        public struct DEVMODE
        {
            private const int CCHDEVICENAME = 32;
            private const int CCHFORMNAME = 32;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = CCHDEVICENAME)]
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
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = CCHFORMNAME)]
            public string dmFormName;
            public ushort dmLogPixels;
            public uint dmBitsPerPel;
            public uint dmPelsWidth;
            public uint dmPelsHeight;
            public uint dmDisplayFlags;
            public uint dmDisplayFrequency;
            // Other fields omitted for brevity
        }

        [DllImport("user32.dll")]
        public static extern bool EnumDisplaySettings(string? deviceName, int modeNum, ref DEVMODE devMode);
        public const int ENUM_CURRENT_SETTINGS = -1;
    }
}
