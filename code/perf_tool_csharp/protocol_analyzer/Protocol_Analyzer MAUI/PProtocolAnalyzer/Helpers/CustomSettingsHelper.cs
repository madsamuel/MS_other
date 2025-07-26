using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace PProtocolAnalyzer.Helpers
{
    public static class CustomSettingsHelper
    {
        /// <summary>
        /// Loads custom settings from JSON file - simplified version for MAUI
        /// In the original WinForms version, this loaded from Resources/custom_registry_settings.json
        /// </summary>
        public static List<string> LoadCustomSettings()
        {
            try
            {
                var settings = new List<string>();
                
                // TODO: Could be enhanced to read from actual JSON file or registry
                // For now, provide default settings similar to the WinForms version
                settings.Add("HEVC not enabled");
                settings.Add("Software before hardware");
                
                return settings;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading custom settings: {ex.Message}");
                return new List<string> { "No custom settings found." };
            }
        }

        /// <summary>
        /// Gets formatted display text for custom settings
        /// </summary>
        public static string GetCustomSettingsDisplay()
        {
            try
            {
                var settings = LoadCustomSettings();
                return string.Join("\n", settings);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting custom settings display: {ex.Message}");
                return "No custom settings found.";
            }
        }
    }

    // Placeholder class for custom registry setting structure
    public class CustomRegistrySetting
    {
        public string? Name { get; set; }
        public string? Value { get; set; }
        public string? DisplayText { get; set; }

        public override string ToString()
        {
            return DisplayText ?? $"{Name}: {Value}";
        }
    }
}
