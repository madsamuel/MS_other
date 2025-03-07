using System;
using CommunityToolkit.WinUI.Notifications; // For toast notifications
using Windows.UI.Notifications;             // For the actual 'ToastNotification' class

// See https://aka.ms/new-console-template for more information
// We'll specify an app ID so Windows knows who is sending the toast.
string appId = "MyCompany.MyToastApp";

// Build the toast content (title, message, two buttons, etc.)
var toastContent = new ToastContentBuilder()
    .AddText("Network Alert")
    .AddText("Your connection is degrading, please take action soon.")
    .AddButton(new ToastButton()
        .SetContent("Fix Now")               // What the button displays
        .AddArgument("action", "fixNow"))    // Argument for activation (if using COM/advanced)
    .AddButton(new ToastButton()
        .SetContent("Ignore")                // Second button
        .AddArgument("action", "ignore"))
    .GetToastContent();

// Create the actual toast notification from the XML content
var toast = new ToastNotification(toastContent.GetXml());

// Use the CommunityToolkit helper to create and show the toast
ToastNotificationManagerCompat.CreateToastNotifier().Show(toast);

// Keep console open so we can observe the result
Console.WriteLine("Toast with two buttons has been sent. Press any key to exit.");
Console.ReadKey();
