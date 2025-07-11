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

        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();

        [DllImport("gdi32.dll")]
        private static extern int GetDeviceCaps(IntPtr hdc, int nIndex);

        private const int LOGPIXELSX = 88;

        [STAThread]
        static void Main()
        {

            // Ensure process is DPI aware to get real DPI (prevents Windows DPI virtualization)
            SetProcessDPIAware();


            // 1) Get primary screen resolution
            var screen = Screen.PrimaryScreen;
            int width = screen.Bounds.Width;
            int height = screen.Bounds.Height;


            // 2) Get scaling factor (DPI awareness)
            // This uses the device context to get the actual DPI for the primary monitor
            float scalingFactor = 1.0f;
            try
            {
                using (var g = System.Drawing.Graphics.FromHwnd(IntPtr.Zero))
                {
                    IntPtr hdc = g.GetHdc();
                    int dpiX = GetDeviceCaps(hdc, LOGPIXELSX); // Get horizontal DPI
                    if (dpiX > 0)
                    {
                        scalingFactor = dpiX / 96.0f; // 96 DPI is 100% scaling
                    }
                    else
                    {
                        // Fallback if DPI could not be retrieved
                        Console.WriteLine("Warning: Unable to retrieve DPI. Defaulting to 100% scaling.");
                    }
                    g.ReleaseHdc(hdc);
                }
            }
            catch (Exception ex)
            {
                // Handle any errors in DPI retrieval
                Console.WriteLine($"Error retrieving DPI: {ex.Message}");
                scalingFactor = 1.0f;
            }


            // 3) Get refresh rate using EnumDisplaySettings
            int refreshRate = -1;
            try
            {
                DEVMODE mode = new DEVMODE();
                mode.dmSize = (ushort)Marshal.SizeOf(mode);
                bool success = EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref mode); // Query current display mode

                // Output display information
                Console.WriteLine("Primary Display:");
                Console.WriteLine($"  Resolution : {width} x {height}");
                Console.WriteLine($"  Scaling    : {scalingFactor * 100:F0}%");

                if (success && mode.dmDisplayFrequency > 0)
                {
                    refreshRate = (int)mode.dmDisplayFrequency;
                    Console.WriteLine($"  Refresh Rate: {refreshRate} Hz");
                }
                else
                {
                    // Fallback if refresh rate could not be retrieved
                    Console.WriteLine("  Refresh Rate: Unable to retrieve");
                }
            }
            catch (Exception ex)
            {
                // Handle any errors in refresh rate retrieval
                Console.WriteLine($"Error retrieving refresh rate: {ex.Message}");
            }
        }
    }
}
