namespace TrafficThrottleApp
{
    partial class ThrottleForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.Button btnToggleThrottle;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
                components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.btnToggleThrottle = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // btnToggleThrottle
            // 
            this.btnToggleThrottle.Location = new System.Drawing.Point(50, 30);
            this.btnToggleThrottle.Name = "btnToggleThrottle";
            this.btnToggleThrottle.Size = new System.Drawing.Size(150, 40);
            this.btnToggleThrottle.TabIndex = 0;
            this.btnToggleThrottle.Text = "Start Throttling";
            this.btnToggleThrottle.UseVisualStyleBackColor = true;
            this.btnToggleThrottle.Click += new System.EventHandler(this.btnToggleThrottle_Click);
            // 
            // ThrottleForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(250, 100);
            this.Controls.Add(this.btnToggleThrottle);
            this.Name = "ThrottleForm";
            this.Text = "Traffic Throttle";
            this.ResumeLayout(false);
        }
    }
}
