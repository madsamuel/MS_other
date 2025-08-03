using System.Text.Json;
using Microsoft.Win32;
using Protocol_Analyzer.Services.Interfaces;

namespace Protocol_Analyzer.Services
{
    public class CustomSettingsService : ICustomSettingsService
    {
        public List<CustomRegistrySetting>? LoadCustomSettings(string path)
        {
            try
            {
                if (File.Exists(path))
                {
                    string json = File.ReadAllText(path);
                    return JsonSerializer.Deserialize<List<CustomRegistrySetting>>(json);
                }
            }
            catch (Exception ex)
            {
                // Log error appropriately
                System.Diagnostics.Debug.WriteLine($"Error loading custom settings: {ex.Message}");
            }
            return null;
        }

        public string GetRegistryDisplay(CustomRegistrySetting setting)
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
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading registry: {ex.Message}");
            }
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
