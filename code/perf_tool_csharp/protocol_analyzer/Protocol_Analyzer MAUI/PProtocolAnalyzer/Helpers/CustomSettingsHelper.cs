using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using Microsoft.Win32;
using System.Reflection;

namespace PProtocolAnalyzer.Helpers
{
    /// <summary>
    /// Registry setting configuration model
    /// </summary>
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
        /// <summary>
        /// Loads custom registry settings from JSON configuration file
        /// File is distributed with the app and user-editable
        /// </summary>
        public static List<CustomRegistrySetting>? LoadCustomSettings()
        {
            try
            {
                // DEBUGGING: Try the exact path we know works
                string hardcodedPath = @"c:\code\MS_other\code\perf_tool_csharp\protocol_analyzer\Protocol_Analyzer MAUI\PProtocolAnalyzer\bin\Debug\net9.0-windows10.0.19041.0\win10-x64\custom_registry_settings.json";
                
                // Try multiple paths to find the JSON file
                string[] possiblePaths = {
                    hardcodedPath, // Debugging path
                    // MAUI app directory (most likely location)
                    Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "custom_registry_settings.json"),
                    // Resources/Raw folder
                    Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Resources", "Raw", "custom_registry_settings.json")
                };

                string jsonPath = "";
                foreach (var path in possiblePaths)
                {
                    System.Diagnostics.Debug.WriteLine($"Checking path: {path}");
                    if (File.Exists(path))
                    {
                        jsonPath = path;
                        System.Diagnostics.Debug.WriteLine($"Found file at: {path}");
                        break;
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"File not found at: {path}");
                    }
                }

                if (string.IsNullOrEmpty(jsonPath))
                {
                    System.Diagnostics.Debug.WriteLine($"Custom registry settings file not found in any of the expected locations:");
                    foreach (var path in possiblePaths)
                    {
                        System.Diagnostics.Debug.WriteLine($"  - {path}");
                    }
                    return null;
                }

                string jsonContent = File.ReadAllText(jsonPath);
                System.Diagnostics.Debug.WriteLine($"JSON content: {jsonContent}");
                
                var settings = JsonSerializer.Deserialize<List<CustomRegistrySetting>>(jsonContent);
                
                System.Diagnostics.Debug.WriteLine($"Successfully loaded {settings?.Count ?? 0} custom registry settings from: {jsonPath}");
                return settings;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading custom settings: {ex.Message}");
                System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
                return null;
            }
        }

        /// <summary>
        /// Gets the display status for a specific registry setting
        /// Checks actual registry value against expected value
        /// </summary>
        public static string GetRegistryDisplay(CustomRegistrySetting setting)
        {
            try
            {
                // Parse the registry path to get base key and subkey
                var (baseKey, subKeyPath) = GetBaseKey(setting.registry_path);
                
                if (baseKey == null)
                {
                    System.Diagnostics.Debug.WriteLine($"Invalid registry path: {setting.registry_path}");
                    return setting.fallback_name;
                }

                // Open the registry subkey
                using (var regKey = baseKey.OpenSubKey(subKeyPath))
                {
                    if (regKey == null)
                    {
                        System.Diagnostics.Debug.WriteLine($"Registry key not found: {setting.registry_path}");
                        return setting.fallback_name;
                    }

                    // Read the registry value
                    var value = regKey.GetValue(setting.value_name);
                    if (value == null)
                    {
                        System.Diagnostics.Debug.WriteLine($"Registry value not found: {setting.value_name}");
                        return setting.fallback_name;
                    }

                    // Compare with expected value
                    if (setting.value_type == "REG_DWORD" && value is int intValue)
                    {
                        if (intValue == setting.expected_value)
                        {
                            return setting.friendly_name;
                        }
                    }
                    
                    System.Diagnostics.Debug.WriteLine($"Registry value mismatch - Expected: {setting.expected_value}, Actual: {value}");
                    return setting.fallback_name;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error reading registry setting {setting.value_name}: {ex.Message}");
                return setting.fallback_name;
            }
        }

        /// <summary>
        /// Parses registry path to get base key and subkey path
        /// Supports HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER
        /// </summary>
        private static (RegistryKey? baseKey, string subKeyPath) GetBaseKey(string fullPath)
        {
            try
            {
                if (fullPath.StartsWith("HKEY_LOCAL_MACHINE\\"))
                {
                    string subKeyPath = fullPath.Substring("HKEY_LOCAL_MACHINE\\".Length);
                    return (Registry.LocalMachine, subKeyPath);
                }
                else if (fullPath.StartsWith("HKEY_CURRENT_USER\\"))
                {
                    string subKeyPath = fullPath.Substring("HKEY_CURRENT_USER\\".Length);
                    return (Registry.CurrentUser, subKeyPath);
                }
                else if (fullPath.StartsWith("HKEY_CLASSES_ROOT\\"))
                {
                    string subKeyPath = fullPath.Substring("HKEY_CLASSES_ROOT\\".Length);
                    return (Registry.ClassesRoot, subKeyPath);
                }
                
                return (null, string.Empty);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error parsing registry path {fullPath}: {ex.Message}");
                return (null, string.Empty);
            }
        }

        /// <summary>
        /// Gets all custom settings status messages for display
        /// Returns list of friendly status messages based on actual registry values
        /// </summary>
        public static List<string> GetAllCustomSettings()
        {
            try
            {
                System.Diagnostics.Debug.WriteLine("GetAllCustomSettings: Starting...");
                
                var customSettings = LoadCustomSettings();
                var results = new List<string>();

                System.Diagnostics.Debug.WriteLine($"GetAllCustomSettings: LoadCustomSettings returned {customSettings?.Count ?? 0} settings");

                if (customSettings == null || customSettings.Count == 0)
                {
                    System.Diagnostics.Debug.WriteLine("GetAllCustomSettings: No settings found, returning default message");
                    results.Add("No custom settings configured");
                    return results;
                }

                foreach (var setting in customSettings)
                {
                    System.Diagnostics.Debug.WriteLine($"GetAllCustomSettings: Processing setting '{setting.value_name}'");
                    string status = GetRegistryDisplay(setting);
                    System.Diagnostics.Debug.WriteLine($"GetAllCustomSettings: Got status '{status}' for setting '{setting.value_name}'");
                    results.Add(status);
                }

                System.Diagnostics.Debug.WriteLine($"GetAllCustomSettings: Returning {results.Count} results");
                return results;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting all custom settings: {ex.Message}");
                System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
                return new List<string> { $"Error loading custom settings: {ex.Message}" };
            }
        }

        /// <summary>
        /// Gets formatted display text for custom settings - Legacy method for compatibility
        /// </summary>
        public static string GetCustomSettingsDisplay()
        {
            try
            {
                var settings = GetAllCustomSettings();
                return string.Join("\n", settings);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting custom settings display: {ex.Message}");
                return "Error loading custom settings";
            }
        }
    }
}
