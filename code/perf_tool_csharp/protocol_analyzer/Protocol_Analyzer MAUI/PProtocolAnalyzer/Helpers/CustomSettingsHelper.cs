using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.Maui.Storage;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Win32;
using System.Reflection;
using Microsoft.Extensions.Logging;

namespace PProtocolAnalyzer.Helpers
{
    /// <summary>
    /// Registry setting configuration model (maps JSON snake_case to C# PascalCase)
    /// </summary>
    public class CustomRegistrySetting
    {
        [JsonPropertyName("registry_path")]
        public string RegistryPath { get; set; } = string.Empty;

        [JsonPropertyName("value_name")]
        public string ValueName { get; set; } = string.Empty;

        [JsonPropertyName("value_type")]
        public string ValueType { get; set; } = string.Empty;

        [JsonPropertyName("expected_value")]
        public int ExpectedValue { get; set; }

        [JsonPropertyName("friendly_name")]
        public string FriendlyName { get; set; } = string.Empty;

        [JsonPropertyName("fallback_name")]
        public string FallbackName { get; set; } = string.Empty;
    }

    public static class CustomSettingsHelper
    {
        /// <summary>
        /// Loads custom registry settings from JSON configuration file
        /// File is distributed with the app and user-editable
        /// </summary>
        private static List<CustomRegistrySetting>? _cachedSettings;

        public static IReadOnlyList<CustomRegistrySetting>? LoadCustomSettings()
        {
            if (_cachedSettings != null)
                return _cachedSettings;

            try
            {
                // Only look for the settings file in the process working directory
                string? jsonPath = null;
                string? jsonContent = null;
                try
                {
                    var candidate = Path.Combine(Directory.GetCurrentDirectory(), "custom_registry_settings.json");
                    if (File.Exists(candidate))
                    {
                        jsonPath = candidate;
                        jsonContent = File.ReadAllText(jsonPath);
                        var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                        try { lg?.LogInformation($"Loaded custom_registry_settings.json from working directory: {jsonPath}"); } catch { }
                    }
                    else
                    {
                        var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                        try { lg?.LogInformation("custom_registry_settings.json not found in working directory."); } catch { }
                    }
                }
                catch (Exception ex)
                {
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                    try { lg?.LogWarning(ex, $"Error reading custom settings from working directory: {ex.Message}"); } catch { }
                }

                if (string.IsNullOrWhiteSpace(jsonContent))
                {
                    // No file in working directory — do not fall back to packaged assets per configuration
                    var lg4 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                    try { lg4?.LogInformation("Custom registry settings file not found in working directory."); } catch { }
                    return null;
                }
                var options = new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true,
                    ReadCommentHandling = JsonCommentHandling.Skip
                };

                var settings = JsonSerializer.Deserialize<List<CustomRegistrySetting>>(jsonContent, options);
                if (settings == null)
                {
                    var lg5 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                    try { lg5?.LogWarning($"Custom settings file parsed but returned null: {jsonPath}"); } catch { }
                    return null;
                }

                _cachedSettings = settings;
                return _cachedSettings;
            }
            catch (Exception ex)
            {
                var lg6 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                try { lg6?.LogError(ex, $"Error loading custom settings: {ex.Message}"); } catch { }
                return null;
            }
        }

