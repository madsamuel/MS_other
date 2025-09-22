using Microsoft.Extensions.Logging;
using System;

namespace PProtocolAnalyzer.Logging
{
    internal class FileLoggerProvider : ILoggerProvider
    {
        private readonly Func<string> _filePathFactory;

        public FileLoggerProvider(Func<string> filePathFactory)
        {
            _filePathFactory = filePathFactory;
        }

        public ILogger CreateLogger(string categoryName)
        {
            return new FileLogger(categoryName, _filePathFactory);
        }

        public void Dispose() { }
    }
}
