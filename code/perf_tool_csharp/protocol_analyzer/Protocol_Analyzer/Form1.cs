using System;
using System.Drawing;
using System.Management;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            BuildUI();
        }
    
        private void BuildUI()
        {
            this.Text = "Session Perf";
            this.Size = new Size(800, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // holder for Setting    
            var detectedSettingsGroup = CreateDetectedSettingsGroup(new Point(20, 20));
            this.Controls.Add(detectedSettingsGroup);             
        }

        private GroupBox CreateDetectedSettingsGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "Detected settings",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),                
                Size = new Size(370, 150),
                Location = location
            };

            // Get visual quality based on system DPI
            var visualQualityValue = GetVisualQuality();
            var visualQuality = CreateLabel("Visual Quality:", new Point(15, 30));
            var visualQualityLabel = CreateBoldLabel(visualQualityValue, new Point(150, 30));

            // Get max FPS based on display refresh rate
            var maxFpsValue = GetMaxFPS();
            var maxFps = CreateLabel("Max Frames p/s:", new Point(15, 55));
            var maxFpsLabel = CreateBoldLabel(maxFpsValue.ToString(), new Point(150, 55));

            // Get encoder type based on system capabilities
            var encoderTypeValue = GetEncoderType();
            var encoderType = CreateLabel("Encoder type:", new Point(15, 80));
            var encoderTypeLabel = CreateBoldLabel(encoderTypeValue, new Point(150, 80));

            // Check hardware encoding capabilities
            var hwEncodeValue = IsHardwareEncodingSupported() ? "Active" : "Inactive";
            var hwEncode = CreateLabel("Hardware Encode:", new Point(15, 105));
            var hwEncodeLabel = CreateBoldLabel(hwEncodeValue, new Point(150, 105));

            group.Controls.AddRange(new Control[]
            {
                visualQuality, visualQualityLabel,
                maxFps, maxFpsLabel,
                encoderType, encoderTypeLabel,
                hwEncode, hwEncodeLabel
            });

            return group;
        }

        private string GetVisualQuality()
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

        private int GetMaxFPS()
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

        private string GetEncoderType()
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

        private bool IsHardwareEncodingSupported()
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

        private Label CreateLabel(string text, Point location)
        {
            return new Label
            {
                Text = text,
                Location = location,
                AutoSize = true,
                Font = new Font("Segoe UI", 9)
            };
        }

        private Label CreateBoldLabel(string text, Point location)
        {
            return new Label
            {
                Text = text,
                Location = location,
                AutoSize = true,
                Font = new Font("Segoe UI", 9, FontStyle.Bold)                
            };
        }

        

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
        }
    }
}
