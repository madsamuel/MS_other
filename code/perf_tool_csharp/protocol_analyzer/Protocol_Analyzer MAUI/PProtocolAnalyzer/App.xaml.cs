using Microsoft.Maui;
using Microsoft.Maui.Controls;

namespace PProtocolAnalyzer;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
		var window = new Window(new AppShell())
		{
			Title = "Protocol Analyzer",
			Width = 900,
			MinimumWidth = 800,
			MaximumWidth = 1200,
			MinimumHeight = 400
			// Removed fixed Height and MaximumHeight to allow auto-sizing
		};

#if WINDOWS
		// Position window at bottom right of screen
		window.Created += (s, e) =>
		{
			var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
			var screenWidth = displayInfo.Width / displayInfo.Density;
			var screenHeight = displayInfo.Height / displayInfo.Density;
			
			window.X = (int)(screenWidth - 900);
			window.Y = (int)(screenHeight - 650); // Approximate position, will adjust with content
		};
#endif

		return window;
	}
}