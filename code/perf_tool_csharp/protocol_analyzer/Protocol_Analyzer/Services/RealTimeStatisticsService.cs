using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class RealTimeStatisticsService : IRealTimeStatisticsService
    {
        public int GetEncoderFramesDropped()
        {
            return RealTimeAdvancedStatistics.GetEncoderFramesDroppedFromWMI();
        }

        public int GetInputFramesPerSecond()
        {
            return RealTimeAdvancedStatistics.GetInputFramesPerSecondFromWMI();
        }
    }
}
