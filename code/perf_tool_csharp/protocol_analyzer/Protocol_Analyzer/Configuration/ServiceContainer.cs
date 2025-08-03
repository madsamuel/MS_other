using Protocol_Analyzer.Services;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Configuration
{
    public static class ServiceContainer
    {
        private static readonly Dictionary<Type, object> _services = new();
        private static readonly object _lock = new();

        public static void RegisterServices()
        {
            lock (_lock)
            {
                // Register services
                Register<IResourceService>(new ResourceService());
                Register<IGpuInformationService>(new GpuInformationService());
                Register<IDetectedSettingsService>(new DetectedSettingsService());
                Register<IRealTimeStatisticsService>(new RealTimeStatisticsService());
                Register<ISessionInfoService>(new SessionInfoService());
                Register<ICustomSettingsService>(new CustomSettingsService());
                Register<ITrayIconService>(new TrayIconService(GetService<IResourceService>()));
                Register<ISystemInformationService>(new SystemInformationService(
                    GetService<IGpuInformationService>(),
                    GetService<IDetectedSettingsService>(),
                    GetService<IRealTimeStatisticsService>(),
                    GetService<ISessionInfoService>(),
                    GetService<ICustomSettingsService>()));
            }
        }

        public static void Register<T>(T implementation) where T : class
        {
            _services[typeof(T)] = implementation;
        }

        public static T GetService<T>() where T : class
        {
            if (_services.TryGetValue(typeof(T), out var service))
            {
                return (T)service;
            }
            throw new InvalidOperationException($"Service of type {typeof(T).Name} is not registered.");
        }

        public static void Clear()
        {
            lock (_lock)
            {
                foreach (var service in _services.Values)
                {
                    if (service is IDisposable disposable)
                    {
                        disposable.Dispose();
                    }
                }
                _services.Clear();
            }
        }
    }
}
