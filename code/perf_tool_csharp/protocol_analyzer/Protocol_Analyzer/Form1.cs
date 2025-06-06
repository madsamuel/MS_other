using System;
using System.Drawing;
using System.Management;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace Protocol_Analyzer
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            BuildUI();
        }

        private void BuildUI()
        {
            this.Text = "Session Perf";
            this.Size = new Size(800, 800);
            this.StartPosition = FormStartPosition.CenterScreen;                         
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);                        
        }
    }
}
