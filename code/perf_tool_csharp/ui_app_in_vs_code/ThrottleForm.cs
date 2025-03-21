namespace TrafficThrottleApp;

using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows.Forms;

public partial class ThrottleForm : Form
{
    private const string WINDIVERT_DLL = "WinDivert64.dll";
        private IntPtr handle = IntPtr.Zero;
        private bool throttling = false;

        // DLL imports from WinDivert
        [DllImport(WINDIVERT_DLL, CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr WinDivertOpen(
            [MarshalAs(UnmanagedType.LPStr)] string filter,
            WinDivertLayer layer, short priority, ulong flags);

        [DllImport(WINDIVERT_DLL, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool WinDivertRecv(IntPtr handle, IntPtr packet,
            uint packetLen, out WinDivertAddress addr, ref uint recvLen);

        [DllImport(WINDIVERT_DLL, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool WinDivertSend(IntPtr handle, IntPtr packet,
            uint packetLen, ref WinDivertAddress addr, ref uint sendLen);

        [DllImport(WINDIVERT_DLL, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool WinDivertClose(IntPtr handle);

        [StructLayout(LayoutKind.Sequential)]
        public struct WinDivertAddress
        {
            public ulong Timestamp;
            public byte Layer;
            public byte Event;
            public ushort Sniffed;
            public uint Reserved1;
            public uint Reserved2;
        }

        public enum WinDivertLayer : uint
        {
            Network = 0, // Network layer
            NetworkForward = 1
        }

        public ThrottleForm()
        {
            InitializeComponent();
        }

        private void btnToggleThrottle_Click(object sender, EventArgs e)
        {
            if (!throttling)
            {
                throttling = true;
                btnToggleThrottle.Text = "Stop Throttling";
                Task.Run(() => StartThrottling());
            }
            else
            {
                throttling = false;
                btnToggleThrottle.Text = "Start Throttling";
            }
        }

        private void StartThrottling()
        {
            // Intercept all inbound traffic (adjust filter as needed)
            handle = WinDivertOpen("inbound", WinDivertLayer.Network, 0, 0);

            if (handle == IntPtr.Zero)
            {
                MessageBox.Show("Failed to open WinDivert handle.");
                throttling = false;
                return;
            }

            uint packetLen = 65535;
            IntPtr packet = Marshal.AllocHGlobal((int)packetLen);
            WinDivertAddress addr;

            try
            {
                while (throttling)
                {
                    uint recvLen = 0;
                    if (!WinDivertRecv(handle, packet, packetLen, out addr, ref recvLen))
                        continue;

                    // Simple throttling: Delay packet injection (e.g., 50 ms delay per packet)
                    Task.Delay(50).Wait();

                    uint sendLen = 0;
                    WinDivertSend(handle, packet, recvLen, ref addr, ref sendLen);
                }
            }
            finally
            {
                WinDivertClose(handle);
                Marshal.FreeHGlobal(packet);
            }
        }
}
