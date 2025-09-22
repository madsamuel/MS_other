using System;
using Microsoft.Extensions.Logging;
using System.Runtime.InteropServices;
using System.Management;
using System.Linq;

namespace PProtocolAnalyzer.Helpers
{
    public static class GPUInformation
    {
        [DllImport("user32.dll")]
        private static extern IntPtr GetDC(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        [DllImport("gdi32.dll")]
        private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

        private const int HORZRES = 8;
        private const int VERTRES = 10;
        private const int LOGPIXELSX = 88;

        /// <summary>
        /// Gets main display resolution and DPI scale - Enhanced version that gets data from GPU
        /// </summary>
        public static ((int Width, int Height) resolution, float dpiScale) GetMainDisplayInfo()
        {
            try
            {
                // First try to get resolution from GPU WMI (onboard GPU data)
                var gpuResolution = GetGpuDisplayResolution();
                if (gpuResolution.Width > 0 && gpuResolution.Height > 0)
                {
                    // Get DPI scale from Win32 API
                    float dpiScale = GetDpiScale();
                    return (gpuResolution, dpiScale);
                }
                }
                catch (Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                    try { lg?.LogError(ex, $"Error getting GPU display resolution: {ex.Message}"); } catch { }
                }

            try
            {
                // Fallback to Win32 API (similar to WinForms Graphics.FromHwnd approach)
                IntPtr hdc = GetDC(IntPtr.Zero);
                if (hdc != IntPtr.Zero)
                {
                    int width = GetDeviceCaps(hdc, HORZRES);
                    int height = GetDeviceCaps(hdc, VERTRES);
                    int dpi = GetDeviceCaps(hdc, LOGPIXELSX);
                    ReleaseDC(IntPtr.Zero, hdc);

                    float dpiScale = dpi / 96f;
                    return ((width, height), dpiScale);
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error getting display info via Win32: {ex.Message}"); } catch { }
            }

            // Final fallback to MAUI DeviceDisplay
            try
            {
                var screen = Microsoft.Maui.Devices.DeviceDisplay.MainDisplayInfo;
                var resolution = ((int)screen.Width, (int)screen.Height);
                var dpiScale = (float)screen.Density;
                return (resolution, dpiScale);
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error getting display info via MAUI: {ex.Message}"); } catch { }
                // Return "Unknown" instead of misleading hardcoded values
                return ((0, 0), 0.0f);
            }
        }

        /// <summary>
        /// Gets graphics profile details - Enhanced dynamic version with WMI queries
        /// Similar to WinForms GraphicsProfileHelper.GetGraphicsProfileDetails()
        /// </summary>
        public static (string sessionType, string gpuType, string encoderType, string hwEncode) GetGraphicsProfileDetails()
        {
            try
            {
                // Detect session type
                string sessionType = GetSessionType();
                
                // Dynamic GPU detection using WMI
                string gpuType = DetectGpuType();
                
                // Dynamic encoding detection
                string encoderType = DetectEncoderType();
                
                // Dynamic hardware encode detection
                string hwEncode = DetectHardwareEncoding();

                return (sessionType, gpuType, encoderType, hwEncode);
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error getting graphics profile details: {ex.Message}"); } catch { }
                return ("Unknown", "Unknown", "Unknown", "Unknown");
            }
        }

        /// <summary>
        /// Gets GPU display resolution from WMI (onboard GPU data)
        /// </summary>
        private static (int Width, int Height) GetGpuDisplayResolution()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController WHERE PNPDeviceID LIKE 'PCI%'"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        var currentHorizontalResolution = obj["CurrentHorizontalResolution"];
                        var currentVerticalResolution = obj["CurrentVerticalResolution"];
                        
                        if (currentHorizontalResolution != null && currentVerticalResolution != null)
                        {
                            int width = Convert.ToInt32(currentHorizontalResolution);
                            int height = Convert.ToInt32(currentVerticalResolution);
                            
                            if (width > 0 && height > 0)
                            {
                                return (width, height);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error getting GPU resolution via WMI: {ex.Message}"); } catch { }
            }
            
            return (0, 0); // Return 0,0 if failed
        }

        /// <summary>
        /// Gets DPI scale using Win32 API
        /// </summary>
        private static float GetDpiScale()
        {
            try
            {
                IntPtr hdc = GetDC(IntPtr.Zero);
                if (hdc != IntPtr.Zero)
                {
                    int dpi = GetDeviceCaps(hdc, LOGPIXELSX);
                    ReleaseDC(IntPtr.Zero, hdc);
                    return dpi / 96f;
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error getting DPI scale: {ex.Message}"); } catch { }
            }
            
            return 1.0f; // Default scale
        }

        private static string GetSessionType()
        {
            try
            {
                // Check if running in RDP session
                var sessionName = Environment.GetEnvironmentVariable("SESSIONNAME");
                if (!string.IsNullOrEmpty(sessionName) && sessionName.StartsWith("RDP-"))
                {
                    return "Remote Session";
                }
                return "Local Session";
            }
            catch
            {
                return "Local Session";
            }
        }

        /// <summary>
        /// Detects GPU type using WMI queries - Dynamic detection
        /// </summary>
        private static string DetectGpuType()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Name FROM Win32_VideoController WHERE PNPDeviceID LIKE 'PCI%'"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        string? gpuName = obj["Name"]?.ToString()?.ToUpper();
                        if (!string.IsNullOrEmpty(gpuName))
                        {
                            if (gpuName.Contains("NVIDIA") || gpuName.Contains("GEFORCE") || gpuName.Contains("QUADRO"))
                                return "NVIDIA dGPU";
                            else if (gpuName.Contains("AMD") || gpuName.Contains("RADEON"))
                                return "AMD dGPU";
                            else if (gpuName.Contains("INTEL") || gpuName.Contains("HD GRAPHICS") || gpuName.Contains("UHD GRAPHICS") || gpuName.Contains("IRIS"))
                                return "iGPU";
                            else
                                return "dGPU"; // Generic discrete GPU
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error detecting GPU type: {ex.Message}"); } catch { }
            }
            
            return "iGPU"; // Default fallback
        }

        /// <summary>
        /// Detects encoder type based on GPU capabilities
        /// </summary>
        private static string DetectEncoderType()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Name FROM Win32_VideoController WHERE PNPDeviceID LIKE 'PCI%'"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        string? gpuName = obj["Name"]?.ToString()?.ToUpper();
                        if (!string.IsNullOrEmpty(gpuName))
                        {
                            // Modern GPUs typically support H265 hardware encoding
                            if (gpuName.Contains("NVIDIA") || gpuName.Contains("AMD") || 
                                gpuName.Contains("INTEL") || gpuName.Contains("UHD") || gpuName.Contains("HD GRAPHICS"))
                            {
                                return "H265 (Hardware)";
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error detecting encoder type: {ex.Message}"); } catch { }
            }
            
            return "H264 (Software)"; // Fallback
        }

        /// <summary>
        /// Detects if hardware encoding is available
        /// </summary>
        private static string DetectHardwareEncoding()
        {
            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Name, AdapterRAM FROM Win32_VideoController WHERE PNPDeviceID LIKE 'PCI%'"))
                {
                    foreach (ManagementObject obj in searcher.Get())
                    {
                        string? gpuName = obj["Name"]?.ToString()?.ToUpper();
                        var adapterRAM = obj["AdapterRAM"];
                        
                        if (!string.IsNullOrEmpty(gpuName))
                        {
                            // Check if it's a modern GPU with sufficient memory for hardware encoding
                            if ((gpuName.Contains("NVIDIA") || gpuName.Contains("AMD") || 
                                 gpuName.Contains("INTEL") || gpuName.Contains("UHD") || gpuName.Contains("HD GRAPHICS")) &&
                                adapterRAM != null && Convert.ToUInt32(adapterRAM) > 1000000000) // > 1GB
                            {
                                return "Yes";
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(GPUInformation));
                try { lg?.LogWarning(ex, $"Error detecting hardware encoding: {ex.Message}"); } catch { }
            }
            
            return "No"; // Conservative fallback
        }
    }
}
