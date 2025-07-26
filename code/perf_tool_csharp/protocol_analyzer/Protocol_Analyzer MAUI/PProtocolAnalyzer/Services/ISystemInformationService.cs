using PProtocolAnalyzer.Models;
using System.Threading.Tasks;

namespace PProtocolAnalyzer.Services
{
    public interface ISystemInformationService
    {
        Task<SystemInformation> GetSystemInformationAsync();
        Task<GpuInformation> GetGpuInformationAsync();
        Task<DetectedSettings> GetDetectedSettingsAsync();
        Task<RealTimeStatistics> GetRealTimeStatisticsAsync();
        Task<SessionInfo> GetSessionInfoAsync();
        Task<CustomSettings> GetCustomSettingsAsync();
    }
}
