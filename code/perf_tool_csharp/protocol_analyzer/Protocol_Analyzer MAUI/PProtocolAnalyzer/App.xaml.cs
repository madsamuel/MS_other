using Microsoft.Maui;
using Microsoft.Maui.Controls;
using PProtocolAnalyzer.Services;
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
	
	// Delegate for window procedure
	private delegate IntPtr WndProcDelegate(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
	
	private TrayIcon? _trayIcon;
	private Microsoft.UI.Xaml.Window? _winUIWindow;
	private WndProcDelegate? _wndProcDelegate;
	
	[DllImport("user32.dll", SetLastError = true)]
	private static extern int GetWindowLong(IntPtr hWnd, int nIndex);
	
	[DllImport("user32.dll", SetLastError = true)]
	private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

	[DllImport("user32.dll", SetLastError = true)]
	private static extern IntPtr SetWindowLongPtr(IntPtr hWnd, int nIndex, IntPtr dwNewLong);

	[DllImport("user32.dll")]
	private static extern IntPtr CallWindowProc(IntPtr lpPrevWndFunc, IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

	private IntPtr _originalWndProc = IntPtr.Zero;
	
	private static void SetWindowStyle(IntPtr hwnd)
	{
		// Get current window style
		int style = GetWindowLong(hwnd, GWL_STYLE);
		// Remove minimize and maximize buttons
		style &= ~(WS_MINIMIZEBOX | WS_MAXIMIZEBOX);
		// Apply new style
		SetWindowLong(hwnd, GWL_STYLE, style);
	}

	private IntPtr WindowProc(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam)
	{
		// Handle tray icon messages
		if (_trayIcon != null && msg == 0x8000) // WM_TRAYICON
		{
			_trayIcon.HandleMessage((int)msg, lParam);
		}

		// Call original window procedure
		return CallWindowProc(_originalWndProc, hWnd, msg, wParam, lParam);
	}

	private void OnExitRequested()
	{
		// Close the application
		Current?.Quit();
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
				_winUIWindow = winUIWindow;
				var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(winUIWindow);
				SetWindowStyle(hwnd);
				
				// Set up custom window procedure to handle tray icon messages
				const int GWLP_WNDPROC = -4;
				_wndProcDelegate = WindowProc;
				_originalWndProc = SetWindowLongPtr(hwnd, GWLP_WNDPROC, 
					Marshal.GetFunctionPointerForDelegate(_wndProcDelegate));
				
				// Create and show tray icon
				_trayIcon = new TrayIcon(hwnd);
				_trayIcon.ExitRequested += OnExitRequested;
				_trayIcon.Show("Protocol Analyzer - Right-click for options");
			}
		};
#endif

		return window;
	}
}