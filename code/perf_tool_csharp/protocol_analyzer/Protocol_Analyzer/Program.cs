using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace Protocol_Analyzer
{
    internal static class Program
    {
        [DllImport("user32.dll")]
        private static extern int GetSystemMetrics(int nIndex);

        const int SM_REMOTESESSION = 0x1000;

        [STAThread]
        static void Main()
        {
            bool isRemoteSession = GetSystemMetrics(SM_REMOTESESSION) != 0;

            // Check if the application is running in a Remote Desktop session 
            // set to !isRemoteSession for production use
            if (!isRemoteSession)
            {
                MessageBox.Show(
                    "This application can only run in a Remote Desktop session.",
                    "Remote Desktop Required",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
                return;
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1());
        }
    }
}
