using Microsoft.Maui;
using Microsoft.Maui.Controls;
using System.Runtime.InteropServices;

#if WINDOWS
using Microsoft.UI;
using Microsoft.UI.Windowing;
using WinRT.Interop;
#endif

namespace PProtocolAnalyzer;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		var window = new Window(new AppShell());

		#if WINDOWS
		window.Created += (s, e) =>
		{
			var mauiWinUIWindow = window.Handler?.PlatformView as Microsoft.UI.Xaml.Window;
			if (mauiWinUIWindow is not null)
			{
				var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(mauiWinUIWindow);
				var windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(hwnd);
				var appWindow = AppWindow.GetFromWindowId(windowId);
				var displayArea = DisplayArea.GetFromWindowId(appWindow.Id, DisplayAreaFallback.Primary);
				var workArea = displayArea.WorkArea;

				// Set desired width and height (adjust as needed or calculate based on content)
				int width = 700; // Example width
				int height = 600; // Example height

				// Position window in bottom right
				int x = workArea.X + workArea.Width - width;
				int y = workArea.Y + workArea.Height - height;

				appWindow.MoveAndResize(new Windows.Graphics.RectInt32(x, y, width, height));
			}
		};
		#endif
		return window;
	}
}

public partial class MainWindow : Microsoft.UI.Xaml.Window
{
    public MainWindow()
    {
        IntPtr hWnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        IntPtr hIcon = LoadIcon("Resources\\Icons\\YourIcon.ico");

        // Set the small and large icons
        SendMessage(hWnd, WM_SETICON, (IntPtr)ICON_SMALL, hIcon);
        SendMessage(hWnd, WM_SETICON, (IntPtr)ICON_BIG, hIcon);
    }

    private IntPtr LoadIcon(string iconPath)
    {
        // Load the icon from the file
        return Marshal.AllocHGlobal(0); // Replace with actual icon loading logic
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

    private const uint WM_SETICON = 0x0080;
    private const int ICON_SMALL = 0;
    private const int ICON_BIG = 1;
}