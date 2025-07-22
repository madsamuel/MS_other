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

            // Top row
            mainTable.Controls.Add(CreateGpuInfoGroup(), 0, 0);
            mainTable.Controls.Add(CreateDetectedSettingsGroup(), 1, 0);

            // Middle row
            mainTable.Controls.Add(CreateRealTimeStatsGroup(), 0, 1);
            mainTable.Controls.Add(CreateSessionInfoGroup(), 1, 1);

            // Bottom row
            var customGroup = CreateCustomSettingsGroup();
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

        private GroupBox CreateGpuInfoGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("GPU Information", table);

            var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
            AddRow(table, "Main Display Resolution:", $"{resolution.Width}x{resolution.Height}");
            AddRow(table, "DPI Scale:", $"{dpiScale * 100:F0}%");

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
            var table = CreateStandardTable();
            var group = CreateGroupBox("Real-Time Advanced Statistics", table);

            statsLabel = AddRow(table, "Encoder Frames Dropped:", "(waiting for data)");
            fpsLabel = AddRow(table, "Input Frames Per Second:", "(waiting for data)");

            return group;
        }

        private GroupBox CreateCustomSettingsGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("Custom Settings", table);

            if (customSettings != null && customSettings.Count > 0)
            {
                foreach (var setting in customSettings)
                {
                    string display = CustomSettingsHelper.GetRegistryDisplay(setting);
                    AddRow(table, setting.ToString(), display);
                }
            }
            else
            {
                AddRow(table, "No custom settings found.", "");
            }

            return group;
        }

        private GroupBox CreateSessionInfoGroup()
        {
            var table = CreateStandardTable();
            var group = CreateGroupBox("Session Info", table);

            var stats = RdpStatsApp.RdpNative.GetRdpStatistics();
            AddRow(table, "Session Id:", stats.SessionId.ToString());
            AddRow(table, "Client Name:", stats.ClientName ?? "N/A");
            AddRow(table, "Protocol Version:", stats.ProtocolVersion ?? "N/A");

            return group;
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
