using System;
using System.Runtime.InteropServices;


namespace DisplayInfoUtil
{
    class Program
    {
        // P/Invoke declaration
        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        private static extern bool EnumDisplaySettings(
            string lpszDeviceName,
            int iModeNum,
            ref DEVMODE lpDevMode);

        private const int ENUM_CURRENT_SETTINGS = -1;

        // Only fields we need; the rest can be omitted or left as padding
        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
        private struct DEVMODE
        {
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmDeviceName;
            public ushort dmSpecVersion;
            public ushort dmDriverVersion;
            public ushort dmSize;
            public ushort dmDriverExtra;
            public uint   dmFields;
            public int    dmPositionX;
            public int    dmPositionY;
            public uint   dmDisplayOrientation;
            public uint   dmDisplayFixedOutput;
            public short  dmColor;
            public short  dmDuplex;
            public short  dmYResolution;
            public short  dmTTOption;
            public short  dmCollate;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
            public string dmFormName;
            public ushort dmLogPixels;
            public uint   dmBitsPerPel;
            public uint   dmPelsWidth;
            public uint   dmPelsHeight;
            public uint   dmDisplayFlags;
            public uint   dmDisplayFrequency;
            public uint   dmICMMethod;
            public uint   dmICMIntent;
            public uint   dmMediaType;
            public uint   dmDitherType;
            public uint   dmReserved1;
            public uint   dmReserved2;
            public uint   dmPanningWidth;
            public uint   dmPanningHeight;
        }

        [STAThread]
        static void Main()
        {
            // 1) Get resolution via Screen.PrimaryScreen
            var screen = Screen.PrimaryScreen;
            int width  = screen.Bounds.Width;
            int height = screen.Bounds.Height;

            // Get scaling factor (DPI awareness)
            float scalingFactor = 1.0f;
            using (var g = System.Drawing.Graphics.FromHwnd(IntPtr.Zero))
            {
                float dpiX = g.DpiX;
                scalingFactor = dpiX / 96.0f; // 96 DPI is 100%
            }

            // 2) Get refresh rate via EnumDisplaySettings
            DEVMODE mode = new DEVMODE();
            mode.dmSize = (ushort)Marshal.SizeOf(mode);
            bool success = EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref mode);

            Console.WriteLine("Primary Display:");
            Console.WriteLine($"  Resolution : {width} x {height}");
            Console.WriteLine($"  Scaling    : {scalingFactor * 100:F0}%");
            if (success && mode.dmDisplayFrequency > 0)
            {
                Console.WriteLine($"  Refresh Rate: {mode.dmDisplayFrequency} Hz");
            }
            else
            {
                Console.WriteLine("  Refresh Rate: Unable to retrieve");
            }
        }
    }
}
