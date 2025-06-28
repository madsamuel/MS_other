using System;
using System.Drawing;
using System.Windows.Forms;
using System.Management;
using System.Runtime.InteropServices;
using System.Text.Json;
using Microsoft.Win32;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        private Label statsLabel = null!;
        private Label fpsLabel = null!;
        private System.Windows.Forms.Timer statsTimer = null!;
        private NotifyIcon? trayIcon;

        private List<CustomRegistrySetting>? customSettings;

        public Form1()
        {
            this.Icon = new Icon("Resources/banana.ico");
            InitializeTrayIcon();
            customSettings = CustomSettingsHelper.LoadCustomSettings("Resources/custom_registry_settings.json");
            BuildUI();
        }

        private void InitializeTrayIcon()
        {
            trayIcon = new NotifyIcon();
            trayIcon.Icon = new Icon("Resources/banana.ico");
            trayIcon.Text = "Session Perf";
            trayIcon.Visible = true;
            // Optional: Add a context menu for exiting
            var contextMenu = new ContextMenuStrip();
            var exitItem = new ToolStripMenuItem("Exit");
            exitItem.Click += (s, e) => { this.Close(); };
            contextMenu.Items.Add(exitItem);
            trayIcon.ContextMenuStrip = contextMenu;
        }

        private void BuildUI()
        {
            this.Text = "Session Perf";
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;

            var gpuInfoGroup = CreateGpuInfoGroup(new Point(20, 20));
            this.Controls.Add(gpuInfoGroup);
            int groupWidth = gpuInfoGroup.Width > 0 ? gpuInfoGroup.Width : 370;
            var detectedSettingsGroup = CreateDetectedSettingsGroup(new Point(20 + groupWidth + 20, 20));
            detectedSettingsGroup.Size = new Size(groupWidth, detectedSettingsGroup.Height);
            this.Controls.Add(detectedSettingsGroup);
            int topRowBottom = Math.Max(
                gpuInfoGroup.Bottom,
                detectedSettingsGroup.Bottom
            );
            var realTimeStatsGroup = CreateRealTimeStatsGroup(new Point(20, topRowBottom + 10), groupWidth);
            this.Controls.Add(realTimeStatsGroup);

            // Add Session Info group below Real-Time Stats, spanning the full width
            var sessionInfoGroup = CreateSessionInfoGroup(new Point(20, realTimeStatsGroup.Bottom + 10));
            sessionInfoGroup.Size = new Size(groupWidth * 2 + 20, sessionInfoGroup.Height);
            this.Controls.Add(sessionInfoGroup);

            // Place Custom Settings under Detected Settings, matching its width
            if (customSettings != null && customSettings.Count > 0)
            {
                int customSettingsY = detectedSettingsGroup.Bottom + 10;
                var customSettingsGroup = CreateCustomSettingsGroup(new Point(detectedSettingsGroup.Left, customSettingsY));
                customSettingsGroup.Size = new Size(groupWidth, customSettingsGroup.Height);
                this.Controls.Add(customSettingsGroup);
            }

            statsTimer = new System.Windows.Forms.Timer();
            statsTimer.Interval = 15000;
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

            // Get display resolution and refresh rate
            var (width, height, refreshRateValue) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
            var resolutionLabel = CreateLabel("Display Resolution:", new Point(15, 30));
            var resolutionValue = CreateBoldLabel(width > 0 && height > 0 ? $"{width}x{height}" : "Unknown", new Point(150, 30));

            var refreshRate = CreateLabel("Display Refresh Rate:", new Point(15, 55));
            var refreshRateLabel = CreateBoldLabel(refreshRateValue > 0 ? $"{refreshRateValue} Hz" : "Unknown", new Point(150, 55));

            // Get visual quality based on system DPI
            var visualQualityValue = DetectedSettingsHelper.GetVisualQuality();
            var visualQuality = CreateLabel("Visual Quality:", new Point(15, 80));
            var visualQualityLabel = CreateBoldLabel(visualQualityValue, new Point(150, 80));

            // Get max FPS based on display refresh rate
            var maxFpsValue = DetectedSettingsHelper.GetMaxFPS();
            var maxFps = CreateLabel("Max Frames p/s:", new Point(15, 105));
            var maxFpsLabel = CreateBoldLabel(maxFpsValue.ToString(), new Point(150, 105));

            // Get encoder type based on system capabilities
            var encoderTypeValue = DetectedSettingsHelper.GetEncoderType();
            var encoderType = CreateLabel("Encoder type:", new Point(15, 130));
            var encoderTypeLabel = CreateBoldLabel(encoderTypeValue, new Point(150, 130));

            // Check hardware encoding capabilities
            var hwEncodeValue = DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive";
            var hwEncode = CreateLabel("Hardware Encode:", new Point(15, 155));
            var hwEncodeLabel = CreateBoldLabel(hwEncodeValue, new Point(150, 155));

            group.Controls.AddRange(new Control[]
            {
                resolutionLabel, resolutionValue,
                refreshRate, refreshRateLabel,
                visualQuality, visualQualityLabel,
                maxFps, maxFpsLabel,
                encoderType, encoderTypeLabel,
                hwEncode, hwEncodeLabel
            });

            return group;
        }

        private GroupBox CreateRealTimeStatsGroup(Point location, int matchWidth = 0)
        {
            var group = new GroupBox
            {
                Text = "Real-Time Advanced Statistics",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Location = location
            };

            // Set width to match GPU Information group if specified
            if (matchWidth > 0)
            {
                // Set the width to match, and height to fit content
                group.Size = new Size(matchWidth, 120); // 120 is enough for 2 lines and padding
                group.AutoSize = false;
            }
            else
            {
                group.AutoSize = true;
                group.AutoSizeMode = AutoSizeMode.GrowAndShrink;
            }

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

        private GroupBox CreateCustomSettingsGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "Custom Settings",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(370, 150),
                Location = location
            };
            int y = 30;
            foreach (var setting in customSettings!)
            {
                string display = CustomSettingsHelper.GetRegistryDisplay(setting);
                var label = new Label
                {
                    Text = display,
                    Location = new Point(15, y),
                    AutoSize = true,
                    Font = new Font("Segoe UI", 9)
                };
                group.Controls.Add(label);
                y += 25;
            }
            return group;
        }

        private GroupBox CreateSessionInfoGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "Session Info",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Location = location
            };

            // Fetch session info from RdpNative
            var stats = RdpStatsApp.RdpNative.GetRdpStatistics();
            var sessionIdLabel = CreateLabel("Session Id:", new Point(15, 30));
            var sessionIdValue = CreateBoldLabel(stats.SessionId.ToString(), new Point(150, 30));
            var clientNameLabel = CreateLabel("Client Name:", new Point(15, 55));
            var clientNameValue = CreateBoldLabel(stats.ClientName ?? "", new Point(150, 55));
            var protocolVersionLabel = CreateLabel("Protocol Version:", new Point(15, 80));
            var protocolVersionValue = CreateBoldLabel(stats.ProtocolVersion ?? "", new Point(150, 80));

            group.Controls.Add(sessionIdLabel);
            group.Controls.Add(sessionIdValue);
            group.Controls.Add(clientNameLabel);
            group.Controls.Add(clientNameValue);
            group.Controls.Add(protocolVersionLabel);
            group.Controls.Add(protocolVersionValue);
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

        // Form overrides
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            // Dynamically size the form to fit all group boxes
            int minX = int.MaxValue, minY = int.MaxValue, maxX = int.MinValue, maxY = int.MinValue;
            foreach (Control ctrl in this.Controls)
            {
                if (ctrl is GroupBox)
                {
                    minX = Math.Min(minX, ctrl.Left);
                    minY = Math.Min(minY, ctrl.Top);
                    maxX = Math.Max(maxX, ctrl.Right);
                    maxY = Math.Max(maxY, ctrl.Bottom);
                }
            }
            int sidePadding = minX; // Use the left padding as the standard for both sides
            int verticalPadding = 20; // Keep vertical padding as before
            this.ClientSize = new Size((maxX - minX) + sidePadding * 2, (maxY - minY) + verticalPadding * 2);
            // Snap to bottom right of the primary screen's working area
            var workingArea = Screen.FromControl(this).WorkingArea;
            this.Location = new System.Drawing.Point(
                workingArea.Right - this.Width,
                workingArea.Bottom - this.Height
            );
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
            statsTimer?.Stop();
            if (trayIcon != null)
            {
                trayIcon.Visible = false;
                trayIcon.Dispose();
            }
        }
    }
}