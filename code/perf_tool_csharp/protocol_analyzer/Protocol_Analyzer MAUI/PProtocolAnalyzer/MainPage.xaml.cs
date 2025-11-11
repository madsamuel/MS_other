using PProtocolAnalyzer.Helpers;
using Microsoft.Extensions.Logging;
using System.Linq;
using System.Runtime.Versioning;

namespace PProtocolAnalyzer;

public partial class MainPage : ContentPage
{
	private const string CUSTOM_SETTINGS_HEADER = "Custom Settings";
	private readonly Color _primaryTextColor = Colors.White;
	private readonly Color _errorTextColor = Colors.Red;
	private System.Timers.Timer? _realTimeStatsTimer;
	private readonly Microsoft.Extensions.Logging.ILogger<MainPage>? _logger;

	public MainPage(Microsoft.Extensions.Logging.ILogger<MainPage> logger)
	{
		_logger = logger;
		try
		{
			InitializeComponent();
			this.LoadAllSections();
			this.InitializeRealTimeStats();
		}
		catch (Exception ex)
		{
			this.LogError("MainPage constructor", ex);
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
				this.SetRealTimeStatsPlaceholder();
			}
		}
		catch (Exception ex)
		{
			this.LogError("InitializeRealTimeStats", ex);
			this.SetRealTimeStatsPlaceholder();
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
			this.LogError("OnRealTimeStatsTimerElapsed", ex);
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

				// Show Total observed throughput, Output (sent) and Input (received)
				this.BandwidthOutputLabel.Text = $"Bandwidth Output: {FormatBandwidth(stats.SentBandwidthKbps)}";
				// Show Bandwidth Input using NIC received counters (format same as output)
				this.BandwidthInputLabel.Text = $"Bandwidth Input: {FormatBandwidth(stats.InputBandwidthKbps)}";
				// Show available bandwidth (capacity - observed) when known
				if (stats.AvailableBandwidthKbps > 0)
				{
					this.AvailableBandwidthLabel.Text = $"Available Bandwidth: {FormatBandwidth(stats.AvailableBandwidthKbps)}";
				}
				else
				{
					this.AvailableBandwidthLabel.Text = $"Available Bandwidth: {stats.AvailableBandwidthFormatted}";
				}
				
				// Clear existing session stats
				this.SessionStatsContainer.Children.Clear();

				// (Per-adapter details removed; showing system total only)
				
				// Add session statistics
				if (stats.Sessions.Length > 0)
				{
					foreach (var session in stats.Sessions)
					{
						var rttLabel = CreateStyledLabel(
							$"Round Trip Latency: {session.RttMs:F0} ms",
							this._primaryTextColor);
						this.SessionStatsContainer.Children.Add(rttLabel);
					}
				}
				else
				{
					var noSessionsLabel = CreateStyledLabel("No active RemoteFX sessions", this._primaryTextColor);
					this.SessionStatsContainer.Children.Add(noSessionsLabel);
				}

				// Update advanced real-time statistics (encoder frames dropped, input FPS)
				try
				{
					var framesDropped = RealTimeStatisticsHelper.GetEncoderFramesDropped();
					var inputFps = RealTimeStatisticsHelper.GetInputFramesPerSecond();

					this.EncoderFramesDroppedLabel.Text = $"Encoder Frames Dropped: {(framesDropped >= 0 ? framesDropped.ToString(System.Globalization.CultureInfo.InvariantCulture) : "Unavailable")}";
					this.InputFpsLabel.Text = $"Input Frames Per Second: {(inputFps >= 0 ? inputFps.ToString(System.Globalization.CultureInfo.InvariantCulture) : "Unavailable")}";
				}
				catch
				{
					this.EncoderFramesDroppedLabel.Text = "Encoder Frames Dropped: (waiting for data)";
					this.InputFpsLabel.Text = "Input Frames Per Second: (waiting for data)";
				}
			}
			else
			{
				this.BandwidthOutputLabel.Text = $"Bandwidth Output: {stats.ErrorMessage}";
				this.BandwidthInputLabel.Text = "Bandwidth Input: Not available";
				
				this.SessionStatsContainer.Children.Clear();
				var errorLabel = CreateStyledLabel($"RemoteFX counters not available: {stats.ErrorMessage}", this._errorTextColor);
				this.SessionStatsContainer.Children.Add(errorLabel);
			}

