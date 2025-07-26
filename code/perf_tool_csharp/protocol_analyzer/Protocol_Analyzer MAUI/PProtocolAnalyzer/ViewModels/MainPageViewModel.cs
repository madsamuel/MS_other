using PProtocolAnalyzer.Models;
using PProtocolAnalyzer.Services;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PProtocolAnalyzer.ViewModels
{
    public class MainPageViewModel : INotifyPropertyChanged
    {
        private readonly ISystemInformationService _systemInformationService;
        private SystemInformation? _systemInformation;
        private bool _isLoading;
        private System.Timers.Timer? _refreshTimer;

        public MainPageViewModel(ISystemInformationService systemInformationService)
        {
            _systemInformationService = systemInformationService;
            LoadSystemInformationCommand = new Command(async () => await LoadSystemInformation());
            
            // Initialize timer for real-time statistics (like the WinForms version)
            _refreshTimer = new System.Timers.Timer(5000); // 5 seconds interval
            _refreshTimer.Elapsed += async (sender, e) => await RefreshRealTimeStatistics();
            _refreshTimer.AutoReset = true;
        }

        public SystemInformation? SystemInformation
        {
            get => _systemInformation;
            set => SetProperty(ref _systemInformation, value);
        }

        public bool IsLoading
        {
            get => _isLoading;
            set => SetProperty(ref _isLoading, value);
        }

        public ICommand LoadSystemInformationCommand { get; }

        public async Task LoadSystemInformation()
        {
            try
            {
                IsLoading = true;
                SystemInformation = await _systemInformationService.GetSystemInformationAsync();
                
                // Start the timer for real-time statistics updates
                _refreshTimer?.Start();
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading system information: {ex.Message}");
                // Could show user-friendly error message here
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task RefreshRealTimeStatistics()
        {
            try
            {
                if (SystemInformation != null)
                {
                    var updatedStats = await _systemInformationService.GetRealTimeStatisticsAsync();
                    
                    // Update on main thread
                    Microsoft.Maui.Controls.Application.Current?.Dispatcher.Dispatch(() =>
                    {
                        if (SystemInformation != null)
                        {
                            SystemInformation.RealTimeStatistics = updatedStats;
                        }
                    });
                }
            }
            catch (System.Exception ex)
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
