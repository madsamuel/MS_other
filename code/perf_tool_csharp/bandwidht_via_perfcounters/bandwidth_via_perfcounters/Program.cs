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
        const string udpCat = "UDPv4";
        const string sentCn = "Datagrams Sent/sec";
        const string recvCn = "Datagrams Received/sec";

        const string rfxCat = "RemoteFX Network";
        const string bwCn   = "Current UDP Bandwidth";
        const string rttCn  = "Current UDP RTT";

        // 1) Verify categories exist
        if (!PerformanceCounterCategory.Exists(udpCat))
        {
            Console.Error.WriteLine($"ERROR: Perf category '{udpCat}' not found.");
            return;
        }
        if (!PerformanceCounterCategory.Exists(rfxCat))
        {
            Console.Error.WriteLine($"ERROR: Perf category '{rfxCat}' not found.");
            return;
        }

        // 2) Verify counters in each category
        var udpCategory = new PerformanceCounterCategory(udpCat);
        var rfxCategory = new PerformanceCounterCategory(rfxCat);

        if (!udpCategory.CounterExists(sentCn) || 
            !udpCategory.CounterExists(recvCn))
        {
            Console.Error.WriteLine($"ERROR: One of '{sentCn}' or '{recvCn}' not in {udpCat}.");
            return;
        }
        if (!rfxCategory.CounterExists(bwCn) ||
            !rfxCategory.CounterExists(rttCn))
        {
            Console.Error.WriteLine($"ERROR: One of '{bwCn}' or '{rttCn}' not in {rfxCat}.");
            return;
        }

        // 3) Instantiate counters

        // UDPv4: aggregate across all interfaces
        var udpInstances     = udpCategory.GetInstanceNames();
        var udpSentCounters  = udpInstances
            .Select(i => new PerformanceCounter(udpCat, sentCn, i, readOnly: true))
            .ToArray();
        var udpRecvCounters  = udpInstances
            .Select(i => new PerformanceCounter(udpCat, recvCn, i, readOnly: true))
            .ToArray();

        // RemoteFX: one per RDP session
        var rfxInstances     = rfxCategory.GetInstanceNames();
        var rfxBwCounters    = rfxInstances
            .Select(i => new PerformanceCounter(rfxCat, bwCn,  i, readOnly: true))
            .ToArray();
        var rfxRttCounters   = rfxInstances
            .Select(i => new PerformanceCounter(rfxCat, rttCn, i, readOnly: true))
            .ToArray();

        Console.WriteLine("Sampling (1s interval). Press Ctrl+C to exit.\n");

        // 4) Sampling loop
        while (true)
        {
            // // UDP rates: sum packets/sec
            // float sent = udpSentCounters.Sum(c => c.NextValue());
            // float recv = udpRecvCounters.Sum(c => c.NextValue());
            // Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] UDP Sent Rate: {sent:F1} pkt/s   UDP Recv Rate: {recv:F1} pkt/s");

            // // RemoteFX UDP BW & RTT per-session
            // for (int idx = 0; idx < rfxInstances.Length; idx++)
            // {
            //     string inst = rfxInstances[idx];
            //     float bw = rfxBwCounters[idx].NextValue();   // bits/sec
            //     float rtt = rfxRttCounters[idx].NextValue();  // ms
            //     Console.WriteLine($"  Session '{inst}': UDP BW = {bw / 1e6:F2} Mbps   RTT = {rtt:F0} ms");
            // }

            // Console.WriteLine();
            // Thread.Sleep(1000);
            
            // --- UDP Bytes/sec → KB/s & MB/s ---
            float totalSentBytes = udpSentCounters.Sum(c => c.NextValue());
            float totalRecvBytes = udpRecvCounters.Sum(c => c.NextValue());

            float sentKB = totalSentBytes / 1024f;
            float sentMB = totalSentBytes / (1024f * 1024f);

            float recvKB = totalRecvBytes / 1024f;
            float recvMB = totalRecvBytes / (1024f * 1024f);

            Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] UDP Sent: {sentKB:F1} KB/s ({sentMB:F2} MB/s)   " +
                              $"UDP Recv: {recvKB:F1} KB/s ({recvMB:F2} MB/s)");

            // --- RemoteFX UDP BW & RTT ---
            for (int i = 0; i < rfxInstances.Length; i++)
            {
                string instName = rfxInstances[i];
                float bwBits    = rfxBwCounters[i].NextValue();   // bits/sec
                float bwBytes   = bwBits / 8f;
                float bwKB      = bwBytes / 1024f;
                float bwMB      = bwBytes / (1024f * 1024f);

                float rttMs     = rfxRttCounters[i].NextValue();  // ms

                Console.WriteLine($"  Session '{instName}': UDP BW = {bwKB:F1} KB/s ({bwMB:F2} MB/s)   RTT = {rttMs:F0} ms");
            }

            Console.WriteLine();
            Thread.Sleep(1000);
        }
    }
}
