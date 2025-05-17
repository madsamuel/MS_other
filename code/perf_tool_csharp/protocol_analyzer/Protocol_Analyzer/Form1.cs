using System;
using System.Drawing;
using System.Management;
using System.Windows.Forms;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        private GroupBox? gpuGroup;
        private Label? gpuInfoLabel;
        private GroupBox? displaySettingsGroup;
        private GroupBox? gpuStatsGroup;
        private Label? gpuStatsLabel;

        private IntPtr gpuDevice;
        private System.Windows.Forms.Timer? gpuStatsTimer;

        public Form1()
        {
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "System Info";
            this.Size = new Size(800, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // GPU Information
            gpuGroup = CreateGpuInfoGroup(new Point(20, 20));
            this.Controls.Add(gpuGroup);
            DisplayGPUInfo();

            // Adjust Display Settings
            displaySettingsGroup = CreateAdjustDisplaySettingsGroup(new Point(400, 20));
            this.Controls.Add(displaySettingsGroup);

            // GPU Statistics
            gpuStatsGroup = CreateGpuStatsGroup(new Point(20, 460));
            this.Controls.Add(gpuStatsGroup);

            int initResult = NvmlInterop.nvmlInit_v2();
            if (initResult != 0)
            {
                MessageBox.Show("NVML initialization failed. Is nvml.dll accessible?");
                return;
            }

            int handleResult = NvmlInterop.nvmlDeviceGetHandleByIndex(0, out gpuDevice);
            if (handleResult != 0)
            {
                MessageBox.Show("Failed to get GPU device handle.");
                return;
            }
            
            gpuStatsTimer = new System.Windows.Forms.Timer();
            gpuStatsTimer.Interval = 1000;
            gpuStatsTimer.Tick += UpdateGpuStats;
            gpuStatsTimer.Start();
        }

        private GroupBox CreateGpuInfoGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "GPU Information",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(350, 420),
                Location = location
            };

            gpuInfoLabel = new Label
            {
                AutoSize = true,
                Location = new Point(15, 30),
                Font = new Font("Segoe UI", 9)
            };

            group.Controls.Add(gpuInfoLabel);
            return group;
        }

        private GroupBox CreateAdjustDisplaySettingsGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "Adjust Display Settings",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(370, 420),
                Location = location
            };

            var codecLabel = CreateLabel("Use video codec for compression:", new Point(15, 30));
            var codecCombo = new ComboBox
            {
                Location = new Point(15, 50), Width = 320,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            codecCombo.Items.AddRange(new[] { "Use when preferred", "Always", "Never" });
            codecCombo.SelectedIndex = 0;

            var qualityLabel = CreateLabel("Visual Quality:", new Point(15, 85));
            var qualityCombo = new ComboBox
            {
                Location = new Point(15, 105), Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            qualityCombo.Items.AddRange(new[] { "Low", "Medium", "High" });
            qualityCombo.SelectedIndex = 1;

            var losslessCheck = new CheckBox { Text = "Allow visually lossless compression", Location = new Point(15, 140), AutoSize = true };
            var maxFpsLabel = CreateLabel("Max Frames per second:", new Point(15, 170));
            var maxFpsCombo = new ComboBox
            {
                Location = new Point(15, 190), Width = 80,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            maxFpsCombo.Items.AddRange(new[] { "15", "24", "30", "60" });
            maxFpsCombo.SelectedItem = "30";

            var hwEncodeCheck = new CheckBox { Text = "Use hardware encoding", Location = new Point(15, 225), AutoSize = true };
            var optimizeCheck = new CheckBox { Text = "Optimize for 3D graphics Workload", Location = new Point(15, 250), AutoSize = true };

            var citrixIddLabel = CreateLabel("Citrix IDD:", new Point(15, 280));
            var iddValueLabel = new Label
            {
                Text = "Not configured",
                Font = new Font("Segoe UI", 9, FontStyle.Bold),
                ForeColor = Color.Black,
                Location = new Point(100, 280),
                AutoSize = true
            };

            var advancedBtn = new Button { Text = "Advanced Settings", Location = new Point(15, 320), Width = 320 };

            group.Controls.AddRange(new Control[]
            {
                codecLabel, codecCombo,
                qualityLabel, qualityCombo,
                losslessCheck,
                maxFpsLabel, maxFpsCombo,
                hwEncodeCheck, optimizeCheck,
                citrixIddLabel, iddValueLabel,
                advancedBtn
            });

            return group;
        }

        private GroupBox CreateGpuStatsGroup(Point location)
        {
            var group = new GroupBox
            {
                Text = "GPU Statistics",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(750, 160),
                Location = location
            };

            gpuStatsLabel = new Label
            {
                AutoSize = true,
                Location = new Point(15, 30),
                Font = new Font("Segoe UI", 9),
                Text = "Loading..."
            };

            group.Controls.Add(gpuStatsLabel);
            return group;
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

        private void DisplayGPUInfo()
        {
            string gpuName = "Unknown GPU";
            string driverVersion = "Unknown Version";
            string licenseType = "NVIDIA Virtual PC";
            string licenseStatus = "Activated";

            using (var searcher = new ManagementObjectSearcher("select * from Win32_VideoController"))
            {
                foreach (var obj in searcher.Get())
                {
                    gpuName = obj["Name"]?.ToString() ?? "Unknown GPU";
                    driverVersion = obj["DriverVersion"]?.ToString() ?? "Unknown Version";
                    break;
                }
            }

            var totalMemoryBytes = new Microsoft.VisualBasic.Devices.ComputerInfo().TotalPhysicalMemory;
            int totalMemoryMB = (int)(totalMemoryBytes / (1024 * 1024));

            Size resolution = Screen.PrimaryScreen?.Bounds.Size ?? new Size(1920, 1080);
            float dpiScale = CreateGraphics()?.DpiX / 96f ?? 1.0f;

            string info = $"Active GPU:\n  {gpuName}\n\n" +
                          $"Total Memory:\n  {totalMemoryMB} MB\n\n" +
                          $"Primary Screen Resolution:\n  {resolution.Width}x{resolution.Height}\n" +
                          $"DPI Scale:\n  {dpiScale * 100:F0} %\n\n" +
                          $"Driver Version:\n  {driverVersion}\n\n" +
                          $"License:\n  {licenseStatus}\n\n" +
                          $"License Type:\n  {licenseType}";

            if (gpuInfoLabel != null)
            {
                gpuInfoLabel.Text = info;
            }
        }

        private void UpdateGpuStats(object? sender, EventArgs e)
        {
            try
            {
                NvmlInterop.NvmlUtilization util;
                NvmlInterop.nvmlDeviceGetUtilizationRates(gpuDevice, out util);

                NvmlInterop.NvmlMemory mem;
                NvmlInterop.nvmlDeviceGetMemoryInfo(gpuDevice, out mem);
                int usedMB = (int)(mem.used / (1024 * 1024));
                int totalMB = (int)(mem.total / (1024 * 1024));
                int memoryPct = (int)(100 * mem.used / mem.total);

                uint encUtil, encPeriod, decUtil, decPeriod;
                NvmlInterop.nvmlDeviceGetEncoderUtilization(gpuDevice, out encUtil, out encPeriod);
                NvmlInterop.nvmlDeviceGetDecoderUtilization(gpuDevice, out decUtil, out decPeriod);

                gpuStatsLabel!.Text = $"GPU Utilization:        {util.gpu}%\n" +
                                      $"Memory Usage:           {memoryPct}% ({usedMB} MB)\n" +
                                      $"Video Encoder Usage:    {encUtil}%\n" +
                                      $"Video Decoder Usage:    {decUtil}%";

                
            }
            catch (Exception ex)
            {
                gpuStatsLabel!.Text = $"Error retrieving GPU stats:\n{ex.Message}";
            }
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
            gpuStatsTimer?.Stop();
            NvmlInterop.nvmlShutdown();
        }
    }
} 
