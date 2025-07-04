using System;
using System.Management;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public static class DetectedSettingsHelper
    {
        public static string GetVisualQuality()
        {
            // Get system DPI to determine visual quality
            using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_DisplayConfiguration"))
            {
                foreach (ManagementObject obj in searcher.Get())
                {
                    if (obj["PelsHeight"] is not null && obj["PelsWidth"] is not null)
                    {
                        int height = 0;
                        int width = 0;
                        var pelsHeightObj = obj["PelsHeight"];
                        var pelsWidthObj = obj["PelsWidth"];
                        if (pelsHeightObj != null && int.TryParse(pelsHeightObj.ToString() ?? "0", out int h))
                            height = h;
                        if (pelsWidthObj != null && int.TryParse(pelsWidthObj.ToString() ?? "0", out int w))
                            width = w;
                        if (height >= 2160 || width >= 3840) return "High";
                        if (height >= 1080 || width >= 1920) return "Medium";
                        return "Low";
                    }
                }
            }
            return "Medium";
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

        public static (int width, int height, int refreshRate) GetDisplayResolutionAndRefreshRate()
        {
            try
            {
                DisplayRefreshRateUtility.DEVMODE devMode = new DisplayRefreshRateUtility.DEVMODE
                {
                    dmDeviceName = string.Empty,
                    dmFormName = string.Empty
                };
                devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DisplayRefreshRateUtility.DEVMODE));
                if (DisplayRefreshRateUtility.EnumDisplaySettings(string.Empty, DisplayRefreshRateUtility.ENUM_CURRENT_SETTINGS, ref devMode))
                {
                    return ((int)devMode.dmPelsWidth, (int)devMode.dmPelsHeight, (int)devMode.dmDisplayFrequency);
                }
            }
            catch { }
            return (-1, -1, -1);
        }

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
        public static extern bool EnumDisplaySettings(string deviceName, int modeNum, ref DEVMODE devMode);
        const int ENUM_CURRENT_SETTINGS = -1;
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