				// Always update advanced stats labels (do not depend on RemoteFX counters)
				try
				{
					var framesDroppedAlways = RealTimeStatisticsHelper.GetEncoderFramesDropped();
					var inputFpsAlways = RealTimeStatisticsHelper.GetInputFramesPerSecond();

					this.EncoderFramesDroppedLabel.Text = $"Encoder Frames Dropped: {(framesDroppedAlways >= 0 ? framesDroppedAlways.ToString(System.Globalization.CultureInfo.InvariantCulture) : "Unavailable")}";
					this.InputFpsLabel.Text = $"Input Frames Per Second: {(inputFpsAlways >= 0 ? inputFpsAlways.ToString(System.Globalization.CultureInfo.InvariantCulture) : "Unavailable")}";
				}
				catch
				{
					// leave existing text if retrieval fails
				}
		}
		catch (Exception ex)
		{
			this.LogError("UpdateRealTimeStatsUI", ex);
		}
	}

	private void SetRealTimeStatsPlaceholder()
	{
		this.BandwidthOutputLabel.Text = "Bandwidth Output: Not available on this platform";
		this.BandwidthInputLabel.Text = "Bandwidth Input: Not available on this platform";
		
		this.SessionStatsContainer.Children.Clear();
		var placeholderLabel = CreateStyledLabel("RemoteFX statistics only available on Windows", this._primaryTextColor);
		this.SessionStatsContainer.Children.Add(placeholderLabel);
	}

	protected override void OnDisappearing()
	{
		try
		{
			this._realTimeStatsTimer?.Stop();
			this._realTimeStatsTimer?.Dispose();
			
			if (OperatingSystem.IsWindows())
			{
				RealTimeStatisticsHelper.Dispose();
			}
		}
		catch (Exception ex)
		{
			this.LogError("OnDisappearing", ex);
		}
		
		base.OnDisappearing();
	}

	private void LoadAllSections()
	{
		this.LoadGpuInformation();
		this.LoadDetectedSettings();
		this.LoadSessionInformation();
		this.LoadCustomSettings();
	}

	private void LogError(string context, Exception ex)
	{
		var message = $"Error in {context}: {ex.Message}";
		try { _logger?.LogError(ex, message); } catch { /* Logging should never crash the application */ }
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
			this.LogError("LoadGpuInformation", ex);
			this.SetGpuInformationFallbackValues();
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
			var hwEncodeSupported = DetectedSettingsHelper.IsHardwareEncodingSupported();
			var encoderType = DetectedSettingsHelper.GetEncoderType();

			SetLabelText(DisplayResolutionLabel, "Display Resolution", $"{width} x {height}");
			SetLabelText(RefreshRateLabel, "Display Refresh Rate", $"{refreshRate} Hz");
			SetLabelText(ScalingFactorLabel, "Scaling", $"{scalingFactor * 100:F0}%");
			SetLabelText(VisualQualityLabel, "Visual Quality", visualQuality);
			// Max Frames display removed; value computed by DetectedSettingsHelper if needed elsewhere.
			SetLabelText(HardwareEncodeStatusLabel, "Hardware Encode", hwEncodeSupported ? "Active" : "Inactive");
			SetLabelText(EncoderTypeLabel, "Encoder type", encoderType);
		}
		catch (Exception ex)
		{
			this.LogError("LoadDetectedSettings", ex);
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
			this.LogError("LoadSessionInformation", ex);
			this.SetSessionInformationFallbackValues();
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
			this.ClearExistingCustomSettings();
			var customSettings = CustomSettingsHelper.GetAllCustomSettings();
			
			if (customSettings?.Any() == true)
			{
				this.AddCustomSettingsToUI(customSettings);
			}
			else
			{
				this.AddNoSettingsMessage();
			}
		}
		catch (Exception ex)
		{
			this.LogError("LoadCustomSettings", ex);
			this.AddErrorMessage($"Error loading custom settings: {ex.Message}");
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
