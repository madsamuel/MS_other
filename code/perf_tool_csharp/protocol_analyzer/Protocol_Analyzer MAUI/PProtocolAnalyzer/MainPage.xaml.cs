using PProtocolAnalyzer.Helpers;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	public MainPage()
	{
		InitializeComponent();

		// Fetch display resolution dynamically
		var (width, height) = DisplayInfoHelper.GetDisplayResolution();

		// Update the UI
		DisplayResolutionLabel.Text = $"Display Resolution: {width} x {height}";
	}
}
