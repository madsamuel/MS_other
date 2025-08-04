# Smart Connect Advisor - Network Performance Monitoring Tools

This repository contains C# console applications that demonstrate Windows toast notification capabilities for network performance monitoring and alerting.

## Project Overview

### SmartConnectAdvisor
A simple console application that demonstrates basic Windows toast notifications for network alerts.

**Features:**
- Displays Windows toast notifications with network degradation alerts
- Interactive toast notifications with action buttons ("Fix Now" and "Send to Admin")
- Uses the CommunityToolkit.WinUI.Notifications library for cross-platform toast support
- Targets .NET 9.0 with Windows 10 compatibility

**Key Components:**
- Static network alert message: "Your connection is degrading, please take action soon."
- Custom application icon integration
- Two-button toast interface for user interaction

### SmartConnectAdvisorAI
An advanced version that integrates with an AI/ML API to predict network performance issues and display contextual alerts.

**Features:**
- **AI-Powered Predictions**: Calls an external machine learning API to predict network degradation probability
- **Dynamic Alert Messages**: Toast messages adapt based on the predicted probability:
  - < 25%: "Connection is stable"
  - 25-50%: "Your connection is degrading, please take action"
  - 50-75%: "Your connection is degrading further, please take action soon"
  - ≥ 75%: "Your connection is degrading beyond usability"
- **Environment Configuration**: Uses .env files for secure API key management
- **HTTP Client Integration**: Makes secure API calls with Bearer token authentication
- **Large Feature Vector Support**: Processes 1000+ dimensional feature vectors for ML prediction
- **Error Handling**: Robust error handling for API calls and JSON parsing
