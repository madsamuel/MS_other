using PProtocolAnalyzer.Helpers;
using System.Linq;
using System.Runtime.Versioning;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	private const string CUSTOM_SETTINGS_HEADER = "Custom Settings";
	private readonly Color _primaryTextColor = Colors.White;
	private readonly Color _errorTextColor = Colors.Red;
	private System.Timers.Timer? _realTimeStatsTimer;

	public MainPage()
	{
		try
		{
			InitializeComponent();
			LoadAllSections();
			InitializeRealTimeStats();
		}
		catch (Exception ex)
		{
			LogError("MainPage constructor", ex);
		}
	}

	[SupportedOSPlatform("windows")]
	private void InitializeRealTimeStats()
	{
		try
		{
			if (OperatingSystem.IsWindows())
			{
				// Initialize RemoteFX counters
				RealTimeStatisticsHelper.InitializeRemoteFXCounters();
				
				// Set up timer for real-time updates
				_realTimeStatsTimer = new System.Timers.Timer(1000); // Update every second
				_realTimeStatsTimer.Elapsed += OnRealTimeStatsTimerElapsed;
				_realTimeStatsTimer.AutoReset = true;
				_realTimeStatsTimer.Start();
			}
			else
			{
				// Set placeholder values for non-Windows platforms
				SetRealTimeStatsPlaceholder();
			}
		}
		catch (Exception ex)
		{
			LogError("InitializeRealTimeStats", ex);
			SetRealTimeStatsPlaceholder();
		}
	}

	[SupportedOSPlatform("windows")]
	private void OnRealTimeStatsTimerElapsed(object? sender, System.Timers.ElapsedEventArgs e)
	{
		try
		{
			if (OperatingSystem.IsWindows())
			{
				var stats = RealTimeStatisticsHelper.GetRemoteFXStats();
				
				// Update UI on main thread
				Dispatcher.Dispatch(() => UpdateRealTimeStatsUI(stats));
			}
		}
		catch (Exception ex)
		{
			LogError("OnRealTimeStatsTimerElapsed", ex);
		}
	}

	private void UpdateRealTimeStatsUI(RemoteFXNetworkStats stats)
	{
		try
		{
			if (stats.IsAvailable)
			{
				// Show authoritative total Bandwidth Output only (convert Kbps->Mbps when appropriate)
				string FormatBandwidth(float kbps)
				{
					if (kbps <= 999f)
						return $"{(int)Math.Round(kbps)} Kbps";
					else
						return $"{(kbps / 1000f):F2} Mbps";
				}

				BandwidthOutputLabel.Text = $"Bandwidth Output: {FormatBandwidth(stats.TotalBandwidthKbps)}";
				// Show Bandwidth Input using NIC received counters (format same as output)
				BandwidthInputLabel.Text = $"Bandwidth Input: {FormatBandwidth(stats.InputBandwidthKbps)}";
				
				// Clear existing session stats
				SessionStatsContainer.Children.Clear();
				
				// Add session statistics
				if (stats.Sessions.Length > 0)
				{
					foreach (var session in stats.Sessions)
					{
						var bandwidthLabel = CreateStyledLabel(
							$"UDP: {session.UdpBandwidthMBps:F2} MB/s | TCP: {session.TcpBandwidthMBps:F2} MB/s",
							_primaryTextColor);
						SessionStatsContainer.Children.Add(bandwidthLabel);
						
						var rttLabel = CreateStyledLabel(
							$"Round Trip Latency: {session.RttMs:F0} ms",
							_primaryTextColor);
						SessionStatsContainer.Children.Add(rttLabel);
					}
				}
				else
				{
					var noSessionsLabel = CreateStyledLabel("No active RemoteFX sessions", _primaryTextColor);
					SessionStatsContainer.Children.Add(noSessionsLabel);
				}
			}
			else
			{
				BandwidthOutputLabel.Text = $"Bandwidth Output: {stats.ErrorMessage}";
				BandwidthInputLabel.Text = "Bandwidth Input: Not available";
				
				SessionStatsContainer.Children.Clear();
				var errorLabel = CreateStyledLabel($"RemoteFX counters not available: {stats.ErrorMessage}", _errorTextColor);
				SessionStatsContainer.Children.Add(errorLabel);
			}
		}
		catch (Exception ex)
		{
			LogError("UpdateRealTimeStatsUI", ex);
		}
	}

	private void SetRealTimeStatsPlaceholder()
	{
	BandwidthOutputLabel.Text = "Bandwidth Output: Not available on this platform";
	BandwidthInputLabel.Text = "Bandwidth Input: Not available on this platform";
		
		SessionStatsContainer.Children.Clear();
		var placeholderLabel = CreateStyledLabel("RemoteFX statistics only available on Windows", _primaryTextColor);
		SessionStatsContainer.Children.Add(placeholderLabel);
	}

	protected override void OnDisappearing()
	{
		try
		{
			_realTimeStatsTimer?.Stop();
			_realTimeStatsTimer?.Dispose();
			
			if (OperatingSystem.IsWindows())
			{
				RealTimeStatisticsHelper.Dispose();
			}
		}
		catch (Exception ex)
		{
			LogError("OnDisappearing", ex);
		}
		
		base.OnDisappearing();
	}

	private void LoadAllSections()
	{
		LoadGpuInformation();
		LoadDetectedSettings();
		LoadSessionInformation();
		LoadCustomSettings();
	}

	private static void LogError(string context, Exception ex)
	{
		var message = $"Error in {context}: {ex.Message}";
		Console.WriteLine(message);
		System.Diagnostics.Debug.WriteLine(message);
	}

	private void LoadGpuInformation()
	{
		try
		{
			var (resolution, dpiScale) = GPUInformation.GetMainDisplayInfo();
			var (sessionType, gpuType, encoderType, hwEncode) = GPUInformation.GetGraphicsProfileDetails();

			SetLabelText(MainDisplayResolutionLabel, "Main Display Resolution", 
				resolution.Width > 0 && resolution.Height > 0 ? $"{resolution.Width}x{resolution.Height}" : "Unknown");
			
			SetLabelText(DpiScaleLabel, "DPI Scale", 
				dpiScale > 0 ? $"{dpiScale * 100:F0} %" : "Unknown");
			
			SetLabelText(SessionTypeLabel, "Session Type", sessionType);
			SetLabelText(GpuTypeLabel, "GPU Type", gpuType);
			SetLabelText(EncodingLabel, "Encoding", encoderType);
			SetLabelText(HwEncodeLabel, "HW Encode", hwEncode);
		}
		catch (Exception ex)
		{
			LogError("LoadGpuInformation", ex);
			SetGpuInformationFallbackValues();
		}
	}

	private void SetGpuInformationFallbackValues()
	{
		SetLabelText(MainDisplayResolutionLabel, "Main Display Resolution", "Unknown");
		SetLabelText(DpiScaleLabel, "DPI Scale", "Unknown");
		SetLabelText(SessionTypeLabel, "Session Type", "Unknown");
		SetLabelText(GpuTypeLabel, "GPU Type", "Unknown");
		SetLabelText(EncodingLabel, "Encoding", "Unknown");
		SetLabelText(HwEncodeLabel, "HW Encode", "Unknown");
	}

	private static void SetLabelText(Label label, string prefix, string value)
	{
		label.Text = $"{prefix}: {value}";
	}

	private void LoadDetectedSettings()
	{
		try
		{
			var (width, height) = DisplayInfoHelper.GetDisplayResolution();
			var refreshRate = DisplayInfoHelper.GetDisplayRefreshRate();
			var scalingFactor = DisplayInfoHelper.GetScalingFactor();
			var visualQuality = DetectedSettingsHelper.GetVisualQuality();
			var maxFps = DetectedSettingsHelper.GetMaxFPS();
			var hwEncodeSupported = DetectedSettingsHelper.IsHardwareEncodingSupported();
			var encoderType = DetectedSettingsHelper.GetEncoderType();

			SetLabelText(DisplayResolutionLabel, "Display Resolution", $"{width} x {height}");
			SetLabelText(RefreshRateLabel, "Display Refresh Rate", $"{refreshRate} Hz");
			SetLabelText(ScalingFactorLabel, "Scaling", $"{scalingFactor * 100:F0}%");
			SetLabelText(VisualQualityLabel, "Visual Quality", visualQuality);
			SetLabelText(MaxFramesLabel, "Max Frames p/s", maxFps.ToString());
			SetLabelText(HardwareEncodeStatusLabel, "Hardware Encode", hwEncodeSupported ? "Active" : "Inactive");
			SetLabelText(EncoderTypeLabel, "Encoder type", encoderType);
		}
		catch (Exception ex)
		{
			LogError("LoadDetectedSettings", ex);
		}
	}

	private void LoadSessionInformation()
	{
		try
		{
			var (sessionId, clientName, protocolVersion) = SessionInfoHelper.GetSessionInfo();
			
			SetLabelText(SessionIdLabel, "Session Id", sessionId);
			SetLabelText(ClientNameLabel, "Client Name", clientName);
			SetLabelText(ProtocolVersionLabel, "Protocol Version", protocolVersion);
		}
		catch (Exception ex)
		{
			LogError("LoadSessionInformation", ex);
			SetSessionInformationFallbackValues();
		}
	}

	private void SetSessionInformationFallbackValues()
	{
		SetLabelText(SessionIdLabel, "Session Id", "Unknown");
		SetLabelText(ClientNameLabel, "Client Name", "Unknown");
		SetLabelText(ProtocolVersionLabel, "Protocol Version", "Unknown");
	}

	private void LoadCustomSettings()
	{
		try
		{
			ClearExistingCustomSettings();
			var customSettings = CustomSettingsHelper.GetAllCustomSettings();
			
			if (customSettings?.Any() == true)
			{
				AddCustomSettingsToUI(customSettings);
			}
			else
			{
				AddNoSettingsMessage();
			}
		}
		catch (Exception ex)
		{
			LogError("LoadCustomSettings", ex);
			AddErrorMessage($"Error loading custom settings: {ex.Message}");
		}
	}

	private void ClearExistingCustomSettings()
	{
		var itemsToRemove = CustomSettingsContainer.Children
			.OfType<Label>()
			.Where(label => label.Text != CUSTOM_SETTINGS_HEADER)
			.ToList();
		
		foreach (var item in itemsToRemove)
		{
			CustomSettingsContainer.Children.Remove(item);
		}
	}

	private void AddCustomSettingsToUI(IEnumerable<string> settings)
	{
		foreach (var setting in settings)
		{
			var label = CreateStyledLabel(setting, _primaryTextColor);
			CustomSettingsContainer.Children.Add(label);
		}
	}

	private void AddNoSettingsMessage()
	{
		var message = CreateStyledLabel("No custom settings configured", _primaryTextColor);
		CustomSettingsContainer.Children.Add(message);
	}

	private void AddErrorMessage(string errorText)
	{
		var errorLabel = CreateStyledLabel(errorText, _errorTextColor);
		CustomSettingsContainer.Children.Add(errorLabel);
	}

	private static Label CreateStyledLabel(string text, Color textColor)
	{
		return new Label
		{
			Text = text,
			TextColor = textColor
		};
	}
}
