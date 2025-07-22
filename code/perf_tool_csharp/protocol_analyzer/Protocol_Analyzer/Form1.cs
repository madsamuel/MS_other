using System;
using System.Collections.Generic;
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
            try
            {
                this.Icon = new Icon("Resources/banana.ico");
                customSettings = CustomSettingsHelper.LoadCustomSettings("Resources/custom_registry_settings.json");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading resources: {ex.Message}", "Initialization Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            InitializeTrayIcon();
            BuildUI();

            this.AutoSizeMode = AutoSizeMode.GrowAndShrink;
        }

        private void InitializeTrayIcon()
        {
            trayIcon = new NotifyIcon();
            try
            {
                trayIcon.Icon = new Icon("Resources/banana.ico");
            }
            catch
            {
                trayIcon.Icon = SystemIcons.Application;
            }
            trayIcon.Text = "Phil's Session Perf";
            trayIcon.Visible = true;
            var contextMenu = new ContextMenuStrip();
            var exitItem = new ToolStripMenuItem("Exit");
            exitItem.Click += (s, e) => { this.Close(); };
            contextMenu.Items.Add(exitItem);
            trayIcon.ContextMenuStrip = contextMenu;
        }

        private void BuildUI()
        {
            this.components = new System.ComponentModel.Container();
            this.AutoScaleMode = AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1000, 700);
            this.Text = "Phil's Session Perf";
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;                
            this.BackColor = SystemColors.Control;

            var mainTable = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                
                ColumnCount = 2,
                RowCount = 3,
                Padding = new Padding(15),                
            };
            
            // TableLayoutPanel for main layout
            mainTable = new TableLayoutPanel();
            mainTable.Dock = DockStyle.Fill;
            mainTable.ColumnCount = 2;
            mainTable.RowCount = 3;
            mainTable.Padding = new Padding(10);
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 30F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 30F));
            mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 40F));


            // GPU Information
            var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
            var (sessionType, gpuType, encoderType, hwEncode) = GraphicsProfileHelper.GetGraphicsProfileDetails();
            var gpuRows = new List<(string, string)>
            {
                ("Main Display Resolution:", $"{resolution.Width}x{resolution.Height}"),
                ("DPI Scale:", $"{dpiScale * 100:F0}%"),
                ("Session Type:", sessionType),
                ("GPU Type:", gpuType),
                ("Encoding:", encoderType),
                ("HW Encode:", hwEncode)
            };
            mainTable.Controls.Add(CreateInfoGroup("GPU Information", gpuRows), 0, 0);

            // Detected Settings
            var (width, height, refreshRateValue, scalingFactor) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
            var detectedRows = new List<(string, string)>
            {
                ("Display Resolution:", width > 0 && height > 0 ? $"{width}x{height}" : "Unknown"),
                ("Display Refresh Rate:", refreshRateValue > 0 ? $"{refreshRateValue} Hz" : "Unknown"),
                ("Scaling:", $"{scalingFactor * 100:F0}%"),
                ("Visual Quality:", DetectedSettingsHelper.GetVisualQuality()),
                ("Max Frames p/s:", DetectedSettingsHelper.GetMaxFPS().ToString()),
                ("Hardware Encode:", DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive"),
                ("Encoder type:", DetectedSettingsHelper.GetEncoderType())
            };
            mainTable.Controls.Add(CreateInfoGroup("Detected settings", detectedRows), 1, 0);

            // Real-Time Advanced Statistics
            var statsRows = new List<(string, string)>
            {
                ("Encoder Frames Dropped:", "(waiting for data)"),
                ("Input Frames Per Second:", "(waiting for data)")
            };
            var statsGroup = CreateInfoGroup("Real-Time Advanced Statistics", statsRows);
            mainTable.Controls.Add(statsGroup, 0, 1);
            // Save references for updating
            statsLabel = (Label)statsGroup.Controls[0].Controls[1];
            fpsLabel = (Label)statsGroup.Controls[0].Controls[3];

            // Session Info
            var sessionStats = RdpStatsApp.RdpNative.GetRdpStatistics();
            var sessionRows = new List<(string, string)>
            {
                ("Session Id:", sessionStats.SessionId.ToString()),
                ("Client Name:", sessionStats.ClientName ?? "N/A"),
                ("Protocol Version:", sessionStats.ProtocolVersion ?? "N/A")
            };
            mainTable.Controls.Add(CreateInfoGroup("Session Info", sessionRows), 1, 1);

            // Custom Settings
            var customRows = new List<(string, string)>();
            if (customSettings != null && customSettings.Count > 0)
            {
                foreach (var setting in customSettings)
                {
                    customRows.Add((setting.ToString(), CustomSettingsHelper.GetRegistryDisplay(setting)));
                }
            }
            else
            {
                customRows.Add(("No custom settings found.", ""));
            }
            var customGroup = CreateInfoGroup("Custom Settings", customRows);
            mainTable.Controls.Add(customGroup, 0, 2);
            mainTable.SetColumnSpan(customGroup, 2);

            // this.Controls.Clear();
            this.Controls.Add(mainTable);

            statsTimer = new System.Windows.Forms.Timer();
            statsTimer.Interval = 5000;
            statsTimer.Tick += PollStats;
            statsTimer.Start();
            PollStats(null, EventArgs.Empty);
        }


        private GroupBox CreateInfoGroup(string title, List<(string, string)> rows)
        {
            var table = new TableLayoutPanel
            {
                ColumnCount = 2,
                Dock = DockStyle.Fill,
                AutoSize = true
            };
            foreach (var (labelText, valueText) in rows)
            {
                var label = new Label { Text = labelText, Font = new Font("Segoe UI", 9F, FontStyle.Bold), AutoSize = true };
                var value = new Label { Text = valueText, Font = new Font("Segoe UI", 9F), AutoSize = true, Margin = new Padding(3, 0, 0, 0) };
                int row = table.RowCount++;
                table.RowStyles.Add(new RowStyle(SizeType.Absolute, 24F));
                table.Controls.Add(label, 0, row);
                table.Controls.Add(value, 1, row);
                label.Anchor = AnchorStyles.Left;
                value.Anchor = AnchorStyles.Left;
            }
            return new GroupBox
            {
                Text = title,
                Font = new Font("Segoe UI", 9.75F, FontStyle.Bold),
                AutoSize = true,
                Dock = DockStyle.Fill,
                Padding = new Padding(15, 10, 15, 10),
                Controls = { table }
            };
        }

        private void PollStats(object? sender, EventArgs e)
        {
            int framesDropped = RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
            statsLabel.Text = framesDropped >= 0 ? framesDropped.ToString() : "Unavailable";

            int inputFps = RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
            fpsLabel.Text = inputFps >= 0 ? inputFps.ToString() : "Unavailable";
        }

        private TableLayoutPanel CreateStandardTable()
        {
            var table = new TableLayoutPanel
            {
                ColumnCount = 2,                           
                Dock = DockStyle.Top, 
            };

            return table;
        }

        private GroupBox CreateGroupBox(string title, Control content)
        {
            return new GroupBox
            {
                Text = title,
                Font = new Font("Segoe UI", 9.75F, FontStyle.Bold),
                AutoSize = true,
                Dock = DockStyle.Fill,
                Padding = new Padding(15, 10, 15, 10), 
                Controls = { content }
            };
        }

        private Label AddRow(TableLayoutPanel table, string labelText, string valueText)
        {
            var label = new Label { Text = labelText, Font = new Font("Segoe UI", 9F, FontStyle.Bold), AutoSize = true };
            var value = new Label { Text = valueText, Font = new Font("Segoe UI", 9F), AutoSize = true, Margin = new Padding(3, 0, 0, 0) };
            
            table.RowCount++;
            table.RowStyles.Add(new RowStyle(SizeType.Absolute, 24F));
            table.Controls.Add(label, 0, table.RowCount - 1);
            table.Controls.Add(value, 1, table.RowCount - 1);

            label.Anchor = AnchorStyles.Left;
            value.Anchor = AnchorStyles.Left;

            return value;
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
            statsTimer?.Stop();
            statsTimer?.Dispose();
            if (trayIcon != null)
            {
                trayIcon.Visible = false;
                trayIcon.Dispose();
            }
        }    
    }
}
