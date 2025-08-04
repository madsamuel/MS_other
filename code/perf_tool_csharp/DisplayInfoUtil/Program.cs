using System.Drawing;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace DisplayInfoUtil;

internal static class Program
{
    private const int ENUM_CURRENT_SETTINGS = -1;
    private const int LOGPIXELSX = 88;
    private const float DEFAULT_DPI = 96.0f;

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    private static extern bool EnumDisplaySettings(string? lpszDeviceName, int iModeNum, ref DevMode lpDevMode);

    [DllImport("user32.dll")]
    private static extern bool SetProcessDPIAware();

    [DllImport("gdi32.dll")]
    private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    private struct DevMode
    {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmDeviceName;
        public ushort dmSpecVersion;
        public ushort dmDriverVersion;
        public ushort dmSize;
        public ushort dmDriverExtra;
        public uint dmFields;
        public int dmPositionX;
        public int dmPositionY;
        public uint dmDisplayOrientation;
        public uint dmDisplayFixedOutput;
        public short dmColor;
        public short dmDuplex;
        public short dmYResolution;
        public short dmTTOption;
        public short dmCollate;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmFormName;
        public ushort dmLogPixels;
        public uint dmBitsPerPel;
        public uint dmPelsWidth;
        public uint dmPelsHeight;
        public uint dmDisplayFlags;
        public uint dmDisplayFrequency;
        public uint dmICMMethod;
        public uint dmICMIntent;
        public uint dmMediaType;
        public uint dmDitherType;
        public uint dmReserved1;
        public uint dmReserved2;
        public uint dmPanningWidth;
        public uint dmPanningHeight;

        public static DevMode Create() => new() { dmSize = (ushort)Marshal.SizeOf<DevMode>() };
    }

    [STAThread]
    private static void Main()
    {
        SetProcessDPIAware();

        var displayInfo = GetDisplayInformation();
        PrintDisplayInformation(displayInfo);
    }

    private static DisplayInformation GetDisplayInformation()
    {
        var primaryScreen = Screen.PrimaryScreen;
        if (primaryScreen == null)
            throw new InvalidOperationException("No primary screen found.");

        var resolution = (primaryScreen.Bounds.Width, primaryScreen.Bounds.Height);
        var scalingFactor = GetScalingFactor();
        var refreshRate = GetRefreshRate();

        return new DisplayInformation(resolution, scalingFactor, refreshRate);
    }

    private static float GetScalingFactor()
    {
        try
        {
            using var graphics = Graphics.FromHwnd(IntPtr.Zero);
            var hdc = graphics.GetHdc();
            try
            {
                var dpiX = GetDeviceCaps(hdc, LOGPIXELSX);
                return dpiX > 0 ? dpiX / DEFAULT_DPI : 1.0f;
            }
            finally
            {
                graphics.ReleaseHdc(hdc);
            }
        }
        catch
        {
            return 1.0f; // Fallback to 100% scaling
        }
    }

    private static int? GetRefreshRate()
    {
        try
        {
            var mode = DevMode.Create();
            return EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref mode) && mode.dmDisplayFrequency > 0
                ? (int)mode.dmDisplayFrequency
                : null;
        }
        catch
        {
            return null;
        }
    }

    private static void PrintDisplayInformation(DisplayInformation info)
    {
        Console.WriteLine("Primary Display:");
        Console.WriteLine($"  Resolution   : {info.Resolution.Width} x {info.Resolution.Height}");
        Console.WriteLine($"  Scaling      : {info.ScalingFactor * 100:F0}%");
        Console.WriteLine($"  Refresh Rate : {(info.RefreshRate?.ToString() ?? "Unknown")} Hz");
    }

    private readonly record struct DisplayInformation(
        (int Width, int Height) Resolution,
        float ScalingFactor,
        int? RefreshRate);
}
