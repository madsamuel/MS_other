using Microsoft.UI.Xaml;
using System;
using System.Runtime.InteropServices;

// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace PProtocolAnalyzer.Platforms.Windows
{
    /// <summary>
    /// Provides application-specific behavior to supplement the default Application class.
    /// </summary>
    public partial class App : MauiWinUIApplication
    {
        /// <summary>
        /// Initializes the singleton application object.  This is the first line of authored code
        /// executed, and as such is the logical equivalent of main() or WinMain().
        /// </summary>
        public App()
        {
            this.InitializeComponent();
        }

        protected override MauiApp CreateMauiApp() => MauiProgram.CreateMauiApp();
    }

    public partial class MainWindow : Microsoft.UI.Xaml.Window
    {
        [DllImport("user32.dll", SetLastError = true)]
        private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        private const uint WM_SETICON = 0x0080;
        private const int ICON_SMALL = 0;
        private const int ICON_BIG = 1;

        public MainWindow()
        {
            this.InitializeComponent();

            IntPtr hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
            IntPtr hIcon = LoadIcon("banana.ico");

            // Set the small and large icons
            SendMessage(hWnd, WM_SETICON, (IntPtr)ICON_SMALL, hIcon);
            SendMessage(hWnd, WM_SETICON, (IntPtr)ICON_BIG, hIcon);
        }

        private IntPtr LoadIcon(string iconPath)
        {
            // Load the icon from the file
            return Marshal.AllocHGlobal(0); // Replace with actual icon loading logic
        }
    }
}

