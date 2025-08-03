using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Models;

namespace Protocol_Analyzer.UI.Controls
{
    public class RealTimeStatisticsPanel : GroupBox
    {
        private readonly Label _contentLabel;
        private RealTimeStatistics? _statistics;

        public RealTimeStatisticsPanel()
        {
            InitializeComponent();
            _contentLabel = new Label();
            SetupContentLabel();
        }

        private void InitializeComponent()
        {
            Text = "Real-Time Advanced Statistics";
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
        public RealTimeStatistics? RealTimeStatistics
        {
            get => _statistics;
            set
            {
                if (_statistics != null)
                    _statistics.PropertyChanged -= OnStatisticsChanged;
                
                _statistics = value;
                
                if (_statistics != null)
                    _statistics.PropertyChanged += OnStatisticsChanged;
                
                UpdateDisplay();
            }
        }

        private void OnStatisticsChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (InvokeRequired)
                Invoke(UpdateDisplay);
            else
                UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            if (_statistics == null)
            {
                _contentLabel.Text = "Loading...";
                return;
            }

            _contentLabel.Text = 
                $"Encoder Frames Dropped: {(_statistics.EncoderFramesDropped >= 0 ? _statistics.EncoderFramesDropped.ToString() : "Unavailable")}\n" +
                $"Input Frames Per Second: {(_statistics.InputFramesPerSecond >= 0 ? _statistics.InputFramesPerSecond.ToString() : "Unavailable")}";
        }
    }
}
