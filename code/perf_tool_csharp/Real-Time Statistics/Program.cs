using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using System.Runtime.Versioning;

class Program
{
    static int updateIntervalMs = 1000;
    static long prevInBytes = -1, prevOutBytes = -1;
    static DateTime prevTime = DateTime.MinValue;

    [DllImport("wtsapi32.dll", SetLastError = true)]
    static extern bool WTSQuerySessionInformation(
        IntPtr hServer,
        int sessionId,
        WTS_INFO_CLASS wtsInfoClass,
        out IntPtr ppBuffer,
        out int pBytesReturned);

    [DllImport("wtsapi32.dll")]
    static extern void WTSFreeMemory(IntPtr pointer);

    static readonly IntPtr WTS_CURRENT_SERVER_HANDLE = IntPtr.Zero;

    enum WTS_INFO_CLASS
    {
        WTSIncomingBytes = 0x19,
        WTSOutgoingBytes = 0x1A,
        WTSIncomingFrames = 0x1B,
        WTSOutgoingFrames = 0x1C,
    }

    static long QuerySessionLong(WTS_INFO_CLASS infoClass)
    {
        IntPtr buffer;
        int bytesReturned;
        int sessionId = Process.GetCurrentProcess().SessionId;
        if (WTSQuerySessionInformation(WTS_CURRENT_SERVER_HANDLE, sessionId, infoClass, out buffer, out bytesReturned) && bytesReturned == sizeof(long))
        {
            long value = Marshal.ReadInt64(buffer);
            WTSFreeMemory(buffer);
            return value;
        }
        if (buffer != IntPtr.Zero)
            WTSFreeMemory(buffer);
        return -1;
    }

    [SupportedOSPlatform("windows")]
    static void Main(string[] args)
    {
        Console.Clear();
        Console.WriteLine("RDP Real-Time Statistics Monitor\n");
        while (true)
        {
            Console.SetCursorPosition(0, 2);
            PrintStats();
            Thread.Sleep(updateIntervalMs);
        }
    }

    [SupportedOSPlatform("windows")]
    static void PrintStats()
    {
        float cpu = GetCpuUsage();
        float mem = GetMemoryUsageMB();
        double bandwidthOut = 0, bandwidthIn = 0;
        GetRdpBandwidthKbps(out bandwidthOut, out bandwidthIn);
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

    static void GetRdpBandwidthKbps(out double outKbps, out double inKbps)
    {
        long inBytes = QuerySessionLong(WTS_INFO_CLASS.WTSIncomingBytes);
        long outBytes = QuerySessionLong(WTS_INFO_CLASS.WTSOutgoingBytes);
        DateTime now = DateTime.UtcNow;
        outKbps = 0;
        inKbps = 0;
        if (prevInBytes >= 0 && prevOutBytes >= 0 && prevTime != DateTime.MinValue)
        {
            double seconds = (now - prevTime).TotalSeconds;
            if (seconds > 0)
            {
                outKbps = ((outBytes - prevOutBytes) * 8.0) / 1000.0 / seconds;
                inKbps = ((inBytes - prevInBytes) * 8.0) / 1000.0 / seconds;
            }
        }
        prevInBytes = inBytes;
        prevOutBytes = outBytes;
        prevTime = now;
    }

    static string FormatBandwidth(double kbps)
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
        string server = Environment.GetEnvironmentVariable("CLIENTNAME");
        if (string.IsNullOrEmpty(server)) return -1;
        try
        {
            var ping = new System.Net.NetworkInformation.Ping();
            var reply = ping.Send(server, 500);
            return reply.Status == System.Net.NetworkInformation.IPStatus.Success ? (int)reply.RoundtripTime : -1;
        }
        catch { return -1; }
    }

    static int GetRdpLatencyMs()
    {
        return GetRdpRttMs();
    }

    [SupportedOSPlatform("windows")]
    static float GetGpuUtilization()
    {
        try
        {
            var searcher = new System.Management.ManagementObjectSearcher("select * from Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine");
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
        percent = Math.Max(0, Math.Min(100, percent));
        int filled = (int)(percent / 100 * width);
        Console.Write("[");
        Console.Write(new string('|', filled));
        Console.Write(new string(' ', width - filled));
        Console.WriteLine("]");
    }
}
