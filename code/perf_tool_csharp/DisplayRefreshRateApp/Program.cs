using System;
using System.Runtime.InteropServices;
using System.Management;

class DisplayRefreshRateUtility
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
    public struct DEVMODE
    {
        private const int CCHDEVICENAME = 32;
        private const int CCHFORMNAME = 32;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = CCHDEVICENAME)]
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
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = CCHFORMNAME)]
        public string dmFormName;

        public ushort dmLogPixels;
        public uint dmBitsPerPel;
        public uint dmPelsWidth;
        public uint dmPelsHeight;

        public uint dmDisplayFlags;
        public uint dmDisplayFrequency;

        // Other fields omitted for brevity
    }

    [DllImport("user32.dll")]
    public static extern bool EnumDisplaySettings(string deviceName, int modeNum, ref DEVMODE devMode);

    const int ENUM_CURRENT_SETTINGS = -1;

    static void Main()
    {
        DEVMODE devMode = new DEVMODE();
        devMode.dmSize = (ushort)Marshal.SizeOf(typeof(DEVMODE));

        if (EnumDisplaySettings(null, ENUM_CURRENT_SETTINGS, ref devMode))
        {
            Console.WriteLine("Resolution: {0}x{1}", devMode.dmPelsWidth, devMode.dmPelsHeight);
            Console.WriteLine("Refresh Rate: {0} Hz", devMode.dmDisplayFrequency);
        }
        else
        {
            Console.WriteLine("Failed to get display settings.");
        }
    }
}
