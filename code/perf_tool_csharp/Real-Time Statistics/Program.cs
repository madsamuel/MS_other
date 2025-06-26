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

    static float latestBandwidthOutputKbps = 0;
    static float latestBandwidthInputKbps = 0;
    static readonly object bandwidthLock = new object();

    [SupportedOSPlatform("windows")]
    static void Main(string[] args)
    {
        Console.Clear();
        Console.WriteLine("RDP Real-Time Statistics Monitor\n");
        StartBandwidthSampler();
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

    static void StartBandwidthSampler()
    {
        new Thread(() =>
        {
            while (true)
            {
                float outKbps, inKbps;
                SampleBandwidthKbps(out outKbps, out inKbps);
                lock (bandwidthLock)
                {
                    latestBandwidthOutputKbps = outKbps;
                    latestBandwidthInputKbps = inKbps;
                }
                Thread.Sleep(200);
            }
        }) { IsBackground = true }.Start();
    }

    static float GetRdpBandwidthOutputKbps()
    {
        lock (bandwidthLock)
        {
            return latestBandwidthOutputKbps;
        }
    }
    static float GetRdpBandwidthInputKbps()
    {
        lock (bandwidthLock)
        {
            return latestBandwidthInputKbps;
        }
    }

    static NetworkInterface? cachedInterface = null;
    static long prevBytesSent = 0;
    static long prevBytesReceived = 0;
    static DateTime prevTime = DateTime.MinValue;

    static void SampleBandwidthKbps(out float outputKbps, out float inputKbps)
    {
        // Prefer interface with most traffic
        var interfaces = NetworkInterface.GetAllNetworkInterfaces()
            .Where(n => n.OperationalStatus == OperationalStatus.Up && n.NetworkInterfaceType != NetworkInterfaceType.Loopback)
            .ToList();
        NetworkInterface? ni = null;
        long maxBytes = 0;
        foreach (var iface in interfaces)
        {
            var stats = iface.GetIPv4Statistics();
            long total = stats.BytesSent + stats.BytesReceived;
            if (total > maxBytes)
            {
                maxBytes = total;
                ni = iface;
            }
        }
        if (ni == null)
        {
            cachedInterface = null;
            prevBytesSent = 0;
            prevBytesReceived = 0;
            prevTime = DateTime.MinValue;
            outputKbps = 0;
            inputKbps = 0;
            return;
        }

        var s = ni.GetIPv4Statistics();
        long bytesSent = s.BytesSent;
        long bytesReceived = s.BytesReceived;
        DateTime now = DateTime.UtcNow;

        outputKbps = 0;
        inputKbps = 0;
        if (cachedInterface?.Id == ni.Id && prevTime != DateTime.MinValue)
        {
            double seconds = (now - prevTime).TotalSeconds;
            if (seconds > 0)
            {
                long deltaSent = bytesSent - prevBytesSent;
                long deltaReceived = bytesReceived - prevBytesReceived;
                outputKbps = (deltaSent * 8f) / 1000f / (float)seconds;
                inputKbps = (deltaReceived * 8f) / 1000f / (float)seconds;
            }
        }
        cachedInterface = ni;
        prevBytesSent = bytesSent;
        prevBytesReceived = bytesReceived;
        prevTime = now;
    }

    [SupportedOSPlatform("windows")]
    static void PrintStats()
    {
        float cpu = GetCpuUsage();
        float mem = GetMemoryUsageMB();
        float bandwidthOut = GetRdpBandwidthOutputKbps();
        float bandwidthIn = GetRdpBandwidthInputKbps();
        int rtt = GetRdpRttMs();
        int latency = GetRdpLatencyMs();
        float gpu = GetGpuUtilization();

        Console.WriteLine($"CPU Usage: {cpu:F1}%");
        Console.WriteLine($"Memory Usage: {mem:F0} MB");
        Console.WriteLine($"RDP Bandwidth Output: {FormatBandwidth(bandwidthOut)}");
        Console.WriteLine($"RDP Bandwidth Input: {FormatBandwidth(bandwidthIn)}");
        Console.WriteLine($"RDP Round Trip Time (RTT): {rtt} ms");
        Console.WriteLine($"RDP Network Latency: {latency} ms");
        Console.WriteLine($"GPU Utilization: {gpu:F1}%");
        DrawBar(gpu);
    }

    static string FormatBandwidth(float kbps)
    {
        if (kbps >= 1000)
            return $"{kbps / 1000:F1} Mbps";
        return $"{kbps:F0} Kbps";
    }

    [SupportedOSPlatform("windows")]
    static float GetCpuUsage()
    {
        using (var cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total"))
        {
            cpuCounter.NextValue();
            Thread.Sleep(200);
            return cpuCounter.NextValue();
        }
    }

    [SupportedOSPlatform("windows")]
    static float GetMemoryUsageMB()
    {
        using (var pc = new PerformanceCounter("Memory", "Committed Bytes"))
        {
            return pc.NextValue() / (1024 * 1024);
        }
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
                string? val = obj["UtilizationPercentage"]?.ToString();
                if (float.TryParse(val, out float parsed))
                    total += parsed;
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
