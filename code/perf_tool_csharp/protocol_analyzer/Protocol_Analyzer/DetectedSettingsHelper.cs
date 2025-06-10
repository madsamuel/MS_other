using System;
using System.Management;

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
                    if (obj["PelsHeight"] != null && obj["PelsWidth"] != null)
                    {
                        int height = Convert.ToInt32(obj["PelsHeight"]);
                        int width = Convert.ToInt32(obj["PelsWidth"]);
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
                    if (obj["CurrentRefreshRate"] != null)
                    {
                        int refreshRate = Convert.ToInt32(obj["CurrentRefreshRate"]);
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
                    if (obj["AdapterRAM"] != null)
                    {
                        // Modern GPUs with significant VRAM support hardware encoding
                        long adapterRAM = Convert.ToInt64(obj["AdapterRAM"]);
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
                        if (obj["VideoProcessor"] != null)
                        {
                            string processor = obj["VideoProcessor"].ToString().ToLower();
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
    }
}
