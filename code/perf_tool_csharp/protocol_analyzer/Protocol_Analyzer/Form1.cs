using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Configuration;
using Protocol_Analyzer.Services.Interfaces;
using Protocol_Analyzer.ViewModels;
using Protocol_Analyzer.UI.Controls;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        private readonly ITrayIconService _trayIconService = null!;
        private readonly IResourceService _resourceService = null!;
        private readonly MainViewModel _viewModel = null!;
        private TableLayoutPanel? _mainTable;
        private GpuInformationPanel? _gpuPanel;
        private DetectedSettingsPanel? _detectedPanel;
        private RealTimeStatisticsPanel? _statisticsPanel;
        private SessionInfoPanel? _sessionPanel;
        private CustomSettingsPanel? _customPanel;

        public Form1()
        {
            try
            {
                // Initialize services
                ServiceContainer.RegisterServices();
                
                _trayIconService = ServiceContainer.GetService<ITrayIconService>();
                _resourceService = ServiceContainer.GetService<IResourceService>();
                _viewModel = new MainViewModel(ServiceContainer.GetService<ISystemInformationService>());

                InitializeFormComponent();
                InitializeTrayIcon();
                _ = InitializeAsync();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error initializing application: {ex.Message}", "Initialization Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void InitializeFormComponent()
        {
            // Set form properties
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(1000, 700);
            Text = "Phil's Session Perf";
            FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false;
            BackColor = SystemColors.Control;

            // Load application icon
            var icon = _resourceService.LoadIcon("Resources/banana.ico");
            if (icon != null)
                Icon = icon;

            BuildDashboardUI();
        }

        private void InitializeTrayIcon()
        {
            _trayIconService.Initialize(this);
            _trayIconService.Show();
        }

        private async Task InitializeAsync()
        {
            await _viewModel.InitializeAsync();
            BindViewModelToControls();
        }

        private void BuildDashboardUI()
        {
            // TableLayoutPanel for main layout
            _mainTable = new TableLayoutPanel();
            _mainTable.Dock = DockStyle.Fill;
            _mainTable.ColumnCount = 2;
            _mainTable.RowCount = 3;
            _mainTable.Padding = new Padding(10);
            _mainTable.AutoSize = false;
            _mainTable.AutoSizeMode = AutoSizeMode.GrowAndShrink;
            _mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            _mainTable.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            _mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 50F));
            _mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));
            _mainTable.RowStyles.Add(new RowStyle(SizeType.Percent, 25F));

            // Create panels
            _gpuPanel = new GpuInformationPanel();
            _detectedPanel = new DetectedSettingsPanel();
            _statisticsPanel = new RealTimeStatisticsPanel();
            _sessionPanel = new SessionInfoPanel();
            _customPanel = new CustomSettingsPanel(ServiceContainer.GetService<ICustomSettingsService>());

            // Add controls to mainTable
            _mainTable.Controls.Add(_gpuPanel, 0, 0);
            _mainTable.Controls.Add(_detectedPanel, 1, 0);
            _mainTable.Controls.Add(_statisticsPanel, 0, 1);
            _mainTable.Controls.Add(_sessionPanel, 1, 1);
            _mainTable.Controls.Add(_customPanel, 0, 2);
            _mainTable.SetColumnSpan(_customPanel, 2);

            Controls.Add(_mainTable);
        }

        private void BindViewModelToControls()
        {
            if (_viewModel.SystemInformation == null) return;

            _gpuPanel!.GpuInformation = _viewModel.SystemInformation.GpuInformation;
            _detectedPanel!.DetectedSettings = _viewModel.SystemInformation.DetectedSettings;
            _statisticsPanel!.RealTimeStatistics = _viewModel.SystemInformation.RealTimeStatistics;
            _sessionPanel!.SessionInfo = _viewModel.SystemInformation.SessionInfo;
            _customPanel!.CustomSettings = _viewModel.SystemInformation.CustomSettings;
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
            _viewModel?.Dispose();
            _trayIconService?.Dispose();
            ServiceContainer.Clear();
        }
    }
}
