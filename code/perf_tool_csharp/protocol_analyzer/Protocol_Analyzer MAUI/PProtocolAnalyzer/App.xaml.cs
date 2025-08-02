using Microsoft.Maui;
using Microsoft.Maui.Controls;
#if WINDOWS
using System.Runtime.InteropServices;
#endif

namespace PProtocolAnalyzer;

public partial class App : Application
{
#if WINDOWS
	// Win32 API constants and methods for window styling
	private const int GWL_STYLE = -16;
	private const int WS_MINIMIZEBOX = 0x20000;
	private const int WS_MAXIMIZEBOX = 0x10000;
	
	[DllImport("user32.dll", SetLastError = true)]
	private static extern int GetWindowLong(IntPtr hWnd, int nIndex);
	
	[DllImport("user32.dll", SetLastError = true)]
	private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
	
	private static void SetWindowStyle(IntPtr hwnd)
	{
		// Get current window style
		int style = GetWindowLong(hwnd, GWL_STYLE);
		// Remove minimize and maximize buttons
		style &= ~(WS_MINIMIZEBOX | WS_MAXIMIZEBOX);
		// Apply new style
		SetWindowLong(hwnd, GWL_STYLE, style);
	}
#endif

	public App()
	{
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		var window = new Window(new AppShell())
		{
			Title = "Protocol Analyzer",
			Width = 700,
			Height = 480,  // Set to a height that better fits the content
			MinimumWidth = 700,
			MaximumWidth = 700,
			MinimumHeight = 480,  // Same as Height to prevent shrinking
			MaximumHeight = 480   // Same as Height to prevent growing
		};

#if WINDOWS
		// Position window at bottom right of screen and configure window style
		window.Created += (s, e) =>
		{
			var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
			var screenWidth = displayInfo.Width / displayInfo.Density;
			var screenHeight = displayInfo.Height / displayInfo.Density;
			
			window.X = (int)(screenWidth - 700 - 50); // Corrected for 700px width + 50px margin
			window.Y = (int)(screenHeight - 480 - 50); // Position based on new 480px height
			
			// Remove minimize and maximize buttons (Windows only)
			if (window.Handler?.PlatformView is Microsoft.UI.Xaml.Window winUIWindow)
			{
				var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(winUIWindow);
				SetWindowStyle(hwnd);
			}
		};
#endif

		return window;
	}
}