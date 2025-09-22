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
                // Candidate locations to probe (no hardcoded dev paths)
                var baseDirsList = new List<string>();

                // Working directory where the process was started (user-run folder)
                try { baseDirsList.Add(Environment.CurrentDirectory); } catch { }

                // AppContext / AppDomain base directories (exe folder)
                try { baseDirsList.Add(AppContext.BaseDirectory ?? string.Empty); } catch { }
                try { baseDirsList.Add(AppDomain.CurrentDomain.BaseDirectory ?? string.Empty); } catch { }

                // Entry assembly location (may differ for single-file or packaged apps)
                try { baseDirsList.Add(Path.GetDirectoryName(Assembly.GetEntryAssembly()?.Location ?? string.Empty) ?? string.Empty); } catch { }
                try { baseDirsList.Add(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location) ?? string.Empty); } catch { }

                // Process main module folder (robust fallback)
                try
                {
                    var mainModule = System.Diagnostics.Process.GetCurrentProcess().MainModule?.FileName;
                    if (!string.IsNullOrEmpty(mainModule))
                        baseDirsList.Add(Path.GetDirectoryName(mainModule) ?? string.Empty);
                }
                catch { }

                var baseDirs = baseDirsList
                    .Where(d => !string.IsNullOrWhiteSpace(d))
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .ToArray();

                var candidates = baseDirs
                    .SelectMany(d => new[] {
                        Path.Combine(d, "custom_registry_settings.json"),
                        Path.Combine(d, "Resources", "Raw", "custom_registry_settings.json")
                    })
                    .Concat(new[] { Path.Combine(Directory.GetCurrentDirectory(), "custom_registry_settings.json") })
                    .Where(p => !string.IsNullOrWhiteSpace(p))
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .ToList();

                string? jsonPath = candidates.FirstOrDefault(File.Exists);
                string? jsonContent = null;

                if (jsonPath != null)
                {
                    jsonContent = File.ReadAllText(jsonPath);
                    var lg = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                    try { lg?.LogInformation($"Loaded custom_registry_settings.json from disk: {jsonPath}"); } catch { }
                }
                else
                {
                    // If the file wasn't found on disk, try reading it from the MAUI app package assets
                    try
                    {
                        using var stream = FileSystem.OpenAppPackageFileAsync("custom_registry_settings.json").GetAwaiter().GetResult();
                        if (stream != null)
                        {
                            using var sr = new StreamReader(stream);
                            jsonContent = sr.ReadToEnd();
                            var lg2 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                            try { lg2?.LogInformation("Loaded custom_registry_settings.json from app package assets."); } catch { }
                        }
                    }
                    catch (Exception ex)
                    {
                        var lg3 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                        try { lg3?.LogWarning(ex, $"App package asset not found or unreadable: {ex.Message}"); } catch { }
                    }
                }

                if (string.IsNullOrWhiteSpace(jsonContent))
                {
                    var lg4 = PProtocolAnalyzer.Logging.LoggerAccessor.GetLogger(typeof(CustomSettingsHelper));
                    try { lg4?.LogInformation("Custom registry settings file not found in any of the expected locations or app package."); } catch { }
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
