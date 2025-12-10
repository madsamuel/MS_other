using System;
using System.Threading.Tasks;

namespace PhoneProximityDetector
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Parse command line arguments
            var config = new AppConfig(args);

            Console.WriteLine("=== Phone Proximity Detector ===");
            Console.WriteLine("This application detects phones with Bluetooth, WiFi, and NRF in proximity.");
            
            if (config.VerboseMode)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("[VERBOSE MODE ENABLED] Detailed device information will be displayed");
                Console.ResetColor();
            }

            if (config.EnableLogging)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine($"[LOGGING ENABLED] Output will be logged to: {config.LogFilePath}");
                Console.ResetColor();
            }

            Console.WriteLine();

            var detector = new ProximityDetector();
            var verboseLogger = new VerboseLogger(config);
            
            // Register event handlers
            detector.OnDeviceDetected += (sender, device) =>
            {
                if (config.VerboseMode)
                {
                    verboseLogger.PrintVerboseOutput(device);
                }
                else
                {
                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine($"[DETECTED] {device}");
                    Console.ResetColor();
                }
                verboseLogger.LogDeviceDetected(device, config.VerboseMode);
            };

            detector.OnDeviceUpdated += (sender, device) =>
            {
                if (config.VerboseMode)
                {
                    verboseLogger.PrintDeviceUpdated(device);
                }
                verboseLogger.LogDeviceUpdate(device);
            };

            detector.OnDeviceLost += (sender, device) =>
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine($"[LOST] {device}");
                Console.ResetColor();
                config.LogMessage($"[LOST] {device}");
            };

            detector.OnError += (sender, error) =>
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[ERROR] {error}");
                Console.ResetColor();
                config.LogMessage($"[ERROR] {error}");
            };

            Console.WriteLine("Starting detection services...");
            Console.WriteLine("Press 'Q' to quit, 'S' to scan now, 'L' to list detected devices, 'H' for help");
            Console.WriteLine();

            config.LogMessage("Application started");
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
                            config.LogMessage("Manual scan triggered by user");
                            await detector.ScanNowAsync();
                            break;
                        case ConsoleKey.L:
                            detector.ListDetectedDevices();
                            break;
                        case ConsoleKey.H:
                            Console.WriteLine();
                            Console.WriteLine("INTERACTIVE COMMANDS:");
                            Console.WriteLine("  Q - Quit the application");
                            Console.WriteLine("  S - Manually trigger a scan");
                            Console.WriteLine("  L - List all detected devices");
                            Console.WriteLine("  H - Show this help message");
                            Console.WriteLine();
                            break;
                    }
                }

                await Task.Delay(100);
            }

            Console.WriteLine("\nStopping detection services...");
            config.LogMessage("Application shutting down");
            await detector.StopAsync();
            Console.WriteLine("Goodbye!");
            
            config.Dispose();
        }
    }
}
