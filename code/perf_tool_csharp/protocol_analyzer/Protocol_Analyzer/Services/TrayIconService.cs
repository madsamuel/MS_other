using System.Windows.Forms;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class TrayIconService : ITrayIconService, IDisposable
    {
        private NotifyIcon? _trayIcon;
        private readonly IResourceService _resourceService;

        public TrayIconService(IResourceService resourceService)
        {
            _resourceService = resourceService ?? throw new ArgumentNullException(nameof(resourceService));
        }

        public void Initialize(Form parentForm)
        {
            if (_trayIcon != null)
                return;

            _trayIcon = new NotifyIcon();
            
            var icon = _resourceService.LoadIcon("Resources/banana.ico");
            _trayIcon.Icon = icon ?? SystemIcons.Application;
            _trayIcon.Text = "Phil's Session Perf";
            
            var contextMenu = new ContextMenuStrip();
            var exitItem = new ToolStripMenuItem("Exit");
            exitItem.Click += (s, e) => parentForm.Close();
            contextMenu.Items.Add(exitItem);
            _trayIcon.ContextMenuStrip = contextMenu;
        }

        public void Show()
        {
            if (_trayIcon != null)
                _trayIcon.Visible = true;
        }

        public void Hide()
        {
            if (_trayIcon != null)
                _trayIcon.Visible = false;
        }

        public void Dispose()
        {
            if (_trayIcon != null)
            {
                _trayIcon.Visible = false;
                _trayIcon.Dispose();
                _trayIcon = null;
            }
        }
    }
}
