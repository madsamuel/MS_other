dotnet --version

Start Visual Studio Code.

Go to the Explorer view and select Create .NET Project. Alternatively, you can bring up the Command Palette using Ctrl+Shift+P (Command+Shift+P on MacOS) and then type ".NET" and find and select the .NET: New Project command.

After selecting the command, you need to choose the project template. Choose Console App.

dotnet restore

dotnet run

dotnet add package CommunityToolkit.WinUI.Notifications 
# dotnet add package Microsoft.Windows.SDK.Contracts # error NETSDK1130
dotnet add package Microsoft.Windows.SDK.Contracts