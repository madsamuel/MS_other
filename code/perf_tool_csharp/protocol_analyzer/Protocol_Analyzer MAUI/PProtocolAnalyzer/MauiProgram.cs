using Microsoft.Extensions.Logging;
using PProtocolAnalyzer.Logging;
using System;
using System.IO;

namespace PProtocolAnalyzer;

public static class MauiProgram
{
	public static System.IServiceProvider? Services { get; private set; }

	public static MauiApp CreateMauiApp()
	{
		var builder = MauiApp.CreateBuilder();
		builder
			.UseMauiApp<App>()
			.ConfigureFonts(fonts =>
			{
				fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
				fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
			});

#if DEBUG
		builder.Logging.AddDebug();
#endif

			// Add a simple file logger (writes to LocalAppData\PProtocolAnalyzer\logs\app.log)
			var logFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PProtocolAnalyzer", "logs");
			var logFile = Path.Combine(logFolder, "app.log");
			builder.Logging.AddProvider(new FileLoggerProvider(() => logFile));

	var app = builder.Build();
	Services = app.Services;
	return app;
	}
}