        /// <summary>
        /// Gets the display status for a specific registry setting
        /// Checks actual registry value against expected value
        /// </summary>
        public static string GetRegistryDisplay(CustomRegistrySetting setting)
        {
            if (setting == null) return string.Empty;

            try
            {
                var (baseKey, subKeyPath) = GetBaseKey(setting.RegistryPath ?? string.Empty);
                if (baseKey == null)
                {
                    return string.IsNullOrEmpty(setting.FallbackName) ? setting.FriendlyName : setting.FallbackName;
                }

                using var regKey = baseKey.OpenSubKey(subKeyPath);
                if (regKey == null)
                    return string.IsNullOrEmpty(setting.FallbackName) ? setting.FriendlyName : setting.FallbackName;

                var rawValue = regKey.GetValue(setting.ValueName);
                if (rawValue == null)
                    return string.IsNullOrEmpty(setting.FallbackName) ? setting.FriendlyName : setting.FallbackName;

                // Normalize value type check
                var type = (setting.ValueType ?? string.Empty).Trim().ToUpperInvariant();
                if (type == "REG_DWORD" || type == "DWORD")
                {
                    try
                    {
                        var intValue = Convert.ToInt32(rawValue);
                        if (intValue == setting.ExpectedValue)
                            return setting.FriendlyName;
                    }
                    catch { /* ignore conversion errors */ }
                }
                else if (type == "REG_SZ" || type == "STRING")
                {
                    var s = rawValue.ToString() ?? string.Empty;
                    if (s.Equals(setting.ExpectedValue.ToString(), StringComparison.OrdinalIgnoreCase))
                        return setting.FriendlyName;
                }
                else
                {
                    // Generic numeric comparison attempt
                    if (int.TryParse(rawValue.ToString(), out var numeric) && numeric == setting.ExpectedValue)
                        return setting.FriendlyName;
                }

                return string.IsNullOrEmpty(setting.FallbackName) ? setting.FriendlyName : setting.FallbackName;
            }
            catch (Exception ex)
            {
                var lg7 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                try { lg7?.LogError(ex, $"Error reading registry setting {setting.ValueName}: {ex.Message}"); } catch { }
                return string.IsNullOrEmpty(setting.FallbackName) ? setting.FriendlyName : setting.FallbackName;
            }
        }

        /// <summary>
        /// Parses registry path to get base key and subkey path
        /// Supports HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER
        /// </summary>
        private static (RegistryKey? baseKey, string subKeyPath) GetBaseKey(string fullPath)
        {
            if (string.IsNullOrWhiteSpace(fullPath)) return (null, string.Empty);

            var path = fullPath.Trim();
            // Support common prefixes and abbreviations
            if (path.StartsWith("HKEY_LOCAL_MACHINE", StringComparison.OrdinalIgnoreCase) || path.StartsWith("HKLM", StringComparison.OrdinalIgnoreCase))
            {
                var prefix = path.IndexOf('\\') >= 0 ? path.Substring(path.IndexOf('\\') + 1) : string.Empty;
                return (Registry.LocalMachine, prefix);
            }

            if (path.StartsWith("HKEY_CURRENT_USER", StringComparison.OrdinalIgnoreCase) || path.StartsWith("HKCU", StringComparison.OrdinalIgnoreCase))
            {
                var prefix = path.IndexOf('\\') >= 0 ? path.Substring(path.IndexOf('\\') + 1) : string.Empty;
                return (Registry.CurrentUser, prefix);
            }

            if (path.StartsWith("HKEY_CLASSES_ROOT", StringComparison.OrdinalIgnoreCase) || path.StartsWith("HKCR", StringComparison.OrdinalIgnoreCase))
            {
                var prefix = path.IndexOf('\\') >= 0 ? path.Substring(path.IndexOf('\\') + 1) : string.Empty;
                return (Registry.ClassesRoot, prefix);
            }

            return (null, string.Empty);
        }

        /// <summary>
        /// Gets all custom settings status messages for display
        /// Returns list of friendly status messages based on actual registry values
        /// </summary>
        public static IReadOnlyList<string> GetAllCustomSettings()
        {
            try
            {
                var customSettings = LoadCustomSettings();
                if (customSettings == null || customSettings.Count == 0)
                    return new[] { "No custom settings configured" };

                var results = new List<string>(customSettings.Count);
                foreach (var setting in customSettings)
                {
                    var status = GetRegistryDisplay(setting);
                    results.Add(status);
                }

                return results;
            }
            catch (Exception ex)
            {
                var lg8 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                try { lg8?.LogError(ex, $"Error getting all custom settings: {ex.Message}"); } catch { }
                return new[] { $"Error loading custom settings: {ex.Message}" };
            }
        }

        /// <summary>
        /// Gets formatted display text for custom settings - Legacy method for compatibility
        /// </summary>
        public static string GetCustomSettingsDisplay()
        {
            var settings = GetAllCustomSettings();
            return string.Join(Environment.NewLine, settings);
        }
    }
}
