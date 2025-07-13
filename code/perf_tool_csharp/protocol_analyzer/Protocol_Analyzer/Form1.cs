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
        private ToolTip tooltip = new ToolTip();

        public Form1()
        {
            this.Icon = new Icon("Resources/banana.ico");
            InitializeTrayIcon();
            customSettings = CustomSettingsHelper.LoadCustomSettings("Resources/custom_registry_settings.json");
            BuildUI();
            this.Font = new Font("Segoe UI", 10F);
            this.MinimumSize = new Size(700, 600);
            this.Padding = new Padding(0);
            this.AutoSize = true;
            this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
        }

        private void InitializeTrayIcon()
        {
            trayIcon = new NotifyIcon();
            trayIcon.Icon = new Icon("Resources/banana.ico");
            trayIcon.Text = "Session Perf";
            trayIcon.Visible = true;
            var contextMenu = new ContextMenuStrip();
            var exitItem = new ToolStripMenuItem("Exit");
            exitItem.Click += (s, e) => { this.Close(); };
            contextMenu.Items.Add(exitItem);
            trayIcon.ContextMenuStrip = contextMenu;
        }

        private void BuildUI()
        {
            this.Text = "Phil's Session Perf";
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MaximizeBox = true;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.BackColor = Color.White;

            var mainTable = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 4,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Padding = new Padding(0),
            };
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            for (int i = 0; i < 4; i++)
                mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));

            // Add modern header
            var headerPanel = new Panel
            {
                Dock = DockStyle.Top,
                Height = 48,
                BackColor = Color.FromArgb(33, 150, 243),
                Margin = new Padding(0, 0, 0, 10),
            };
            var headerLabel = new Label
            {
                Text = "Phil's Session Perf",
                Font = new Font("Segoe UI", 18, FontStyle.Bold),
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(18, 8)
            };
            headerPanel.Controls.Add(headerLabel);
            mainTable.Controls.Add(headerPanel, 0, 0);
            mainTable.SetColumnSpan(headerPanel, 2);

            // Cards with modern look
            var gpuInfoGroup = CreateCardGroupBox(CreateGpuInfoGroup());
            mainTable.Controls.Add(gpuInfoGroup, 0, 1);

            var detectedSettingsGroup = CreateCardGroupBox(CreateDetectedSettingsGroup());
            mainTable.Controls.Add(detectedSettingsGroup, 1, 1);

            var realTimeStatsGroup = CreateCardGroupBox(CreateRealTimeStatsGroup());
            mainTable.Controls.Add(realTimeStatsGroup, 0, 2);

            var customSettingsGroup = CreateCardGroupBox(CreateCustomSettingsGroup());
            mainTable.Controls.Add(customSettingsGroup, 1, 2);

            var sessionInfoGroup = CreateCardGroupBox(CreateSessionInfoGroup());
            mainTable.Controls.Add(sessionInfoGroup, 0, 3);
            mainTable.SetColumnSpan(sessionInfoGroup, 2);

            // Clear and add
            this.Controls.Clear();
            this.Controls.Add(mainTable);

            // Stats timer
            statsTimer = new System.Windows.Forms.Timer();
            statsTimer.Interval = 15000;
            statsTimer.Tick += PollEncoderFramesDropped;
            statsTimer.Start();
        }

        private GroupBox CreateCardGroupBox(GroupBox inner)
        {
            // Soft "card" background
            inner.BackColor = Color.FromArgb(245, 245, 245);
            inner.Padding = new Padding(12);
            inner.Dock = DockStyle.Fill;
            inner.Margin = new Padding(15, 10, 15, 10);
            return inner;
        }

        private GroupBox CreateGpuInfoGroup()
        {
            var group = new GroupBox
            {
                Text = "GPU Information",
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
            };

            var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
            int y = 30;

            AddRow(group, "Main Display Resolution:", $"{resolution.Width}x{resolution.Height}", ref y);
            AddRow(group, "DPI Scale:", $"{dpiScale * 100:F0} %", ref y);
            AddDivider(group, ref y);

            var (sessionType, gpuType, encoderType, hwEncode) = GraphicsProfileHelper.GetGraphicsProfileDetails();
            AddRow(group, "Session Type:", sessionType, ref y);
            AddRow(group, "GPU Type:", gpuType, ref y);
            AddRow(group, "Encoding:", encoderType, ref y);
            AddRow(group, "HW Encode:", hwEncode, ref y, hwEncode == "Active" ? Color.SeaGreen : Color.IndianRed);

            return group;
        }

        private GroupBox CreateDetectedSettingsGroup()
        {
            var group = new GroupBox
            {
                Text = "Detected Settings",
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
            };

            var (width, height, refreshRateValue, scalingFactor) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
            int y = 30;

            AddRow(group, "Display Resolution:", width > 0 && height > 0 ? $"{width}x{height}" : "Unknown", ref y);
            AddRow(group, "Display Refresh Rate:", refreshRateValue > 0 ? $"{refreshRateValue} Hz" : "Unknown", ref y);
            AddRow(group, "Scaling:", $"{scalingFactor * 100:F0}%", ref y);
            AddRow(group, "Visual Quality:", DetectedSettingsHelper.GetVisualQuality(), ref y);
            AddRow(group, "Max Frames p/s:", DetectedSettingsHelper.GetMaxFPS().ToString(), ref y);
            AddRow(group, "Hardware Encode:", DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive", ref y, DetectedSettingsHelper.IsHardwareEncodingSupported() ? Color.SeaGreen : Color.IndianRed);
            AddRow(group, "Encoder type:", DetectedSettingsHelper.GetEncoderType(), ref y);

            return group;
        }

        private GroupBox CreateRealTimeStatsGroup()
        {
            var group = new GroupBox
            {
                Text = "Real-Time Advanced Statistics",
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Dock = DockStyle.Fill
            };

            int y = 30;
            statsLabel = CreateBoldLabel("Encoder Frames Dropped: (waiting for data)", new Point(15, y));
            tooltip.SetToolTip(statsLabel, "Number of video frames dropped by the encoder since session start.");
            group.Controls.Add(statsLabel);
            y += 30;

            fpsLabel = CreateBoldLabel("Input Frames Per Second: (waiting for data)", new Point(15, y));
            tooltip.SetToolTip(fpsLabel, "Input frames per second received by the encoder.");
            group.Controls.Add(fpsLabel);

            return group;
        }

        private GroupBox CreateCustomSettingsGroup()
        {
            var group = new GroupBox
            {
                Text = "Custom Settings",
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
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

        private GroupBox CreateSessionInfoGroup()
        {
            var group = new GroupBox
            {
                Text = "Session Info",
                Font = new Font("Segoe UI", 11, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
            };
            int y = 30;
            var stats = RdpStatsApp.RdpNative.GetRdpStatistics();
            AddRow(group, "Session Id:", stats.SessionId.ToString(), ref y);
            AddRow(group, "Client Name:", stats.ClientName ?? string.Empty, ref y);
            AddRow(group, "Protocol Version:", stats.ProtocolVersion ?? string.Empty, ref y);
            return group;
        }

        private void AddRow(GroupBox group, string label, string value, ref int y, Color? valueColor = null)
        {
            var lbl = CreateLabel(label, new Point(15, y));
            var val = CreateBoldLabel(value, new Point(180, y), valueColor ?? Color.FromArgb(40, 40, 40));
            group.Controls.Add(lbl);
            group.Controls.Add(val);
            y += 30;
        }

        private void AddDivider(GroupBox group, ref int y)
        {
            var divider = new Label
            {
                Height = 1,
                Width = 300,
                Location = new Point(15, y),
                BackColor = Color.LightGray
            };
            group.Controls.Add(divider);
            y += 12;
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

        private Label CreateBoldLabel(string text, Point location, Color? foreColor = null)
        {
            var label = new Label
            {
                Text = text,
                Location = location,
                AutoSize = true,
                Font = new Font("Segoe UI", 9, FontStyle.Bold)
            };
            if (foreColor != null)
                label.ForeColor = foreColor.Value;
            return label;
        }

        private void PollEncoderFramesDropped(object? sender, EventArgs e)
        {
            int framesDropped = RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
            statsLabel.Text = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString() : "Unavailable")}";
            int inputFps = RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
            fpsLabel.Text = $"Input Frames Per Second: {(inputFps >= 0 ? inputFps.ToString() : "Unavailable")}";
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
