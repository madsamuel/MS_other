using PProtocolAnalyzer.Helpers;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	public MainPage()
	{
		InitializeComponent();

		// Fetch display resolution dynamically
		var (width, height) = DisplayInfoHelper.GetDisplayResolution();
		DisplayResolutionLabel.Text = $"Display Resolution: {width} x {height}";

		// Fetch display refresh rate dynamically
		var refreshRate = DisplayInfoHelper.GetDisplayRefreshRate();
		RefreshRateLabel.Text = $"Display Refresh Rate: {refreshRate} Hz";
	}
}
