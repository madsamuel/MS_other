using System;
using System.Drawing;
using System.Windows.Forms;
using System.Management;
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

            // holder for Detected Setting    
            var detectedSettingsGroup = CreateDetectedSettingsGroup(new Point(20, 20));
            this.Controls.Add(detectedSettingsGroup);    

            // Real-Time Advanced Statistics section
            var realTimeStatsGroup = CreateRealTimeStatsGroup(new Point(20, 200));
            this.Controls.Add(realTimeStatsGroup);
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
            var visualQualityValue = DetectedSettingsHelper.GetVisualQuality();
            var visualQuality = CreateLabel("Visual Quality:", new Point(15, 30));
            var visualQualityLabel = CreateBoldLabel(visualQualityValue, new Point(150, 30));

            // Get max FPS based on display refresh rate
            var maxFpsValue = DetectedSettingsHelper.GetMaxFPS();
            var maxFps = CreateLabel("Max Frames p/s:", new Point(15, 55));
            var maxFpsLabel = CreateBoldLabel(maxFpsValue.ToString(), new Point(150, 55));

            // Get encoder type based on system capabilities
            var encoderTypeValue = DetectedSettingsHelper.GetEncoderType();
            var encoderType = CreateLabel("Encoder type:", new Point(15, 80));
            var encoderTypeLabel = CreateBoldLabel(encoderTypeValue, new Point(150, 80));

            // Check hardware encoding capabilities
            var hwEncodeValue = DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive";
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

        private GroupBox CreateRealTimeStatsGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "Real-Time Advanced Statistics",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(370, 150),
                Location = location
            };

            var statsLabel = new Label
            {
                Text = "(Real-time statistics will appear here)",
                Location = new Point(15, 30),
                AutoSize = true,
                Font = new Font("Segoe UI", 9)
            };

            group.Controls.Add(statsLabel);
            return group;
        }

        // UI helper methods
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
