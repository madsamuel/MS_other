using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Microsoft.Win32;

namespace Protocol_Analyzer
{
    public class CustomRegistrySetting
    {
        public string registry_path { get; set; } = string.Empty;
        public string value_name { get; set; } = string.Empty;
        public string value_type { get; set; } = string.Empty;
        public int expected_value { get; set; }
        public string friendly_name { get; set; } = string.Empty;
        public string fallback_name { get; set; } = string.Empty;
    }

    public static class CustomSettingsHelper
    {
        public static List<CustomRegistrySetting>? LoadCustomSettings(string path)
        {
            if (File.Exists(path))
            {
                string json = File.ReadAllText(path);
                return JsonSerializer.Deserialize<List<CustomRegistrySetting>>(json);
            }
            return null;
        }

        public static string GetRegistryDisplay(CustomRegistrySetting setting)
        {
            try
            {
                var baseKey = GetBaseKey(setting.registry_path, out string subKeyPath);
                using (var key = baseKey.OpenSubKey(subKeyPath))
                {
                    if (key != null)
                    {
                        var value = key.GetValue(setting.value_name);
                        if (value != null && value.ToString() == setting.expected_value.ToString())
                        {
                            return setting.friendly_name;
                        }
                    }
                }
            }
            catch { }
            return setting.fallback_name;
        }

        private static RegistryKey GetBaseKey(string fullPath, out string subKeyPath)
        {
            if (fullPath.StartsWith("HKEY_LOCAL_MACHINE"))
            {
                subKeyPath = fullPath.Substring("HKEY_LOCAL_MACHINE".Length + 1);
                return Registry.LocalMachine;
            }
            if (fullPath.StartsWith("HKEY_CURRENT_USER"))
            {
                subKeyPath = fullPath.Substring("HKEY_CURRENT_USER".Length + 1);
                return Registry.CurrentUser;
            }
            // Add more as needed
            subKeyPath = fullPath;
            return Registry.LocalMachine;
        }
    }
}
