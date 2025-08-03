using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Models;

namespace Protocol_Analyzer.UI.Controls
{
    public class SessionInfoPanel : GroupBox
    {
        private readonly Label _contentLabel;
        private SessionInfo? _sessionInfo;

        public SessionInfoPanel()
        {
            InitializeComponent();
            _contentLabel = new Label();
            SetupContentLabel();
        }

        private void InitializeComponent()
        {
            Text = "Session Info";
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
        public SessionInfo? SessionInfo
        {
            get => _sessionInfo;
            set
            {
                if (_sessionInfo != null)
                    _sessionInfo.PropertyChanged -= OnSessionInfoChanged;
                
                _sessionInfo = value;
                
                if (_sessionInfo != null)
                    _sessionInfo.PropertyChanged += OnSessionInfoChanged;
                
                UpdateDisplay();
            }
        }

        private void OnSessionInfoChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
        {
            if (InvokeRequired)
                Invoke(UpdateDisplay);
            else
                UpdateDisplay();
        }

        private void UpdateDisplay()
        {
            if (_sessionInfo == null)
            {
                _contentLabel.Text = "Loading...";
                return;
            }

            _contentLabel.Text = 
                $"Session Id: {_sessionInfo.SessionId}\n" +
                $"Client Name: {_sessionInfo.ClientName}\n" +
                $"Protocol Version: {_sessionInfo.ProtocolVersion}";
        }
    }
}
