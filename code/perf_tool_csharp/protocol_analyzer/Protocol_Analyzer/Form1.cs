using System;
using System.Management;
using System.Windows.Forms;
using System.Drawing;

namespace Protocol_Analyzer;
public partial class Form1 : Form
{
    public Form1()
    {
        InitializeComponent();
        InitializeUI();
        DisplayGPUInfo();
    }

    private GroupBox gpuGroup;
    private Label gpuInfoLabel;

    private void InitializeUI()
    {
        this.Text = "System Info";
        this.Size = new Size(400, 450);

        gpuGroup = new GroupBox
        {
            Text = "GPU Information",
            Font = new Font("Segoe UI", 10, FontStyle.Bold),
            Size = new Size(350, 380),
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