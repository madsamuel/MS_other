using System.ComponentModel;
using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.UI.Controls
{
    public class CustomSettingsPanel : GroupBox
    {
        private readonly Label _contentLabel;
        private readonly ICustomSettingsService _customSettingsService;
        private List<CustomRegistrySetting>? _customSettings;

        public CustomSettingsPanel(ICustomSettingsService customSettingsService)
        {
            _customSettingsService = customSettingsService ?? throw new ArgumentNullException(nameof(customSettingsService));
            InitializeComponent();
            _contentLabel = new Label();
            SetupContentLabel();
        }

        private void InitializeComponent()
        {
            Text = "Custom Settings";
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
        public List<CustomRegistrySetting>? CustomSettings
        {
            get => _customSettings;
            set
            {
                _customSettings = value;
                UpdateDisplay();
            }
        }

        private void UpdateDisplay()
        {
            if (_customSettings == null || _customSettings.Count == 0)
            {
                _contentLabel.Text = "No custom settings found.";
                return;
            }

            var displayStrings = _customSettings
                .Select(s => _customSettingsService.GetRegistryDisplay(s) ?? s.ToString() ?? string.Empty)
                .Where(s => !string.IsNullOrEmpty(s));

            _contentLabel.Text = string.Join("\n", displayStrings);
        }
    }
}
