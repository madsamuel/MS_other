using System;
using System.Collections.Generic;
using System.Text;

namespace PhoneProximityDetector
{
    public class VerboseLogger
    {
        private readonly AppConfig _config;

        public VerboseLogger(AppConfig config)
        {
            _config = config;
        }

        public string FormatDeviceVerbose(DetectedDevice device)
        {
            var sb = new StringBuilder();

            sb.AppendLine();
            sb.AppendLine("╔════════════════════════════════════════════════════════════════╗");
            sb.AppendLine($"║ DEVICE DETECTION - {device.Type}".PadRight(65) + "║");
            sb.AppendLine("╠════════════════════════════════════════════════════════════════╣");

            // Basic Information
            sb.AppendLine($"║ Name:                    {device.Name}".PadRight(65) + "║");
            sb.AppendLine($"║ MAC Address:             {device.MacAddress}".PadRight(65) + "║");
            sb.AppendLine($"║ Device ID:               {device.Id}".PadRight(65) + "║");
            sb.AppendLine($"║ Likely Phone:            {(device.IsPhone() ? "YES ✓" : "NO")}".PadRight(65) + "║");

            // Signal & Proximity Information
            sb.AppendLine("╠════════════════════════════════════════════════════════════════╣");
            sb.AppendLine($"║ Signal Strength (RSSI):  {device.SignalStrength} dBm".PadRight(65) + "║");
            sb.AppendLine($"║ Proximity Level:         {device.GetProximityLevel()}".PadRight(65) + "║");
            sb.AppendLine($"║ Est. Distance:           ~{GetEstimatedDistance(device)} feet".PadRight(65) + "║");

            // Temporal Information
            sb.AppendLine("╠════════════════════════════════════════════════════════════════╣");
            sb.AppendLine($"║ First Seen:              {device.FirstSeen:yyyy-MM-dd HH:mm:ss}".PadRight(65) + "║");
            sb.AppendLine($"║ Last Seen:               {device.LastSeen:yyyy-MM-dd HH:mm:ss}".PadRight(65) + "║");
            sb.AppendLine($"║ Time Visible:            {(device.LastSeen - device.FirstSeen).ToString(@"hh\:mm\:ss")}".PadRight(65) + "║");

            // Additional Information (Bluetooth/WiFi specific)
            if (device.AdditionalInfo.Count > 0)
            {
                sb.AppendLine("╠════════════════════════════════════════════════════════════════╣");
                sb.AppendLine("║ DETAILED INFORMATION:");

                foreach (var kvp in device.AdditionalInfo)
                {
                    var line = $"║   • {kvp.Key}: {kvp.Value}";
                    sb.AppendLine(line.PadRight(65) + "║");
                }
            }

            // Analysis Information
            sb.AppendLine("╠════════════════════════════════════════════════════════════════╣");
            sb.AppendLine("║ ANALYSIS & PRIVACY RISKS:");
            sb.AppendLine(GetPrivacyAnalysis(device));

            sb.AppendLine("╚════════════════════════════════════════════════════════════════╝");

            var output = sb.ToString();
            _config.LogMessage(output.Replace("║", "|").Replace("╔", "+").Replace("╚", "+").Replace("╠", "+").Replace("═", "="));

            return output;
        }

        private string GetEstimatedDistance(DetectedDevice device)
        {
            int measuredPower = -59;
            if (device.AdditionalInfo.TryGetValue("TxPower", out var txStr) && int.TryParse(txStr, out var txVal))
            {
                measuredPower = txVal;
            }

            double n = 2.0;
            double meters = Math.Pow(10.0, (measuredPower - device.SignalStrength) / (10.0 * n));
            double feet = meters * 3.28084;

            if (double.IsNaN(feet) || double.IsInfinity(feet) || feet < 0)
                feet = 0;
            if (feet > 300)
                feet = 300;

            return Math.Round(feet, 1).ToString();
        }

        private string GetPrivacyAnalysis(DetectedDevice device)
        {
            var sb = new StringBuilder();

            switch (device.Type)
            {
                case DeviceType.Bluetooth:
                    sb.AppendLine("║   BLUETOOTH INFORMATION EXPOSED:".PadRight(65) + "║");
                    sb.AppendLine($"║   ✗ MAC Address: {device.MacAddress}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("Manufacturer"))
                        sb.AppendLine($"║   ✗ Manufacturer: {device.AdditionalInfo["Manufacturer"]}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("BtVersion"))
                        sb.AppendLine($"║   ✗ Bluetooth Version: {device.AdditionalInfo["BtVersion"]}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("DeviceClass"))
                        sb.AppendLine($"║   ✗ Device Class: {device.AdditionalInfo["DeviceClass"]}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("BatteryLevel"))
                        sb.AppendLine($"║   ✗ Battery Level: {device.AdditionalInfo["BatteryLevel"]}".PadRight(65) + "║");
                    
                    sb.AppendLine("║   ⚠ RISK: Device can be uniquely identified and tracked".PadRight(65) + "║");
                    break;

                case DeviceType.WiFi:
                    sb.AppendLine("║   WIFI INFORMATION EXPOSED:".PadRight(65) + "║");
                    sb.AppendLine($"║   ✗ SSID: {device.Name}".PadRight(65) + "║");
                    sb.AppendLine($"║   ✗ MAC Address: {device.MacAddress}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("Encryption"))
                        sb.AppendLine($"║   ✗ Encryption: {device.AdditionalInfo["Encryption"]}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("Frequency"))
                        sb.AppendLine($"║   ✗ Frequency: {device.AdditionalInfo["Frequency"]}".PadRight(65) + "║");
                    
                    if (device.AdditionalInfo.ContainsKey("Channel"))
                        sb.AppendLine($"║   ✗ Channel: {device.AdditionalInfo["Channel"]}".PadRight(65) + "║");
                    
                    sb.AppendLine("║   ⚠ RISK: Location can be inferred from SSID and signal patterns".PadRight(65) + "║");
                    break;
            }

            sb.AppendLine("║".PadRight(65) + "║");
            sb.AppendLine("║   PRIVACY THREATS:".PadRight(65) + "║");
            sb.AppendLine("║   → User Tracking: Device can be followed across locations".PadRight(65) + "║");
            sb.AppendLine("║   → Behavioral Profiling: Patterns reveal daily routines".PadRight(65) + "║");
            sb.AppendLine("║   → De-anonymization: Combined with other data sources".PadRight(65) + "║");
            sb.AppendLine("║   → Fingerprinting: Device model & OS can be inferred".PadRight(65) + "║");

            return sb.ToString();
        }

        public void LogDeviceDetected(DetectedDevice device, bool verbose)
        {
            if (verbose)
            {
                _config.LogMessage(FormatDeviceVerbose(device));
            }
            else
            {
                _config.LogMessage($"[DETECTED] {device}");
            }
        }

        public void LogDeviceUpdate(DetectedDevice device)
        {
            _config.LogMessage($"[UPDATED] {device.Name} ({device.MacAddress}) - Signal: {device.SignalStrength} dBm");
        }

        public void PrintVerboseOutput(DetectedDevice device)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine(FormatDeviceVerbose(device));
            Console.ResetColor();
        }

        public void PrintDeviceUpdated(DetectedDevice device)
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine($"[UPDATED] {device.Name} ({device.MacAddress}) - Signal: {device.SignalStrength} dBm");
            Console.ResetColor();
        }
    }
}
