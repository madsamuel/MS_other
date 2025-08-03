using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Models;

namespace Protocol_Analyzer.UI.Controls
{
    public class GpuInformationPanel : GroupBox
    {
        private readonly Label _contentLabel;
        private GpuInformation? _gpuInformation;

        public GpuInformationPanel()
        {
            InitializeComponent();
            _contentLabel = new Label();
            SetupContentLabel();
        }

        private void InitializeComponent()
        {
            Text = "GPU Information";
            Dock = DockStyle.Fill;
            Font = new Font("Segoe UI", 10F, FontStyle.Bold);
        }

        private void SetupContentLabel()
        {
            _contentLabel.Font = new Font("Segoe UI", 11F, FontStyle.Regular);
            _contentLabel.AutoSize = false;
            _contentLabel.Dock = DockStyle.Fill;
            _contentLabel.TextAlign = ContentAlignment.TopLeft;
            Controls.Add(_contentLabel);
        }

        [Browsable(false)]
        [DesignerSerializationVisibility(DesignerSerializationVisibility.Hidden)]
        public GpuInformation? GpuInformation
        {
            get => _gpuInformation;
            set
            {
                if (_gpuInformation != null)
                    _gpuInformation.PropertyChanged -= OnGpuInformationChanged;
                
                _gpuInformation = value;
                
                if (_gpuInformation != null)
                    _gpuInformation.PropertyChanged += OnGpuInformationChanged;
                
                UpdateDisplay();
            }
        }

        private void OnGpuInformationChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (InvokeRequired)
                Invoke(UpdateDisplay);
            else
                UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            if (_gpuInformation == null)
            {
                _contentLabel.Text = "Loading...";
                return;
            }

            _contentLabel.Text = 
                $"Main Display Resolution: {_gpuInformation.Resolution.Width}x{_gpuInformation.Resolution.Height}\n" +
                $"DPI Scale: {_gpuInformation.DpiScale * 100:F0}%\n" +
                $"Session Type: {_gpuInformation.SessionType}\n" +
                $"GPU Type: {_gpuInformation.GpuType}\n" +
                $"Encoding: {_gpuInformation.EncoderType}\n" +
                $"HW Encode: {(_gpuInformation.HardwareEncoding ? "Yes" : "No")}";
        }
    }
}
