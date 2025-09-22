using Microsoft.Extensions.Logging;
using Microsoft.Maui;
using System;

namespace PProtocolAnalyzer.Logging
{
    internal static class LoggerAccessor
    {
        public static ILogger<T>? GetLogger<T>()
        {
            try
            {
                var services = PProtocolAnalyzer.MauiProgram.Services;
                if (services == null) return null;
                return services.GetService(typeof(ILogger<T>)) as ILogger<T>;
            }
            catch
            {
                return null;
            }
        }

        public static ILogger? GetLogger(Type categoryType)
        {
            try
            {
                var services = PProtocolAnalyzer.MauiProgram.Services;
                if (services == null) return null;
                var factory = services.GetService(typeof(Microsoft.Extensions.Logging.ILoggerFactory)) as Microsoft.Extensions.Logging.ILoggerFactory;
                return factory?.CreateLogger(categoryType.FullName ?? categoryType.Name);
            }
            catch
            {
                return null;
            }
        }

        public static ILogger? GetLogger(string categoryName)
        {
            try
            {
                var services = PProtocolAnalyzer.MauiProgram.Services;
                if (services == null) return null;
                var factory = services.GetService(typeof(Microsoft.Extensions.Logging.ILoggerFactory)) as Microsoft.Extensions.Logging.ILoggerFactory;
                return factory?.CreateLogger(categoryName);
            }
            catch
            {
                return null;
            }
        }
    }
}
