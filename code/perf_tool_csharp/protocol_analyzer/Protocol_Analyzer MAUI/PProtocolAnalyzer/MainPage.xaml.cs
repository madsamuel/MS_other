using PProtocolAnalyzer.Helpers;
using System.Linq;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	public MainPage()
	{
		try
		{
			InitializeComponent();

			// Load dynamic data for all sections
			LoadGpuInformation();
			LoadDetectedSettings();
			LoadSessionInformation();
			LoadCustomSettings();
		}
		catch (Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error in MainPage constructor: {ex.Message}");
			System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
		}
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

			// NEW: Fetch Visual Quality dynamically using enhanced DetectedSettingsHelper
			var visualQuality = DetectedSettingsHelper.GetVisualQuality();
			VisualQualityLabel.Text = $"Visual Quality: {visualQuality}";

			// NEW: Fetch Max Frames dynamically using enhanced DetectedSettingsHelper
			var maxFps = DetectedSettingsHelper.GetMaxFPS();
			MaxFramesLabel.Text = $"Max Frames p/s: {maxFps}";

			// NEW: Fetch Hardware Encoding status dynamically
			var hwEncodeSupported = DetectedSettingsHelper.IsHardwareEncodingSupported();
			HardwareEncodeStatusLabel.Text = $"Hardware Encode: {(hwEncodeSupported ? "Active" : "Inactive")}";

			// NEW: Fetch Encoder Type dynamically
			var encoderType = DetectedSettingsHelper.GetEncoderType();
			EncoderTypeLabel.Text = $"Encoder type: {encoderType}";
		}
		catch (System.Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error loading detected settings: {ex.Message}");
		}
	}

	private void LoadSessionInformation()
	{
		try
		{
			// NEW: Fetch Session Information dynamically using SessionInfoHelper
			var (sessionId, clientName, protocolVersion) = SessionInfoHelper.GetSessionInfo();
			
			SessionIdLabel.Text = $"Session Id: {sessionId}";
			ClientNameLabel.Text = $"Client Name: {clientName}";
			ProtocolVersionLabel.Text = $"Protocol Version: {protocolVersion}";
		}
		catch (System.Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error loading session information: {ex.Message}");
			// Set fallback values
			SessionIdLabel.Text = "Session Id: Unknown";
			ClientNameLabel.Text = "Client Name: Unknown";
			ProtocolVersionLabel.Text = "Protocol Version: Unknown";
		}
	}

	private void LoadCustomSettings()
	{
		try
		{
			System.Diagnostics.Debug.WriteLine("LoadCustomSettings: Starting...");
			
			// Clear any existing custom settings labels (except the header)
			var childrenToRemove = CustomSettingsContainer.Children
				.Where(child => child is Label label && label.Text != "Custom Settings")
				.ToList();
			
			foreach (var child in childrenToRemove)
			{
				CustomSettingsContainer.Children.Remove(child);
			}

			System.Diagnostics.Debug.WriteLine("LoadCustomSettings: Cleared existing labels");

			// Add a test label to verify this method is being called
			var testLabel = new Label
			{
				Text = "LoadCustomSettings method called successfully!",
				TextColor = (Color)Resources["DarkText"]
			};
			CustomSettingsContainer.Children.Add(testLabel);

			// NEW: Fetch Custom Settings dynamically using CustomSettingsHelper
			var customSettings = CustomSettingsHelper.GetAllCustomSettings();
			
			System.Diagnostics.Debug.WriteLine($"LoadCustomSettings: Got {customSettings?.Count ?? 0} custom settings");
			
			// Add each custom setting as a separate label
			if (customSettings != null)
			{
				foreach (var setting in customSettings)
				{
					System.Diagnostics.Debug.WriteLine($"LoadCustomSettings: Adding setting: {setting}");
					var label = new Label
					{
						Text = setting,
						TextColor = (Color)Resources["DarkText"]
					};
					CustomSettingsContainer.Children.Add(label);
				}
			}
			else
			{
				System.Diagnostics.Debug.WriteLine("LoadCustomSettings: customSettings is null");
				// Add a debug label to show that we tried but failed
				var debugLabel = new Label
				{
					Text = "Custom settings could not be loaded - customSettings is null",
					TextColor = (Color)Resources["DarkText"]
				};
				CustomSettingsContainer.Children.Add(debugLabel);
			}
		}
		catch (System.Exception ex)
		{
			System.Diagnostics.Debug.WriteLine($"Error loading custom settings: {ex.Message}");
			System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
			// Add fallback label
			var fallbackLabel = new Label
			{
				Text = $"Error loading custom settings: {ex.Message}",
				TextColor = (Color)Resources["DarkText"]
			};
			CustomSettingsContainer.Children.Add(fallbackLabel);
		}
	}
}
