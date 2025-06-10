using System;
using System.Management;

namespace Protocol_Analyzer
{
    public static class RealTimeAdvancedStatistics
    {
        public static int GetEncoderFramesDroppedFromWMI()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("root\\CIMV2", "SELECT * FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        foreach (var prop in obj.Properties)
                        {
                            if (prop.Name.ToLower().Contains("dropped") && prop.Value != null)
                            {
                                if (int.TryParse(prop.Value.ToString(), out int dropped))
                                    return dropped;
                            }
                        }
                    }
                }
            }
            catch
            {
                return -1;
            }
            return -1;
        }

        public static int GetInputFramesPerSecondFromWMI()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("root\\CIMV2", "SELECT * FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        foreach (var prop in obj.Properties)
                        {
                            if ((prop.Name.ToLower().Contains("inputframes") || prop.Name.ToLower().Contains("fps")) && prop.Value != null)
                            {
                                if (int.TryParse(prop.Value.ToString(), out int fps))
                                    return fps;
                            }
                        }
                    }
                }
            }
            catch
            {
                return -1;
            }
            return -1;
        }
    }
}
