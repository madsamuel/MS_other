using Microsoft.Extensions.Logging;
using System;
using System.IO;

namespace PProtocolAnalyzer.Logging
{
    internal class FileLogger : ILogger
    {
        private readonly string _categoryName;
        private readonly Func<string>? _filePathFactory;

        public FileLogger(string categoryName, Func<string>? filePathFactory)
        {
            _categoryName = categoryName;
            _filePathFactory = filePathFactory;
        }

    IDisposable Microsoft.Extensions.Logging.ILogger.BeginScope<TState>(TState state) => NullScope.Instance;

        public bool IsEnabled(LogLevel logLevel) => logLevel != LogLevel.None;

        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
        {
            try
            {
                var message = formatter(state, exception);
                var filePath = _filePathFactory?.Invoke();
                if (string.IsNullOrEmpty(filePath)) return;

                var line = $"[{DateTime.UtcNow:O}] [{logLevel}] {_categoryName}: {message}" + (exception != null ? $" Exception: {exception}" : string.Empty);
                // Ensure directory
                var dir = Path.GetDirectoryName(filePath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                    Directory.CreateDirectory(dir);

                File.AppendAllLines(filePath, new[] { line });
            }
            catch { /* best-effort logging */ }
        }

        private class NullScope : IDisposable
        {
            public static readonly NullScope Instance = new NullScope();
            public void Dispose() { }
        }
    }
}
