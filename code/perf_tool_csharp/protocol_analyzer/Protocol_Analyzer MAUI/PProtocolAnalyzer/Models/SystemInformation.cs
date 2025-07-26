using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace PProtocolAnalyzer.Models
{
    public class SystemInformation : INotifyPropertyChanged
    {
        private GpuInformation _gpuInformation = new();
        private DetectedSettings _detectedSettings = new();
        private RealTimeStatistics _realTimeStatistics = new();
        private SessionInfo _sessionInfo = new();
        private CustomSettings _customSettings = new();

        public GpuInformation GpuInformation
        {
            get => _gpuInformation;
            set => SetProperty(ref _gpuInformation, value);
        }

        public DetectedSettings DetectedSettings
        {
            get => _detectedSettings;
            set => SetProperty(ref _detectedSettings, value);
        }

        public RealTimeStatistics RealTimeStatistics
        {
            get => _realTimeStatistics;
            set => SetProperty(ref _realTimeStatistics, value);
        }

        public SessionInfo SessionInfo
        {
            get => _sessionInfo;
            set => SetProperty(ref _sessionInfo, value);
        }

        public CustomSettings CustomSettings
        {
            get => _customSettings;
            set => SetProperty(ref _customSettings, value);
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

    public class GpuInformation : INotifyPropertyChanged
    {
        private string _mainDisplayResolution = "Unknown";
        private string _dpiScale = "Unknown";
        private string _sessionType = "Unknown";
        private string _gpuType = "Unknown";
        private string _encoding = "Unknown";
        private string _hwEncode = "Unknown";

        public string MainDisplayResolution
        {
            get => _mainDisplayResolution;
            set => SetProperty(ref _mainDisplayResolution, value);
        }

        public string DpiScale
        {
            get => _dpiScale;
            set => SetProperty(ref _dpiScale, value);
        }

        public string SessionType
        {
            get => _sessionType;
            set => SetProperty(ref _sessionType, value);
        }

        public string GpuType
        {
            get => _gpuType;
            set => SetProperty(ref _gpuType, value);
        }

        public string Encoding
        {
            get => _encoding;
            set => SetProperty(ref _encoding, value);
        }

        public string HwEncode
        {
            get => _hwEncode;
            set => SetProperty(ref _hwEncode, value);
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

    public class DetectedSettings : INotifyPropertyChanged
    {
        private string _displayResolution = "Unknown";
        private string _displayRefreshRate = "Unknown";
        private string _scaling = "Unknown";
        private string _visualQuality = "Unknown";
        private string _maxFramesPerSecond = "Unknown";
        private string _hardwareEncode = "Unknown";
        private string _encoderType = "Unknown";

        public string DisplayResolution
        {
            get => _displayResolution;
            set => SetProperty(ref _displayResolution, value);
        }

        public string DisplayRefreshRate
        {
            get => _displayRefreshRate;
            set => SetProperty(ref _displayRefreshRate, value);
        }

        public string Scaling
        {
            get => _scaling;
            set => SetProperty(ref _scaling, value);
        }

        public string VisualQuality
        {
            get => _visualQuality;
            set => SetProperty(ref _visualQuality, value);
        }

        public string MaxFramesPerSecond
        {
            get => _maxFramesPerSecond;
            set => SetProperty(ref _maxFramesPerSecond, value);
        }

        public string HardwareEncode
        {
            get => _hardwareEncode;
            set => SetProperty(ref _hardwareEncode, value);
        }

        public string EncoderType
        {
            get => _encoderType;
            set => SetProperty(ref _encoderType, value);
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

    public class RealTimeStatistics : INotifyPropertyChanged
    {
        private string _encoderFramesDropped = "Waiting for data";
        private string _inputFramesPerSecond = "Waiting for data";

        public string EncoderFramesDropped
        {
            get => _encoderFramesDropped;
            set => SetProperty(ref _encoderFramesDropped, value);
        }

        public string InputFramesPerSecond
        {
            get => _inputFramesPerSecond;
            set => SetProperty(ref _inputFramesPerSecond, value);
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

    public class SessionInfo : INotifyPropertyChanged
    {
        private string _sessionId = "Unknown";
        private string _clientName = "Unknown";
        private string _protocolVersion = "Unknown";

        public string SessionId
        {
            get => _sessionId;
            set => SetProperty(ref _sessionId, value);
        }

        public string ClientName
        {
            get => _clientName;
            set => SetProperty(ref _clientName, value);
        }

        public string ProtocolVersion
        {
            get => _protocolVersion;
            set => SetProperty(ref _protocolVersion, value);
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

    public class CustomSettings : INotifyPropertyChanged
    {
        private string _settings = "No custom settings found.";

        public string Settings
        {
            get => _settings;
            set => SetProperty(ref _settings, value);
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
