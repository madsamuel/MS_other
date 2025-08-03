using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class SessionInfoService : ISessionInfoService
    {
        public RdpStatsApp.RdpNative.RdpStatistics GetRdpStatistics()
        {
            return RdpStatsApp.RdpNative.GetRdpStatistics();
        }
    }
}
