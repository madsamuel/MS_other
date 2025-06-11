using System;
using System.Drawing;
using System.Windows.Forms;

namespace Protocol_Analyzer
{
    public static class GPUInformation
    {
        public static (Size resolution, float dpiScale) GetMainDisplayInfo()
        {
            Size resolution = Screen.PrimaryScreen?.Bounds.Size ?? new Size(1920, 1080);
            float dpiScale = 1.0f;
            using (var g = Graphics.FromHwnd(IntPtr.Zero))
            {
                dpiScale = g.DpiX / 96f;
            }
            return (resolution, dpiScale);
        }
    }
}
