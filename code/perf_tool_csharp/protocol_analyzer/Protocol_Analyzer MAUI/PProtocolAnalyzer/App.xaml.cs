using Microsoft.Maui;
using Microsoft.Maui.Controls;

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