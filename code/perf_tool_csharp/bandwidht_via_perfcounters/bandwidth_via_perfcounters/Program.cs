using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.Versioning;
using System.Threading;

[SupportedOSPlatform("windows")]
class Program
{
    static void Main()
    {
        // Guard: Windows only
        if (!OperatingSystem.IsWindows())
        {
            Console.Error.WriteLine("ERROR: This tool only runs on Windows.");
            return;
        }

        // Perf counter definitions
        const string cat = "RemoteFX Network";
        const string sentCn = "UDP Sent Rate";
        const string recvCn = "UDP Received Rate";
        const string bwCn   = "Current UDP Bandwidth";
        const string rttCn  = "Current UDP RTT";

        var category = new PerformanceCounterCategory(cat);
        var missingCounters = new System.Collections.Generic.List<string>();
        if (!category.CounterExists(sentCn)) missingCounters.Add($"'{sentCn}' in {cat}");
        if (!category.CounterExists(recvCn)) missingCounters.Add($"'{recvCn}' in {cat}");
        if (!category.CounterExists(bwCn))  missingCounters.Add($"'{bwCn}' in {cat}");
        if (!category.CounterExists(rttCn)) missingCounters.Add($"'{rttCn}' in {cat}");
        if (missingCounters.Count > 0)
        {
            Console.Error.WriteLine($"ERROR: Missing counter(s): {string.Join(", ", missingCounters)}");
            return;
        }

        // 2) Instantiate counters
        var instances = category.GetInstanceNames();
        var udpSentCounters = instances.Select(i => new PerformanceCounter(cat, sentCn, i, true)).ToArray();
        var udpRecvCounters = instances.Select(i => new PerformanceCounter(cat, recvCn, i, true)).ToArray();
        var rfxBwCounters   = instances.Select(i => new PerformanceCounter(cat, bwCn, i, true)).ToArray();
        var rfxRttCounters  = instances.Select(i => new PerformanceCounter(cat, rttCn, i, true)).ToArray();

        Console.WriteLine("Sampling (1s interval). Press Ctrl+C to exit.\n");

        // Warm up counters for accurate readings
        foreach (var c in udpSentCounters) c.NextValue();
        foreach (var c in udpRecvCounters) c.NextValue();
        foreach (var c in rfxBwCounters) c.NextValue();
        foreach (var c in rfxRttCounters) c.NextValue();
        Thread.Sleep(1000);

        // 3) Sampling loop
        while (true)
        {
            float sentPackets = udpSentCounters.Sum(c => c.NextValue());
            float recvPackets = udpRecvCounters.Sum(c => c.NextValue());
            // Assume 1472 bytes per UDP packet (typical for Ethernet, adjust as needed)
            const float bytesPerPacket = 1472f;
            float sentKbps = (sentPackets * bytesPerPacket * 8) / 1024f;
            float recvKbps = (recvPackets * bytesPerPacket * 8) / 1024f;

            string sentRateStr = sentKbps >= 1024f ? $"{sentKbps / 1024f:F2} Mbps" : $"{sentKbps:F1} kbps";
            string recvRateStr = recvKbps >= 1024f ? $"{recvKbps / 1024f:F2} Mbps" : $"{recvKbps:F1} kbps";

            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] UDP Sent Rate: {sentRateStr}   UDP Recv Rate: {recvRateStr}");

            for (int i = 0; i < instances.Length; i++)
            {
                string inst = instances[i];
                float bwBits = rfxBwCounters[i].NextValue();
                float bwMB = (bwBits / 8f) / (1024f * 1024f);
                float rtt = rfxRttCounters[i].NextValue();
                Console.WriteLine($"  Session '{inst}': UDP BW = {bwMB:F2} MB/s   RTT = {rtt:F0} ms");
            }

            Console.WriteLine();
            Thread.Sleep(1000);
        }
    }
}
