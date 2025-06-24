# RdpStatsMonitor

A .NET 9 C# console utility that displays real-time RDP session statistics, updating at a configurable interval.

## Features
- Detects if running in an RDP session
- Displays:
  - CPU usage
  - Memory usage
  - RDP Bandwidth Output
  - RDP RTT and Network Latency
  - GPU Utilization
- Continuously updates stats at a user-configurable interval

## Usage
1. Build the project:
   ```powershell
   dotnet build
   ```
2. Run the utility:
   ```powershell
   dotnet run
   ```
3. Adjust the update interval by changing the `updateIntervalMs` variable in `Program.cs`.

## Notes
- Some statistics are approximated due to Windows API limitations for RDP.
- Requires .NET 9 SDK.
