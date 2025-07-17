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
            this.AutoSize = false;
            this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
            this.Padding = new Padding(10);
            this.Size = new Size(700, 800);           
            this.MinimumSize = new Size(700, 800); 
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
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.StartPosition = FormStartPosition.CenterScreen;

            var mainTable = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 3,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowOnly,
                Padding = new Padding(10),
            };
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 40F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 40F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 34F));

            var gpuInfoGroup = CreateGpuInfoGroup();
            mainTable.Controls.Add(gpuInfoGroup, 0, 0);

            var detectedSettingsGroup = CreateDetectedSettingsGroup();
            mainTable.Controls.Add(detectedSettingsGroup, 1, 0);

            var realTimeStatsGroup = CreateRealTimeStatsGroup();
            mainTable.Controls.Add(realTimeStatsGroup, 0, 1);

            var customSettingsGroup = CreateCustomSettingsGroup();
            mainTable.Controls.Add(customSettingsGroup, 1, 1);

            var sessionInfoGroup = CreateSessionInfoGroup();
            mainTable.Controls.Add(sessionInfoGroup, 0, 2);
            mainTable.SetColumnSpan(sessionInfoGroup, 2);

            this.Controls.Clear();
            this.Controls.Add(mainTable);

            statsTimer = new System.Windows.Forms.Timer();
            statsTimer.Interval = 15000;
            statsTimer.Tick += PollEncoderFramesDropped;
            statsTimer.Start();
        }

        private GroupBox CreateGpuInfoGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("GPU Information", table);

            table.AutoSize = false;
            table.Dock = DockStyle.Fill;
        
            group.AutoSize = false;
            group.MinimumSize = new Size(320, 155);   // Adjust size as needed to fit all labels
            group.MaximumSize = new Size(320, 155);   // Optional: locks the size so it never grows/shrinks
            group.Size = new Size(320, 155);

            var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
            AddRow(table, "Main Display Resolution:", $"{resolution.Width}x{resolution.Height}");
            AddRow(table, "DPI Scale:", $"{dpiScale * 100:F0} %");

            var (sessionType, gpuType, encoderType, hwEncode) = GraphicsProfileHelper.GetGraphicsProfileDetails();
            AddRow(table, "Session Type:", sessionType);
            AddRow(table, "GPU Type:", gpuType);
            AddRow(table, "Encoding:", encoderType);
            AddRow(table, "HW Encode:", hwEncode);

            return group;
        }

        private GroupBox CreateDetectedSettingsGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("Detected settings", table);

            table.AutoSize = false;
            table.Dock = DockStyle.Fill;
        
            group.AutoSize = false;
            group.MinimumSize = new Size(320, 155);   // Adjust size as needed to fit all labels
            group.MaximumSize = new Size(320, 155);   // Optional: locks the size so it never grows/shrinks
            group.Size = new Size(320, 155);

            var (width, height, refreshRateValue, scalingFactor) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
            AddRow(table, "Display Resolution:", width > 0 && height > 0 ? $"{width}x{height}" : "Unknown");
            AddRow(table, "Display Refresh Rate:", refreshRateValue > 0 ? $"{refreshRateValue} Hz" : "Unknown");
            AddRow(table, "Scaling:", $"{scalingFactor * 100:F0}%");
            AddRow(table, "Visual Quality:", DetectedSettingsHelper.GetVisualQuality());
            AddRow(table, "Max Frames p/s:", DetectedSettingsHelper.GetMaxFPS().ToString());
            AddRow(table, "Hardware Encode:", DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive");
            AddRow(table, "Encoder type:", DetectedSettingsHelper.GetEncoderType());

            return group;
        }

        private GroupBox CreateRealTimeStatsGroup()
        {
            var table = new TableLayoutPanel
            {
                ColumnCount = 1,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Dock = DockStyle.Fill
            };
            var group = CreateGroupBox("Real-Time Advanced Statistics", table);

            statsLabel = CreateValueLabel("Encoder Frames Dropped: (waiting for data)");
            fpsLabel = CreateValueLabel("Input Frames Per Second: (waiting for data)");

            table.Controls.Add(statsLabel);
            table.Controls.Add(fpsLabel);

            return group;
        }
        private GroupBox CreateCustomSettingsGroup()
        {
            var table = new TableLayoutPanel
            {
                ColumnCount = 1,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Dock = DockStyle.Fill
            };
            var group = CreateGroupBox("Custom Settings", table);

            foreach (var setting in customSettings!)
            {
                string display = CustomSettingsHelper.GetRegistryDisplay(setting);
                var label = CreateValueLabel(display);
                table.Controls.Add(label);
            }

            return group;
        }


        private GroupBox CreateSessionInfoGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("Session Info", table);

            var stats = RdpStatsApp.RdpNative.GetRdpStatistics();
            AddRow(table, "Session Id:", stats.SessionId.ToString());
            AddRow(table, "Client Name:", stats.ClientName ?? string.Empty);
            AddRow(table, "Protocol Version:", stats.ProtocolVersion ?? string.Empty);

            return group;
        }

        private void PollEncoderFramesDropped(object? sender, EventArgs e)
        {
            int framesDropped = RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
            statsLabel.Text = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString() : "Unavailable")}";
            int inputFps = RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
            fpsLabel.Text = $"Input Frames Per Second: {(inputFps >= 0 ? inputFps.ToString() : "Unavailable")}";
        }

        private TableLayoutPanel CreateStandardTable()
        {
            return new TableLayoutPanel
            {
                ColumnCount = 2,
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Dock = DockStyle.Fill
            };
        }

        private GroupBox CreateGroupBox(string title, Control content)
        {
            return new GroupBox
            {
                Text = title,
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                AutoSize = true,
                AutoSizeMode = AutoSizeMode.GrowAndShrink,
                Dock = DockStyle.Fill,
                Controls = { content }
            };
        }

        private void AddRow(TableLayoutPanel table, string labelText, string valueText)
        {
            var label = new Label { Text = labelText, Font = new Font("Segoe UI", 9), AutoSize = true };
            var value = new Label { Text = valueText, Font = new Font("Segoe UI", 9, FontStyle.Bold), AutoSize = true };
            table.Controls.Add(label);
            table.Controls.Add(value);
        }

        private Label CreateValueLabel(string text)
        {
            return new Label
            {
                Text = text,
                Font = new Font("Segoe UI", 9),
                AutoSize = true,
                Dock = DockStyle.Top
            };
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
