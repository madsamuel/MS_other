using PProtocolAnalyzer.Helpers;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	public MainPage()
	{
		InitializeComponent();

		// Load GPU Information dynamically using the GPUInformation helper
		LoadGpuInformation();

		// Load Detected Settings dynamically (existing working code)
		LoadDetectedSettings();
	}

	private void LoadGpuInformation()
	{
		try
		{
			// Fetch GPU information using the helper (similar to WinForms pattern)
			var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
			var (sessionType, gpuType, encoderType, hwEncode) = GPUInformation.GetGraphicsProfileDetails();

			// Update labels with dynamic data - handle unknown values properly
			if (resolution.Width > 0 && resolution.Height > 0)
				MainDisplayResolutionLabel.Text = $"Main Display Resolution: {resolution.Width}x{resolution.Height}";
			else
				MainDisplayResolutionLabel.Text = "Main Display Resolution: Unknown";

			if (dpiScale > 0)
				DpiScaleLabel.Text = $"DPI Scale: {dpiScale * 100:F0} %";
			else
				DpiScaleLabel.Text = "DPI Scale: Unknown";

			SessionTypeLabel.Text = $"Session Type: {sessionType}";
			GpuTypeLabel.Text = $"GPU Type: {gpuType}";
			EncodingLabel.Text = $"Encoding: {encoderType}";
			HwEncodeLabel.Text = $"HW Encode: {hwEncode}";
		}
		catch (System.Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error loading GPU information: {ex.Message}");
			// Set fallback values
			MainDisplayResolutionLabel.Text = "Main Display Resolution: Unknown";
			DpiScaleLabel.Text = "DPI Scale: Unknown";
			SessionTypeLabel.Text = "Session Type: Unknown";
			GpuTypeLabel.Text = "GPU Type: Unknown";
			EncodingLabel.Text = "Encoding: Unknown";
			HwEncodeLabel.Text = "HW Encode: Unknown";
		}
	}

	private void LoadDetectedSettings()
	{
		try
		{
			// Fetch display resolution dynamically (existing working code)
			var (width, height) = DisplayInfoHelper.GetDisplayResolution();
			DisplayResolutionLabel.Text = $"Display Resolution: {width} x {height}";

			// Fetch display refresh rate dynamically (existing working code)
			var refreshRate = DisplayInfoHelper.GetDisplayRefreshRate();
			RefreshRateLabel.Text = $"Display Refresh Rate: {refreshRate} Hz";

			// Fetch scaling factor dynamically (existing working code)
			var scalingFactor = DisplayInfoHelper.GetScalingFactor();
			ScalingFactorLabel.Text = $"Scaling: {scalingFactor * 100:F0}%";
		}
		catch (System.Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error loading detected settings: {ex.Message}");
		}
	}
}
