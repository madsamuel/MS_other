using System;
using System.Threading.Tasks;

namespace PhoneProximityDetector
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("=== Phone Proximity Detector ===");
            Console.WriteLine("This application detects phones with Bluetooth, WiFi, and NRF in proximity.");
            Console.WriteLine();

            var detector = new ProximityDetector();
            
            // Register event handlers
            detector.OnDeviceDetected += (sender, device) =>
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine($"[DETECTED] {device}");
                Console.ResetColor();
            };

            detector.OnDeviceLost += (sender, device) =>
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine($"[LOST] {device}");
                Console.ResetColor();
            };

            detector.OnError += (sender, error) =>
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[ERROR] {error}");
                Console.ResetColor();
            };

            Console.WriteLine("Starting detection services...");
            Console.WriteLine("Press 'Q' to quit, 'S' to scan now, 'L' to list detected devices");
            Console.WriteLine();

            await detector.StartAsync();

            // Main loop
            bool running = true;
            while (running)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true);
                    switch (key.Key)
                    {
                        case ConsoleKey.Q:
                            running = false;
                            break;
                        case ConsoleKey.S:
                            Console.WriteLine("Manual scan triggered...");
                            await detector.ScanNowAsync();
                            break;
                        case ConsoleKey.L:
                            detector.ListDetectedDevices();
                            break;
                    }
                }

                await Task.Delay(100);
            }

            Console.WriteLine("\nStopping detection services...");
            await detector.StopAsync();
            Console.WriteLine("Goodbye!");
        }
    }
}
