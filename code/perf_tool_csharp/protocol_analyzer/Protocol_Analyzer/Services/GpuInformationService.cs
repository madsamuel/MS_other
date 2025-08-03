using System.Drawing;
using System.Windows.Forms;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class GpuInformationService : IGpuInformationService
    {
        public (Size resolution, float dpiScale) GetMainDisplayInfo()
        {
            Size resolution = Screen.PrimaryScreen?.Bounds.Size ?? new Size(1920, 1080);
            float dpiScale = 1.0f;
            
            using (var g = Graphics.FromHwnd(IntPtr.Zero))
            {
                dpiScale = g.DpiX / 96f;
            }
            
            return (resolution, dpiScale);
        }

        public (string sessionType, string gpuType, string encoderType, string hwEncode) GetGraphicsProfileDetails()
        {
            return GraphicsProfileHelper.GetGraphicsProfileDetails();
        }
    }
}
