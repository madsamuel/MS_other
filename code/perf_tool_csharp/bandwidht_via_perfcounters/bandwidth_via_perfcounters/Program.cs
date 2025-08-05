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

        // 1) Perf counter definitions
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
            // These counters are already in bits per second (bps)
            float sentBps = udpSentCounters.Sum(c => c.NextValue());
            float recvBps = udpRecvCounters.Sum(c => c.NextValue());

            string sentRateStr = sentBps >= 1_000_000 ? $"{sentBps / 1_000_000:F2} Mbps" : $"{sentBps / 1000:F1} kbps";
            string recvRateStr = recvBps >= 1_000_000 ? $"{recvBps / 1_000_000:F2} Mbps" : $"{recvBps / 1000:F1} kbps";

            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] UDP Sent Rate / Bandwidth Output: {sentRateStr}   UDP Recv Rate / Bandwidth Input: {recvRateStr}");

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
