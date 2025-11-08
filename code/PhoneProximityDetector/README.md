# Phone Proximity Detector

A C# application that detects phones with Bluetooth, WiFi, and NRF capabilities in proximity of your Windows laptop/desktop.

## Features

- **Bluetooth Detection**: Scans for nearby Bluetooth devices and identifies phones based on device names
- **WiFi Detection**: Monitors WiFi networks and identifies phone hotspots
- **NRF Detection**: Framework for Nordic RF detection (requires additional hardware)
- **Signal Strength Monitoring**: Displays RSSI values to estimate proximity
- **Real-time Updates**: Continuous scanning with configurable intervals
- **Phone Identification**: Smart detection of phone devices vs other devices

## Requirements

- Windows 10/11 (x64)
- .NET 8.0 SDK or Runtime
- Bluetooth adapter (for Bluetooth detection)
- WiFi adapter (for WiFi detection)
- **Optional**: Nordic nRF52840/nRF51 USB dongle (for NRF detection)

## Installation

1. Ensure you have .NET 8.0 SDK installed
2. Navigate to the project directory
3. Restore dependencies and build:
   ```powershell
   dotnet restore
   dotnet build
   ```

## Usage

Run the application:
```powershell
dotnet run
```

### Controls

- **Q**: Quit the application
- **S**: Trigger a manual scan
- **L**: List all currently detected devices

### Output Format

The application displays detected devices in the following format:
```
📱 [Bluetooth] Samsung Galaxy S21 (AA:BB:CC:DD:EE:FF) | Signal: -65 dBm | Proximity: Close
```

- 📱 indicates the device is identified as a phone
- Signal strength ranges from -100 dBm (far) to -30 dBm (very close)
- Proximity levels: Very Close, Close, Medium, Far

## Technology Stack

- **InTheHand.BluetoothLE**: Cross-platform Bluetooth Low Energy library
- **ManagedNativeWifi**: Native WiFi management for Windows
- **System.Management**: Windows system management

## NRF Detection

NRF detection requires specialized hardware that is NOT included in standard laptops:

### Required Hardware
- Nordic nRF52840 USB Dongle or similar
- nRF51 Dongle
- Any Nordic development kit with USB connectivity

### Setup for NRF
1. Connect the Nordic USB dongle to your PC
2. Flash appropriate firmware that:
   - Scans for NRF devices
   - Reports findings via serial communication
   - Outputs format: `NRF,MAC_ADDRESS,RSSI,DEVICE_NAME`
3. Update `NRFDetector.cs` with your COM port settings

Without NRF hardware, the application will function normally but only detect Bluetooth and WiFi devices.

## How It Works

### Bluetooth Detection
- Uses BLE (Bluetooth Low Energy) scanning
- Continuously scans for advertising devices
- Identifies phones by device name patterns
- Reports signal strength (RSSI) for proximity estimation

### WiFi Detection
- Scans available WiFi networks
- Identifies phone hotspots by SSID patterns
- Common patterns: "iPhone", "Android", device names with "phone"
- Uses BSSID (MAC address) for unique identification

### Phone Identification
Devices are identified as phones if their name contains:
- iPhone, Android, Samsung, Pixel, OnePlus, Xiaomi
- Huawei, Oppo, Vivo, Motorola, LG, Nokia
- Generic terms like "phone" or "mobile"

## Permissions

On Windows, the application may require:
- Administrator privileges for WiFi scanning
- Bluetooth permissions (typically granted by default)
- Access to network interfaces

## Troubleshooting

**No devices detected:**
- Ensure Bluetooth is enabled on your PC
- Check that WiFi adapter is active
- Make sure target phone has Bluetooth enabled
- For phone hotspots, the phone must have WiFi hotspot active

**Bluetooth errors:**
- Update Bluetooth drivers
- Restart Bluetooth service: `Restart-Service -Name bthserv`
- Check Windows Privacy settings for Bluetooth access

**WiFi errors:**
- Run as Administrator
- Ensure WiFi is not in Airplane mode
- Check that WiFi adapter supports monitoring mode

## Privacy & Security

This application:
- Only scans for devices broadcasting their presence
- Does not connect to or interact with detected devices
- Does not store or transmit device information
- Operates entirely locally on your machine

## Future Enhancements

- [ ] GUI interface with live device map
- [ ] Device history and analytics
- [ ] Configurable scan intervals
- [ ] Export detected devices to CSV/JSON
- [ ] Custom phone identification patterns
- [ ] Distance estimation improvements
- [ ] Support for additional wireless protocols

## License

This is a demonstration/educational project. Modify and use as needed.

## Contributing

Feel free to enhance the NRF detection implementation or add support for additional wireless protocols!
