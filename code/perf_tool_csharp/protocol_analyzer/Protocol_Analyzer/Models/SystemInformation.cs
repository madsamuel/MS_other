using System.ComponentModel;
using System.Drawing;
using System.Runtime.CompilerServices;

namespace Protocol_Analyzer.Models
{
    public class SystemInformation : INotifyPropertyChanged
    {
        private GpuInformation _gpuInformation = new();
        private DetectedSettings _detectedSettings = new();
        private RealTimeStatistics _realTimeStatistics = new();
        private SessionInfo _sessionInfo = new();
        private List<CustomRegistrySetting> _customSettings = new();

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

        public List<CustomRegistrySetting> CustomSettings
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
        private Size _resolution = new(1920, 1080);
        private float _dpiScale = 1.0f;
        private string _sessionType = "Unknown";
        private string _gpuType = "Unknown";
        private string _encoderType = "Unknown";
        private bool _hardwareEncoding = false;

        public Size Resolution
        {
            get => _resolution;
            set => SetProperty(ref _resolution, value);
        }

        public float DpiScale
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

        public string EncoderType
        {
            get => _encoderType;
            set => SetProperty(ref _encoderType, value);
        }

        public bool HardwareEncoding
        {
            get => _hardwareEncoding;
            set => SetProperty(ref _hardwareEncoding, value);
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
        private int _width = 0;
        private int _height = 0;
        private int _refreshRate = 60;
        private float _scalingFactor = 1.0f;
        private string _visualQuality = "Unknown";
        private int _maxFps = 60;
        private bool _hardwareEncodingSupported = false;
        private string _encoderType = "Unknown";

        public int Width
        {
            get => _width;
            set => SetProperty(ref _width, value);
        }

        public int Height
        {
            get => _height;
            set => SetProperty(ref _height, value);
        }

        public int RefreshRate
        {
            get => _refreshRate;
            set => SetProperty(ref _refreshRate, value);
        }

        public float ScalingFactor
        {
            get => _scalingFactor;
            set => SetProperty(ref _scalingFactor, value);
        }

        public string VisualQuality
        {
            get => _visualQuality;
            set => SetProperty(ref _visualQuality, value);
        }

        public int MaxFps
        {
            get => _maxFps;
            set => SetProperty(ref _maxFps, value);
        }

        public bool HardwareEncodingSupported
        {
            get => _hardwareEncodingSupported;
            set => SetProperty(ref _hardwareEncodingSupported, value);
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
        private int _encoderFramesDropped = -1;
        private int _inputFramesPerSecond = -1;

        public int EncoderFramesDropped
        {
            get => _encoderFramesDropped;
            set => SetProperty(ref _encoderFramesDropped, value);
        }

        public int InputFramesPerSecond
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
        private int _sessionId = -1;
        private string _clientName = "Unknown";
        private string _protocolVersion = "Unknown";

        public int SessionId
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
}
