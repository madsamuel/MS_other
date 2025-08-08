# Protocol Analyzer Distribution Package

## Files Included:
- `PProtocolAnalyzer.exe` - Main application executable
- `custom_registry_settings.json` - Configuration file for registry settings
- `Start_Protocol_Analyzer.bat` - Batch file to launch the application
- Various Microsoft runtime DLLs and dependencies

## System Requirements:
- Windows 10 version 19041 or later
- .NET 9.0 Runtime (Windows Desktop Apps)
- Windows App SDK Runtime

## Installation Instructions:
1. Extract all files to a folder on your system
2. Ensure all files remain in the same directory
3. Double-click `Start_Protocol_Analyzer.bat` to run the application
   OR
   Double-click `PProtocolAnalyzer.exe` directly

## Features:
- Real-Time RemoteFX Network Statistics monitoring
- System Information display
- Custom Registry Settings detection
- Detected Settings validation
- System tray integration with right-click exit menu

## Configuration:
The `custom_registry_settings.json` file contains the registry settings that the application will monitor. You can modify this file to add or remove registry keys as needed.

## Troubleshooting:
- If the application doesn't start, ensure you have the latest Windows App SDK runtime installed
- For performance counter access, the application may need to be run as Administrator
- If RemoteFX counters are not available, the Real-Time Statistics section will show "N/A"

## Support:
This application monitors RemoteFX network performance counters and system information for protocol analysis purposes.
