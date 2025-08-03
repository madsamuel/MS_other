using System.ComponentModel;
using System.Runtime.CompilerServices;
using Protocol_Analyzer.Models;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged, IDisposable
    {
        private readonly ISystemInformationService _systemInformationService;
        private readonly System.Windows.Forms.Timer _refreshTimer;
        private Models.SystemInformation _systemInformation;
        private bool _isLoading;

        public MainViewModel(ISystemInformationService systemInformationService)
        {
            _systemInformationService = systemInformationService ?? throw new ArgumentNullException(nameof(systemInformationService));
            _systemInformation = new Models.SystemInformation();
            
            _refreshTimer = new System.Windows.Forms.Timer();
            _refreshTimer.Interval = 5000; // 5 seconds
            _refreshTimer.Tick += async (s, e) => await RefreshRealTimeStatisticsAsync();
        }

        public Models.SystemInformation SystemInformation
        {
            get => _systemInformation;
            private set => SetProperty(ref _systemInformation, value);
        }

        public bool IsLoading
        {
            get => _isLoading;
            private set => SetProperty(ref _isLoading, value);
        }

        public async Task InitializeAsync()
        {
            IsLoading = true;
            try
            {
                SystemInformation = await _systemInformationService.GetSystemInformationAsync();
                _refreshTimer.Start();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error initializing system information: {ex.Message}");
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshRealTimeStatisticsAsync()
        {
            try
            {
                await _systemInformationService.RefreshRealTimeStatisticsAsync(SystemInformation);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error refreshing real-time statistics: {ex.Message}");
            }
        }

        public void Dispose()
        {
            _refreshTimer?.Stop();
            _refreshTimer?.Dispose();
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected bool SetProperty<T>(ref T backingField, T value, [CallerMemberName] string propertyName = "")
        {
            if (Equals(backingField, value))
                return false;

            backingField = value;
            OnPropertyChanged(propertyName);
            return true;
        }

        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = "")
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
