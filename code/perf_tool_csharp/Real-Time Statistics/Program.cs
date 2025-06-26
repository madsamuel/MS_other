using System;
using System.Diagnostics;
using System.Linq;
using System.Management;
using System.Net.NetworkInformation;
using System.Runtime.InteropServices;
using System.Threading;
using System.Runtime.Versioning;

class Program
{
    // Update interval in milliseconds (change as needed)
    static int updateIntervalMs = 1000;

    static void Main(string[] args)
    {
        Console.Clear();
        Console.WriteLine("RDP Real-Time Statistics Monitor\n");
        // if (!IsRdpSession())
        // {
        //     Console.WriteLine("Not running in an RDP session. Exiting.");
        //     return;
        // }
        while (true)
        {
            Console.SetCursorPosition(0, 2);
            PrintStats();
            Thread.Sleep(updateIntervalMs);
        }
    }

    static bool IsRdpSession()
    {
        return Environment.GetEnvironmentVariable("SESSIONNAME")?.StartsWith("RDP-") == true;
    }

    static void PrintStats()
    {
        float cpu = GetCpuUsage();
        float mem = GetMemoryUsageMB();
        float bandwidth = GetRdpBandwidthKbps();
        int rtt = GetRdpRttMs();
        int latency = GetRdpLatencyMs();
        float gpu = GetGpuUtilization();

        Console.WriteLine($"CPU Usage: {cpu:F1}%");
        Console.WriteLine($"Memory Usage: {mem:F0} MB");
        Console.WriteLine($"RDP Bandwidth Output: {bandwidth:F0} Kbps");
        Console.WriteLine($"RDP Round Trip Time (RTT): {rtt} ms");
        Console.WriteLine($"RDP Network Latency: {latency} ms");
        Console.WriteLine($"GPU Utilization: {gpu:F1}%");
        DrawBar(gpu);
    }

    static float GetCpuUsage()
    {
        using (var cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total"))
        {
            cpuCounter.NextValue();
            Thread.Sleep(200);
            return cpuCounter.NextValue();
        }
    }



    static float GetMemoryUsageMB()
    {
        using (var pc = new PerformanceCounter("Memory", "Committed Bytes"))
        {
            return pc.NextValue() / (1024 * 1024);
        }
    }

    static float GetRdpBandwidthKbps()
    {
        // Approximate: use network interface bytes/sec for active interface
        var ni = NetworkInterface.GetAllNetworkInterfaces()
            .FirstOrDefault(n => n.OperationalStatus == OperationalStatus.Up && n.NetworkInterfaceType != NetworkInterfaceType.Loopback);
        if (ni == null) return 0;
        var stats1 = ni.GetIPv4Statistics();
        long bytesSent1 = stats1.BytesSent;
        Thread.Sleep(200);
        var stats2 = ni.GetIPv4Statistics();
        long bytesSent2 = stats2.BytesSent;
        return ((bytesSent2 - bytesSent1) * 8) / 200f; // Kbps
    }

    static int GetRdpRttMs()
    {
        // Approximate RTT to RDP server (gateway)
        string server = Environment.GetEnvironmentVariable("CLIENTNAME");
        if (string.IsNullOrEmpty(server)) return -1;
        try
        {
            var ping = new Ping();
            var reply = ping.Send(server, 500);
            return reply.Status == IPStatus.Success ? (int)reply.RoundtripTime : -1;
        }
        catch { return -1; }
    }

    static int GetRdpLatencyMs()
    {
        // Use RTT as a proxy for latency
        return GetRdpRttMs();
    }

    [SupportedOSPlatform("windows")]
    static float GetGpuUtilization()
    {
        try
        {
            var searcher = new ManagementObjectSearcher("select * from Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine");
            float total = 0;
            foreach (var obj in searcher.Get())
            {
                total += float.Parse(obj["UtilizationPercentage"].ToString());
            }
            return total;
        }
        catch { return 0; }
    }

    static void DrawBar(float percent)
    {
        int width = 30;
        // Clamp percent between 0 and 100
        percent = Math.Max(0, Math.Min(100, percent));
        int filled = (int)(percent / 100 * width);
        Console.Write("[");
        Console.Write(new string('|', filled));
        Console.Write(new string(' ', width - filled));
        Console.WriteLine("]");
    }
}
