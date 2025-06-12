using System;
using System.Drawing;
using System.Windows.Forms;
using System.Management;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        private Label statsLabel = null!;
        private Label fpsLabel = null!;
        private System.Windows.Forms.Timer statsTimer = null!;

        public Form1()
        {
            BuildUI();
        }
    
        private void BuildUI()
        {
            this.Text = "Session Perf";
            this.Size = new Size(800, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // GPU Information section
            var gpuInfoGroup = CreateGpuInfoGroup(new Point(20, 20));
            this.Controls.Add(gpuInfoGroup);

            // Detected Settings section - match width and padding
            int groupWidth = gpuInfoGroup.Width > 0 ? gpuInfoGroup.Width : 370;
            var detectedSettingsGroup = CreateDetectedSettingsGroup(new Point(20 + groupWidth + 20, 20));
            detectedSettingsGroup.Size = new Size(groupWidth, detectedSettingsGroup.Height);
            this.Controls.Add(detectedSettingsGroup);

            // Real-Time Advanced Statistics section
            var realTimeStatsGroup = CreateRealTimeStatsGroup(new Point(20, 300));
            this.Controls.Add(realTimeStatsGroup);

            // Start polling for encoder frames dropped every 15 seconds
            statsTimer = new System.Windows.Forms.Timer();
            statsTimer.Interval = 15000; // 15 seconds
            statsTimer.Tick += PollEncoderFramesDropped;
            statsTimer.Start();
        }

        private GroupBox CreateGpuInfoGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "GPU Information",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Location = location
            };

            var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
            var resolutionLabel = CreateLabel("Main Display Resolution:", new Point(15, 30));
            var resolutionValue = CreateBoldLabel($"{resolution.Width}x{resolution.Height}", new Point(150, 30));
            var dpiLabel = CreateLabel("DPI Scale:", new Point(15, 55));
            var dpiValue = CreateBoldLabel($"{dpiScale * 100:F0} %", new Point(150, 55));

            var (sessionType, gpuType, encoderType, hwEncode) = GraphicsProfileHelper.GetGraphicsProfileDetails();
            var sessionTypeLabel = CreateLabel("Session Type:", new Point(15, 80));
            var sessionTypeValue = CreateBoldLabel(sessionType, new Point(150, 80));
            var gpuTypeLabel = CreateLabel("GPU Type:", new Point(15, 105));
            var gpuTypeValue = CreateBoldLabel(gpuType, new Point(150, 105));
            var encoderTypeLabel = CreateLabel("Encoding:", new Point(15, 130));
            var encoderTypeValue = CreateBoldLabel(encoderType, new Point(150, 130));
            var hwEncodeLabel = CreateLabel("HW Encode:", new Point(15, 155));
            var hwEncodeValue = CreateBoldLabel(hwEncode, new Point(150, 155));

            group.Controls.Add(resolutionLabel);
            group.Controls.Add(resolutionValue);
            group.Controls.Add(dpiLabel);
            group.Controls.Add(dpiValue);
            group.Controls.Add(sessionTypeLabel);
            group.Controls.Add(sessionTypeValue);
            group.Controls.Add(gpuTypeLabel);
            group.Controls.Add(gpuTypeValue);
            group.Controls.Add(encoderTypeLabel);
            group.Controls.Add(encoderTypeValue);
            group.Controls.Add(hwEncodeLabel);
            group.Controls.Add(hwEncodeValue);
            return group;
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

            statsLabel = new Label
            {
                Text = "Encoder Frames Dropped: (waiting for data)",
                Location = new Point(15, 30),
                AutoSize = true,
                Font = new Font("Segoe UI", 9)
            };

            fpsLabel = new Label
            {
                Text = "Input Frames Per Second: (waiting for data)",
                Location = new Point(15, 55),
                AutoSize = true,
                Font = new Font("Segoe UI", 9)
            };

            group.Controls.Add(statsLabel!);
            group.Controls.Add(fpsLabel!);
            return group;
        }

        private void PollEncoderFramesDropped(object? sender, EventArgs e)
        {
            int framesDropped = RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
            statsLabel.Text = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString() : "Unavailable")}";
            int inputFps = RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
            fpsLabel.Text = $"Input Frames Per Second: {(inputFps >= 0 ? inputFps.ToString() : "Unavailable")}";
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
            statsTimer?.Stop();
        }
    }
}
