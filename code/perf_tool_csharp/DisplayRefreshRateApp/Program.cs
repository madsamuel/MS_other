using System;
using System.Management;

class DisplayRefreshRateUtility
{
    static void Main()
    {
        try
        {
            using (var searcher = new ManagementObjectSearcher("SELECT * FROM Win32_VideoController"))
            {
                foreach (ManagementObject obj in searcher.Get())
                {
                    var name = obj["Name"];
                    var refreshRate = obj["CurrentRefreshRate"];

                    Console.WriteLine($"Display: {name}");
                    Console.WriteLine($"Refresh Rate: {refreshRate} Hz");
                    return; // Show only the first (primary) display
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error retrieving refresh rate: {ex.Message}");
        }
    }
}
