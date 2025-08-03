using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Models;

namespace Protocol_Analyzer.UI.Controls
{
    public class DetectedSettingsPanel : GroupBox
    {
        private readonly Label _contentLabel;
        private DetectedSettings? _detectedSettings;

        public DetectedSettingsPanel()
        {
            InitializeComponent();
            _contentLabel = new Label();
            SetupContentLabel();
        }

        private void InitializeComponent()
        {
            Text = "Detected Settings";
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
        public DetectedSettings? DetectedSettings
        {
            get => _detectedSettings;
            set
            {
                if (_detectedSettings != null)
                    _detectedSettings.PropertyChanged -= OnDetectedSettingsChanged;
                
                _detectedSettings = value;
                
                if (_detectedSettings != null)
                    _detectedSettings.PropertyChanged += OnDetectedSettingsChanged;
                
                UpdateDisplay();
            }
        }

        private void OnDetectedSettingsChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (InvokeRequired)
                Invoke(UpdateDisplay);
            else
                UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            if (_detectedSettings == null)
            {
                _contentLabel.Text = "Loading...";
                return;
            }

            _contentLabel.Text = 
                $"Display Resolution: {(_detectedSettings.Width > 0 && _detectedSettings.Height > 0 ? $"{_detectedSettings.Width}x{_detectedSettings.Height}" : "Unknown")}\n" +
                $"Display Refresh Rate: {(_detectedSettings.RefreshRate > 0 ? $"{_detectedSettings.RefreshRate} Hz" : "Unknown")}\n" +
                $"Scaling: {_detectedSettings.ScalingFactor * 100:F0}%\n" +
                $"Visual Quality: {_detectedSettings.VisualQuality}\n" +
                $"Max Frames p/s: {_detectedSettings.MaxFps}\n" +
                $"Hardware Encode: {(_detectedSettings.HardwareEncodingSupported ? "Active" : "Inactive")}\n" +
                $"Encoder type: {_detectedSettings.EncoderType}";
        }
    }
}
