using System;
using System.IO;

namespace PhoneProximityDetector
{
    public class AppConfig
    {
        public bool VerboseMode { get; set; }
        public string? LogFilePath { get; set; }
        public bool EnableLogging { get; set; }
        private StreamWriter? _logWriter;
        private readonly object _logLock = new object();

        public AppConfig(string[] args)
        {
            VerboseMode = false;
            EnableLogging = false;
            LogFilePath = null;

            ParseCommandLineArgs(args);

            if (EnableLogging && !string.IsNullOrEmpty(LogFilePath))
            {
                InitializeLogging();
            }
        }

        private void ParseCommandLineArgs(string[] args)
        {
            for (int i = 0; i < args.Length; i++)
            {
                switch (args[i].ToLower())
                {
                    case "-verbose":
                    case "--verbose":
                        VerboseMode = true;
                        break;
                    case "-log":
                    case "--log":
                        if (i + 1 < args.Length)
                        {
                            LogFilePath = args[i + 1];
                            EnableLogging = true;
                            i++; // Skip next arg as we've consumed it
                        }
                        break;
                    case "-help":
                    case "--help":
                    case "-?":
                        PrintUsage();
                        Environment.Exit(0);
                        break;
                }
            }
        }

        private void InitializeLogging()
        {
            try
            {
                // Create directory if it doesn't exist
                var directory = Path.GetDirectoryName(LogFilePath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                if (!string.IsNullOrEmpty(LogFilePath))
                {
                    _logWriter = new StreamWriter(LogFilePath, append: true) { AutoFlush = true };
                    LogMessage($"=== Logging Started: {DateTime.Now:yyyy-MM-dd HH:mm:ss} ===");
                    LogMessage($"Verbose Mode: {VerboseMode}");
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[ERROR] Failed to initialize logging: {ex.Message}");
                Console.ResetColor();
                EnableLogging = false;
            }
        }

        public void LogMessage(string message)
        {
            lock (_logLock)
            {
                if (EnableLogging && _logWriter != null)
                {
                    try
                    {
                        _logWriter.WriteLine($"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {message}");
                    }
                    catch
                    {
                        // Silently fail if logging fails
                    }
                }
            }
        }

        public void Dispose()
        {
            lock (_logLock)
            {
                if (_logWriter != null)
                {
                    LogMessage($"=== Logging Ended: {DateTime.Now:yyyy-MM-dd HH:mm:ss} ===");
                    _logWriter?.Flush();
                    _logWriter?.Dispose();
                    _logWriter = null;
                }
            }
        }

        private static void PrintUsage()
        {
            Console.WriteLine(@"
=== Phone Proximity Detector - Usage ===

COMMAND LINE OPTIONS:
  -verbose, --verbose
      Enable verbose output with detailed device information including:
      - Device MAC addresses and manufacturers
      - Bluetooth versions and supported profiles
      - Battery levels (where available)
      - Device types and classes
      - Connection history
      - WiFi encryption types and frequency bands
      - Signal strength patterns
      - Device fingerprinting data
      - Movement patterns and behavioral analysis

  -log <filepath>, --log <filepath>
      Enable logging to the specified file path
      Example: -log C:\logs\proximity_detection.log

  -help, --help, -?
      Display this help message

EXAMPLES:
  PhoneProximityDetector.exe -verbose
  PhoneProximityDetector.exe -log ""C:\logs\detection.log""
  PhoneProximityDetector.exe -verbose -log ""C:\logs\detection.log""

INTERACTIVE COMMANDS (while running):
  Q - Quit the application
  S - Manually trigger a scan
  L - List all detected devices
");
        }
    }
}
