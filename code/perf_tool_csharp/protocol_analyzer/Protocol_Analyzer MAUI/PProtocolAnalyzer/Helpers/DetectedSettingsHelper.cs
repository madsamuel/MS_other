using System;
using System.Collections.Generic;
using System.Linq;
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
        /// Gets display resolution and refresh rate using existing DisplayInfoHelper.
        /// Returns (width, height, refreshRate, scalingFactor). Keeps previous behavior.
        /// </summary>
        public static (int width, int height, int refreshRate, float scalingFactor) GetDisplayResolutionAndRefreshRate()
        {
            try
            {
                var (widthDouble, heightDouble) = DisplayInfoHelper.GetDisplayResolution();
                var refreshRateDouble = DisplayInfoHelper.GetDisplayRefreshRate();
                var scalingFactorDouble = DisplayInfoHelper.GetScalingFactor();

                return ((int)widthDouble, (int)heightDouble, (int)Math.Round(refreshRateDouble), (float)scalingFactorDouble);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetDisplayResolutionAndRefreshRate - {ex.Message}");
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
                // Prefer runtime display info
                var (w, h, _, _) = GetDisplayResolutionAndRefreshRate();
                if (w > 0 && h > 0)
                {
                    if (h >= 2160 || w >= 3840) return "High";
                    if (h >= 1080 || w >= 1920) return "Medium";
                    return "Low";
                }

                // Fallback to Win32 DEVMODE
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

                return "Medium";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetVisualQuality - {ex.Message}");
                return "Unknown";
            }
        }

        /// <summary>
        /// Gets maximum FPS setting based on display refresh rate - Enhanced dynamic version
        /// </summary>
        public static int GetMaxFPS()
        {
            // 1) Prefer runtime API
            try
            {
                var runtimeRefresh = DisplayInfoHelper.GetDisplayRefreshRate();
                if (runtimeRefresh > 0)
                    return Math.Min((int)Math.Round(runtimeRefresh), 120);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetMaxFPS - DeviceDisplay read failed: {ex.Message}");
            }

            // 2) Win32 DEVMODE
            try
            {
                var winApiRefresh = GetRefreshRate();
                if (winApiRefresh > 0)
                    return Math.Min(winApiRefresh, 120);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetMaxFPS - GetRefreshRate failed: {ex.Message}");
            }

            // 3) WMI fallback
            try
            {
                foreach (var val in QueryWmiProperty("SELECT CurrentRefreshRate FROM Win32_VideoController", "CurrentRefreshRate"))
                {
                    if (int.TryParse(val, out var rr))
                        return Math.Min(rr, 120);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetMaxFPS - WMI refresh failed: {ex.Message}");
            }

            return 60;
        }

        /// <summary>
        /// Checks if hardware encoding is supported - Enhanced dynamic version
        /// </summary>
        public static bool IsHardwareEncodingSupported()
        {
            try
            {
                foreach (var vp in QueryWmiProperty("SELECT VideoProcessor FROM Win32_VideoController", "VideoProcessor"))
                {
                    var proc = (vp ?? string.Empty).ToLowerInvariant();
                    if (proc.Contains("nvidia") || proc.Contains("amd") || proc.Contains("intel"))
                        return true;
                }

                // Fallback: large adapter RAM often indicates modern GPUs
                foreach (var ram in QueryWmiProperty("SELECT AdapterRAM FROM Win32_VideoController", "AdapterRAM"))
                {
                    if (long.TryParse(ram, out var adapterRam) && adapterRam >= 1073741824L)
                        return true;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:IsHardwareEncodingSupported - {ex.Message}");
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
                foreach (var ram in QueryWmiProperty("SELECT AdapterRAM FROM Win32_VideoController", "AdapterRAM"))
                {
                    if (long.TryParse(ram, out var adapterRam) && adapterRam >= 1073741824L)
                        return "H265 (Hardware)";
                }
                return "H265 (Software)";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:GetEncoderType - {ex.Message}");
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

        /// <summary>
        /// Helper to query WMI and return string values for the requested property.
        /// Returns an empty enumeration if the query fails.
        /// </summary>
        private static IEnumerable<string> QueryWmiProperty(string wql, string propertyName)
        {
            var results = new List<string>();
            try
            {
                using var searcher = new ManagementObjectSearcher(wql);
                foreach (ManagementObject obj in searcher.Get())
                {
                    if (obj[propertyName] is not null)
                    {
                        results.Add(obj[propertyName].ToString() ?? string.Empty);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"DetectedSettingsHelper:QueryWmiProperty({propertyName}) - {ex.Message}");
            }

            return results;
        }
    }
}
