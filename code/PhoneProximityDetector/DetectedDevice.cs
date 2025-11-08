using System;
using System.Collections.Generic;
using System.Linq;

namespace PhoneProximityDetector
{
    public enum DeviceType
    {
        Bluetooth,
        WiFi,
        NRF,
        Unknown
    }

    public class DetectedDevice
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = "Unknown";
        public DeviceType Type { get; set; }
        public int SignalStrength { get; set; } // RSSI or similar
        public string MacAddress { get; set; } = string.Empty;
        public DateTime FirstSeen { get; set; }
        public DateTime LastSeen { get; set; }
        public Dictionary<string, string> AdditionalInfo { get; set; } = new();

        public bool IsPhone()
        {
            // Try to determine if this is a phone based on name or characteristics
            var lowerName = Name.ToLower();
            return lowerName.Contains("phone") ||
                   lowerName.Contains("iphone") ||
                   lowerName.Contains("android") ||
                   lowerName.Contains("samsung") ||
                   lowerName.Contains("pixel") ||
                   lowerName.Contains("oneplus") ||
                   lowerName.Contains("xiaomi") ||
                   lowerName.Contains("huawei") ||
                   lowerName.Contains("oppo") ||
                   lowerName.Contains("vivo") ||
                   lowerName.Contains("motorola") ||
                   lowerName.Contains("lg") ||
                   lowerName.Contains("nokia");
        }

        public string GetProximityLevel()
        {
            // Bluetooth and WiFi RSSI typically range from -100 to 0 dBm
            // Higher (closer to 0) means stronger signal
            if (SignalStrength >= -50)
                return "Very Close";
            else if (SignalStrength >= -70)
                return "Close";
            else if (SignalStrength >= -85)
                return "Medium";
            else
                return "Far";
        }

        private double GetEstimatedDistanceFeet()
        {
            // Estimate distance using log-distance path loss model.
            // Assumptions:
            // - Measured power (RSSI at 1 meter) defaults to -59 dBm if unknown
            // - Path loss exponent n defaults to 2.0 (typical indoor open space)
            // If available, a TxPower value in AdditionalInfo (key: "TxPower") is used as measured power.

            int measuredPower = -59;
            if (AdditionalInfo != null && AdditionalInfo.TryGetValue("TxPower", out var txStr) && int.TryParse(txStr, out var txVal))
            {
                measuredPower = txVal;
            }

            double n = 2.0; // path loss exponent

            // d (meters) = 10 ^ ((measuredPower - RSSI) / (10 * n))
            double meters = Math.Pow(10.0, (measuredPower - SignalStrength) / (10.0 * n));
            double feet = meters * 3.28084;

            // Bound the value to avoid extreme/unhelpful outputs
            if (double.IsNaN(feet) || double.IsInfinity(feet) || feet < 0)
                feet = 0;

            // Cap at a reasonable upper bound for readability
            if (feet > 300)
                feet = 300;

            return feet;
        }

        public override string ToString()
        {
            var phoneIndicator = IsPhone() ? "📱" : "  ";
            var distanceFeet = GetEstimatedDistanceFeet();
            var info = $"{phoneIndicator} [{Type}] {Name} ({MacAddress}) | Signal: {SignalStrength} dBm | Est. Distance: ~{Math.Round(distanceFeet, 1)} ft";
            
            if (AdditionalInfo.Count > 0)
            {
                info += " | " + string.Join(", ", AdditionalInfo.Select(kv => $"{kv.Key}: {kv.Value}"));
            }

            return info;
        }
    }
}
