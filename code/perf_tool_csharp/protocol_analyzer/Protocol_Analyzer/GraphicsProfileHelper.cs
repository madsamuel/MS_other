using System;
using System.Management;

namespace Protocol_Analyzer
{
    public static class GraphicsProfileHelper
    {
        public static string GetGraphicsProfile()
        {
            // Attempt to infer graphics profile based on available GPU and session info
            string profile = "Unknown";
            string encoderType = DetectedSettingsHelper.GetEncoderType();
            bool hwEncoding = DetectedSettingsHelper.IsHardwareEncodingSupported();

            // Check if running in RDP session
            bool isRemoteSession = false;
            try
            {
                isRemoteSession = SystemInformation.TerminalServerSession;
            }
            catch { }

            // Try to get GPU type (dGPU, iGPU, etc.)
            string gpuType = "Unknown";
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        string name = obj["Name"]?.ToString()?.ToLower() ?? "";
                        if (name.Contains("nvidia") || name.Contains("amd"))
                            gpuType = "dGPU";
                        else if (name.Contains("intel"))
                            gpuType = "iGPU";
                        else
                            gpuType = "Other";
                        break;
                    }
                }
            }
            catch { }

            // Compose profile string
            if (isRemoteSession)
            {
                profile = $"RDP Session\nGPU: {gpuType}\nEncoding: {encoderType}\nHW Encode: {(hwEncoding ? "Yes" : "No")}";
            }
            else
            {
                profile = $"Local Session\nGPU: {gpuType}\nEncoding: {encoderType}\nHW Encode: {(hwEncoding ? "Yes" : "No")}";
            }
            return profile;
        }

        public static (string sessionType, string gpuType, string encoderType, string hwEncode) GetGraphicsProfileDetails()
        {
            string sessionType = "Unknown";
            string encoderType = DetectedSettingsHelper.GetEncoderType();
            bool hwEncoding = DetectedSettingsHelper.IsHardwareEncodingSupported();
            string hwEncode = hwEncoding ? "Yes" : "No";

            // Check if running in RDP session
            bool isRemoteSession = false;
            try
            {
                isRemoteSession = System.Windows.Forms.SystemInformation.TerminalServerSession;
            }
            catch { }
            sessionType = isRemoteSession ? "RDP Session" : "Local Session";

            // Try to get GPU type (dGPU, iGPU, etc.)
            string gpuType = "Unknown";
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        string name = obj["Name"]?.ToString()?.ToLower() ?? "";
                        if (name.Contains("nvidia") || name.Contains("amd"))
                            gpuType = "dGPU";
                        else if (name.Contains("intel"))
                            gpuType = "iGPU";
                        else
                            gpuType = "Other";
                        break;
                    }
                }
            }
            catch { }

            return (sessionType, gpuType, encoderType, hwEncode);
        }
    }
}
