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
			Width = 700,
			Height = 480,  // Set to a height that better fits the content
			MinimumWidth = 700,
			MaximumWidth = 700,
			MinimumHeight = 480,  // Same as Height to prevent shrinking
			MaximumHeight = 480   // Same as Height to prevent growing
		};

#if WINDOWS
		// Position window at bottom right of screen
		window.Created += (s, e) =>
		{
			var displayInfo = DeviceDisplay.Current.MainDisplayInfo;
			var screenWidth = displayInfo.Width / displayInfo.Density;
			var screenHeight = displayInfo.Height / displayInfo.Density;
			
			window.X = (int)(screenWidth - 700 - 50); // Corrected for 700px width + 50px margin
			window.Y = (int)(screenHeight - 480 - 50); // Position based on new 480px height
		};
#endif

		return window;
	}
}