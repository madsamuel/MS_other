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

        public Form1()
        {
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "System Info";
            this.Size = new Size(800, 500);
            this.StartPosition = FormStartPosition.CenterScreen;

            // --- GPU INFO GROUP (Left) ---
            gpuGroup = new GroupBox
            {
                Text = "GPU Information",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(350, 420),
                Location = new Point(20, 20)
            };

            gpuInfoLabel = new Label
            {
                AutoSize = true,
                Location = new Point(15, 30),
                Font = new Font("Segoe UI", 9)
            };

            gpuGroup.Controls.Add(gpuInfoLabel);
            this.Controls.Add(gpuGroup);
            DisplayGPUInfo();

            // --- ADJUST DISPLAY SETTINGS GROUP (Right) ---
            displaySettingsGroup = new GroupBox
            {
                Text = "Adjust Display Settings",
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                Size = new Size(370, 420),
                Location = new Point(400, 20)
            };

            var codecLabel = new Label { Text = "Use video codec for compression:", Location = new Point(15, 30), AutoSize = true };
            var codecCombo = new ComboBox
            {
                Location = new Point(15, 50),
                Width = 320,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            codecCombo.Items.AddRange(new[] { "Use when preferred", "Always", "Never" });
            codecCombo.SelectedIndex = 0;

            var qualityLabel = new Label { Text = "Visual Quality:", Location = new Point(15, 85), AutoSize = true };
            var qualityCombo = new ComboBox
            {
                Location = new Point(15, 105),
                Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            qualityCombo.Items.AddRange(new[] { "Low", "Medium", "High" });
            qualityCombo.SelectedIndex = 1;

            var losslessCheck = new CheckBox { Text = "Allow visually lossless compression", Location = new Point(15, 140), AutoSize = true };

            var maxFpsLabel = new Label { Text = "Max Frames per second:", Location = new Point(15, 170), AutoSize = true };
            var maxFpsCombo = new ComboBox
            {
                Location = new Point(15, 190),
                Width = 80,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            maxFpsCombo.Items.AddRange(new[] { "15", "24", "30", "60" });
            maxFpsCombo.SelectedItem = "30";

            var hwEncodeCheck = new CheckBox { Text = "Use hardware encoding", Location = new Point(15, 225), AutoSize = true };
            var optimizeCheck = new CheckBox { Text = "Optimize for 3D graphics Workload", Location = new Point(15, 250), AutoSize = true };

            var citrixIddLabel = new Label { Text = "Citrix IDD:", Location = new Point(15, 280), AutoSize = true };
            var iddValueLabel = new Label
            {
                Text = "Not configured",
                Font = new Font("Segoe UI", 9, FontStyle.Bold),
                ForeColor = Color.Black,
                Location = new Point(100, 280),
                AutoSize = true
            };

            var advancedBtn = new Button
            {
                Text = "⚙ Advanced Settings",
                Location = new Point(15, 320),
                Width = 320
            };

            displaySettingsGroup.Controls.AddRange(new Control[]
            {
                codecLabel, codecCombo,
                qualityLabel, qualityCombo,
                losslessCheck,
                maxFpsLabel, maxFpsCombo,
                hwEncodeCheck, optimizeCheck,
                citrixIddLabel, iddValueLabel,
                advancedBtn
            });

            this.Controls.Add(displaySettingsGroup);
        }

        private void DisplayGPUInfo()
        {
            string gpuName = "";
            string driverVersion = "";
            string licenseType = "NVIDIA Virtual PC";
            string licenseStatus = "Activated";

            using (var searcher = new ManagementObjectSearcher("select * from Win32_VideoController"))
            {
                foreach (var obj in searcher.Get())
                {
                    gpuName = obj["Name"]?.ToString();
                    driverVersion = obj["DriverVersion"]?.ToString();
                    break;
                }
            }

            int totalMemoryMB = (int)(new Microsoft.VisualBasic.Devices.ComputerInfo().TotalPhysicalMemory / (1024 * 1024));
            Size resolution = Screen.PrimaryScreen.Bounds.Size;
            float dpiScale = CreateGraphics().DpiX / 96f;

            string info = $"Active GPU:\n  {gpuName}\n\n" +
                          $"Total Memory:\n  {totalMemoryMB} MB\n\n" +
                          $"Primary Screen Resolution:\n  {resolution.Width}x{resolution.Height}\n" +
                          $"DPI Scale:\n  {dpiScale * 100:F0} %\n\n" +
                          $"Driver Version:\n  {driverVersion}\n\n" +
                          $"License:\n  {licenseStatus}\n\n" +
                          $"License Type:\n  {licenseType}";

            gpuInfoLabel.Text = info;
        }
    }
}
