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

        public class CustomRegistrySetting
        {
            public string registry_path { get; set; } = string.Empty;
            public string value_name { get; set; } = string.Empty;
            public string value_type { get; set; } = string.Empty;
            public int expected_value { get; set; }
            public string friendly_name { get; set; } = string.Empty;
            public string fallback_name { get; set; } = string.Empty;
        }

        private List<CustomRegistrySetting>? customSettings;

        public Form1()
        {
            this.Icon = new Icon("Resources/banana.ico");
            InitializeTrayIcon();
            LoadCustomSettings();
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

        private void LoadCustomSettings()
        {
            string path = "Resources/custom_registry_settings.json";
            if (System.IO.File.Exists(path))
            {
                string json = System.IO.File.ReadAllText(path);
                customSettings = JsonSerializer.Deserialize<List<CustomRegistrySetting>>(json);
            }
            else
            {
                customSettings = null;
            }
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
            int customSettingsY = realTimeStatsGroup.Bottom + 10;
            if (customSettings != null && customSettings.Count > 0)
            {
                var customSettingsGroup = CreateCustomSettingsGroup(new Point(20, customSettingsY));
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
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Location = location
            };
            int y = 30;
            foreach (var setting in customSettings!)
            {
                string display = GetRegistryDisplay(setting);
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

        private string GetRegistryDisplay(CustomRegistrySetting setting)
        {
            try
            {
                var baseKey = GetBaseKey(setting.registry_path, out string subKeyPath);
                using (var key = baseKey.OpenSubKey(subKeyPath))
                {
                    if (key != null)
                    {
                        var value = key.GetValue(setting.value_name);
                        if (value != null && value.ToString() == setting.expected_value.ToString())
                        {
                            return setting.friendly_name;
                        }
                    }
                }
            }
            catch { }
            return setting.fallback_name;
        }

        private RegistryKey GetBaseKey(string fullPath, out string subKeyPath)
        {
            if (fullPath.StartsWith("HKEY_LOCAL_MACHINE"))
            {
                subKeyPath = fullPath.Substring("HKEY_LOCAL_MACHINE".Length + 1);
                return Registry.LocalMachine;
            }
            if (fullPath.StartsWith("HKEY_CURRENT_USER"))
            {
                subKeyPath = fullPath.Substring("HKEY_CURRENT_USER".Length + 1);
                return Registry.CurrentUser;
            }
            // Add more as needed
            subKeyPath = fullPath;
            return Registry.LocalMachine;
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