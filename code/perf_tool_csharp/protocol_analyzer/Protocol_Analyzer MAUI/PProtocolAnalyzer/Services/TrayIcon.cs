using System.Runtime.InteropServices;

namespace PProtocolAnalyzer.Services;

/// <summary>
/// Elegant system tray icon implementation using Win32 APIs directly.
/// Provides system tray functionality without external dependencies.
/// </summary>
public class TrayIcon : IDisposable
{
    private const int WM_TRAYICON = 0x8000;
    private const int WM_RBUTTONUP = 0x0205;
    private const int NIM_ADD = 0x00000000;
    private const int NIM_MODIFY = 0x00000001;
    private const int NIM_DELETE = 0x00000002;
    private const int NIF_MESSAGE = 0x00000001;
    private const int NIF_ICON = 0x00000002;
    private const int NIF_TIP = 0x00000004;

    private readonly IntPtr _windowHandle;
    private readonly uint _iconId;
    private bool _disposed = false;

    public event Action? ExitRequested;

    public TrayIcon(IntPtr windowHandle, uint iconId = 1)
    {
        _windowHandle = windowHandle;
        _iconId = iconId;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct NotifyIconData
    {
        public int cbSize;
        public IntPtr hWnd;
        public uint uID;
        public uint uFlags;
        public uint uCallbackMessage;
        public IntPtr hIcon;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string szTip;
    }

    [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
    private static extern bool Shell_NotifyIcon(int dwMessage, ref NotifyIconData lpData);

    [DllImport("user32.dll")]
    private static extern IntPtr LoadIcon(IntPtr hInstance, IntPtr lpIconName);

    [DllImport("kernel32.dll")]
    private static extern IntPtr GetModuleHandle(string lpModuleName);

    [DllImport("user32.dll")]
    private static extern IntPtr CreatePopupMenu();

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern bool AppendMenu(IntPtr hMenu, uint uFlags, uint uIDNewItem, string lpNewItem);

    [DllImport("user32.dll")]
    private static extern uint TrackPopupMenu(IntPtr hMenu, uint uFlags, int x, int y, int nReserved, IntPtr hWnd, IntPtr prcRect);

    [DllImport("user32.dll")]
    private static extern bool DestroyMenu(IntPtr hMenu);

    [DllImport("user32.dll")]
    private static extern bool GetCursorPos(out POINT lpPoint);

    [DllImport("user32.dll")]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int X;
        public int Y;
    }

    private const uint MF_STRING = 0x00000000;
    private const uint TPM_RIGHTBUTTON = 0x0002;
    private const uint TPM_RETURNCMD = 0x0100;
    private const int MENU_EXIT = 1001;

    /// <summary>
    /// Shows the tray icon with the specified tooltip.
    /// </summary>
    /// <param name="tooltip">Tooltip text to display on hover</param>
    /// <returns>True if successful, false otherwise</returns>
    public bool Show(string tooltip = "Protocol Analyzer")
    {
        var iconData = new NotifyIconData
        {
            cbSize = Marshal.SizeOf<NotifyIconData>(),
            hWnd = _windowHandle,
            uID = _iconId,
            uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP,
            uCallbackMessage = WM_TRAYICON,
            hIcon = LoadIcon(GetModuleHandle(null!), new IntPtr(32512)), // Default application icon
            szTip = tooltip
        };

        return Shell_NotifyIcon(NIM_ADD, ref iconData);
    }

    /// <summary>
    /// Updates the tooltip text of the tray icon.
    /// </summary>
    /// <param name="tooltip">New tooltip text</param>
    /// <returns>True if successful, false otherwise</returns>
    public bool UpdateTooltip(string tooltip)
    {
        var iconData = new NotifyIconData
        {
            cbSize = Marshal.SizeOf<NotifyIconData>(),
            hWnd = _windowHandle,
            uID = _iconId,
            uFlags = NIF_TIP,
            szTip = tooltip
        };

        return Shell_NotifyIcon(NIM_MODIFY, ref iconData);
    }

    /// <summary>
    /// Handles messages sent to the tray icon (like right-click events).
    /// Call this from your window's message handler.
    /// </summary>
    /// <param name="message">The message ID</param>
    /// <param name="lParam">Additional message data</param>
    public void HandleMessage(int message, IntPtr lParam)
    {
        if (message == WM_TRAYICON)
        {
            int mouseMessage = (int)(lParam.ToInt64() & 0xFFFF);
            if (mouseMessage == WM_RBUTTONUP)
            {
                ShowContextMenu();
            }
        }
    }

    /// <summary>
    /// Shows the context menu at the cursor position.
    /// </summary>
    private void ShowContextMenu()
    {
        // Create popup menu
        IntPtr menu = CreatePopupMenu();
        if (menu == IntPtr.Zero) return;

        try
        {
            // Add "Exit" menu item
            AppendMenu(menu, MF_STRING, MENU_EXIT, "Exit");

            // Get cursor position
            GetCursorPos(out POINT cursorPos);

            // Set foreground window to ensure menu displays properly
            SetForegroundWindow(_windowHandle);

            // Show menu and get selected item
            uint selectedItem = TrackPopupMenu(menu, TPM_RIGHTBUTTON | TPM_RETURNCMD, 
                cursorPos.X, cursorPos.Y, 0, _windowHandle, IntPtr.Zero);

            // Handle menu selection
            if (selectedItem == MENU_EXIT)
            {
                ExitRequested?.Invoke();
            }
        }
        finally
        {
            DestroyMenu(menu);
        }
    }

    /// <summary>
    /// Removes the tray icon.
    /// </summary>
    /// <returns>True if successful, false otherwise</returns>
    public bool Hide()
    {
        var iconData = new NotifyIconData
        {
            cbSize = Marshal.SizeOf<NotifyIconData>(),
            hWnd = _windowHandle,
            uID = _iconId
        };

        return Shell_NotifyIcon(NIM_DELETE, ref iconData);
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            Hide();
            _disposed = true;
        }
        GC.SuppressFinalize(this);
    }

    ~TrayIcon()
    {
        Dispose();
    }
}
