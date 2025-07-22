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
    // Designer container (not used by WinForms designer, but for consistency)
    private System.ComponentModel.IContainer? _components = null;
    private TableLayoutPanel mainTable = null!;
    private GroupBox groupGpu = null!;
    private GroupBox groupDetected = null!;
    private GroupBox groupStats = null!;
    private GroupBox groupCustom = null!;
    private GroupBox groupSession = null!;
    private Label gpuLabel = null!;
    private Label detectedLabel = null!;
    private Label statsLabel = null!;
    private Label customLabel = null!;
    private Label sessionLabel = null!;
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
        BuildDashboardUI();
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

    private void BuildDashboardUI()
    {
        _components = new System.ComponentModel.Container();
        this.AutoScaleMode = AutoScaleMode.Font;
        this.ClientSize = new System.Drawing.Size(1000, 700);
        this.Text = "Phil's Session Perf";
        this.FormBorderStyle = FormBorderStyle.FixedSingle;
        this.MaximizeBox = false;
        this.BackColor = SystemColors.Control;

        // TableLayoutPanel for main layout
        mainTable = new TableLayoutPanel();
        mainTable.Dock = DockStyle.Fill;
        mainTable.ColumnCount = 2;
        mainTable.RowCount = 3;
        mainTable.Padding = new Padding(10);
        mainTable.AutoSize = false;
        mainTable.AutoSizeMode = AutoSizeMode.GrowAndShrink;
        mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
        mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
        mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 50F));
        mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));
        mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));

        // Consistent font for all labels
        var labelFont = new Font("Segoe UI", 11F, FontStyle.Regular);

        // GPU Information GroupBox
        groupGpu = new GroupBox();
        groupGpu.Text = "GPU Information";
        groupGpu.Dock = DockStyle.Fill;
        gpuLabel = new Label();
        var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
        var (sessionType, gpuType, encoderType, hwEncode) = GraphicsProfileHelper.GetGraphicsProfileDetails();
        gpuLabel.Text =
            $"Main Display Resolution: {resolution.Width}x{resolution.Height}\n" +
            $"DPI Scale: {dpiScale * 100:F0} %\n" +
            $"Session Type: {sessionType}\n" +
            $"GPU Type: {gpuType}\n" +
            $"Encoding: {encoderType}\n" +
            $"HW Encode: {hwEncode}";
        gpuLabel.Font = labelFont;
        gpuLabel.AutoSize = false;
        gpuLabel.Dock = DockStyle.Fill;
        gpuLabel.TextAlign = ContentAlignment.TopLeft;
        groupGpu.Controls.Add(gpuLabel);

        // Detected Settings GroupBox
        groupDetected = new GroupBox();
        groupDetected.Text = "Detected settings";
        groupDetected.Dock = DockStyle.Fill;
        detectedLabel = new Label();
        var (width, height, refreshRateValue, scalingFactor) = DetectedSettingsHelper.GetDisplayResolutionAndRefreshRate();
        detectedLabel.Text =
            $"Display Resolution: {(width > 0 && height > 0 ? $"{width}x{height}" : "Unknown")}\n" +
            $"Display Refresh Rate: {(refreshRateValue > 0 ? $"{refreshRateValue} Hz" : "Unknown")}\n" +
            $"Scaling: {scalingFactor * 100:F0}%\n" +
            $"Visual Quality: {DetectedSettingsHelper.GetVisualQuality()}\n" +
            $"Max Frames p/s: {DetectedSettingsHelper.GetMaxFPS()}\n" +
            $"Hardware Encode: {(DetectedSettingsHelper.IsHardwareEncodingSupported() ? "Active" : "Inactive")}\n" +
            $"Encoder type: {DetectedSettingsHelper.GetEncoderType()}";
        detectedLabel.Font = labelFont;
        detectedLabel.AutoSize = false;
        detectedLabel.Dock = DockStyle.Fill;
        detectedLabel.TextAlign = ContentAlignment.TopLeft;
        groupDetected.Controls.Add(detectedLabel);

        // Real-Time Advanced Statistics GroupBox
        groupStats = new GroupBox();
        groupStats.Text = "Real-Time Advanced Statistics";
        groupStats.Dock = DockStyle.Fill;
        statsLabel = new Label();
        statsLabel.Text = "Encoder Frames Dropped: (waiting for data)\nInput Frames Per Second: (waiting for data)";
        statsLabel.Font = labelFont;
        statsLabel.AutoSize = false;
        statsLabel.Dock = DockStyle.Fill;
        statsLabel.TextAlign = ContentAlignment.TopLeft;
        groupStats.Controls.Add(statsLabel);

        // Session Info GroupBox
        groupSession = new GroupBox();
        groupSession.Text = "Session Info";
        groupSession.Dock = DockStyle.Fill;
        sessionLabel = new Label();
        var sessionStats = RdpStatsApp.RdpNative.GetRdpStatistics();
        sessionLabel.Text =
            $"Session Id: {sessionStats.SessionId}\n" +
            $"Client Name: {sessionStats.ClientName ?? "N/A"}\n" +
            $"Protocol Version: {sessionStats.ProtocolVersion ?? "N/A"}";
        sessionLabel.Font = labelFont;
        sessionLabel.AutoSize = false;
        sessionLabel.Dock = DockStyle.Fill;
        sessionLabel.TextAlign = ContentAlignment.TopLeft;
        groupSession.Controls.Add(sessionLabel);

        // Custom Settings GroupBox
        groupCustom = new GroupBox();
        groupCustom.Text = "Custom Settings";
        groupCustom.Dock = DockStyle.Fill;
        customLabel = new Label();
        if (customSettings != null && customSettings.Count > 0)
        {
            customLabel.Text = string.Join("\n", customSettings.ConvertAll(s =>
                (CustomSettingsHelper.GetRegistryDisplay(s) ?? s.ToString()) ?? string.Empty));
        }
        else
        {
            customLabel.Text = "No custom settings found.";
        }
        customLabel.Font = labelFont;
        customLabel.AutoSize = false;
        customLabel.Dock = DockStyle.Fill;
        customLabel.TextAlign = ContentAlignment.TopLeft;
        groupCustom.Controls.Add(customLabel);

        // Add controls to mainTable
        mainTable.Controls.Add(groupGpu, 0, 0);
        mainTable.Controls.Add(groupDetected, 1, 0);
        mainTable.Controls.Add(groupStats, 0, 1);
        mainTable.Controls.Add(groupSession, 1, 1);
        mainTable.Controls.Add(groupCustom, 0, 2);
        mainTable.SetColumnSpan(groupCustom, 2);

        this.Controls.Add(mainTable);

        // Timer for stats
        statsTimer = new System.Windows.Forms.Timer();
        statsTimer.Interval = 5000;
        statsTimer.Tick += PollStats;
        statsTimer.Start();
        PollStats(null, EventArgs.Empty);
    }

    private void PollStats(object? sender, EventArgs e)
    {
        int framesDropped = RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
        int inputFps = RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
        statsLabel.Text = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString() : "Unavailable")}\nInput Frames Per Second: {(inputFps >= 0 ? inputFps.ToString() : "Unavailable")}";
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
