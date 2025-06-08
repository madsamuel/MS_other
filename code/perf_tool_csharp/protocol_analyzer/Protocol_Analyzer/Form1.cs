using System;
using System.Drawing;
using System.Management;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            BuildUI();
        }
    
        private void BuildUI()
        {
            this.Text = "Session Perf";
            this.Size = new Size(800, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // holder for Setting    
            var detectedSettingsGroup = CreateDetectedSettingsGroup(new Point(20, 20));
            this.Controls.Add(detectedSettingsGroup);             
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

            var visualQuality = CreateLabel("Visual Quality:", new Point(15, 30));
            var visualQualityValue = CreateBoldLabel("Medium", new Point(150, 30));

            var maxFps = CreateLabel("Max Frames p/s:", new Point(15, 55));
            var maxFpsValue = CreateBoldLabel("30", new Point(150, 55));

            var encoderType = CreateLabel("Encoder type:", new Point(15, 80));
            var encoderTypeValue = CreateBoldLabel("H265 (Yuv420)", new Point(150, 80));

            var hwEncode = CreateLabel("Hardware Encode:", new Point(15, 105));
            var hwEncodeValue = CreateBoldLabel("Inactive", new Point(150, 105));

            group.Controls.AddRange(new Control[]
            {
                visualQuality, visualQualityValue,
                maxFps, maxFpsValue,
                encoderType, encoderTypeValue,
                hwEncode, hwEncodeValue
            });

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

        

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
        }
    }
}
