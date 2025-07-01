import ctypes
from ctypes import wintypes

# Load wtsapi32.dll
wtsapi32 = ctypes.WinDLL('wtsapi32.dll')

# Constants
WTS_CURRENT_SERVER_HANDLE = ctypes.c_void_p(0)
WTS_CURRENT_SESSION = -1

# WTS_INFO_CLASS enum
class WTS_INFO_CLASS:
    WTSInitialProgram = 0
    WTSApplicationName = 1
    WTSWorkingDirectory = 2
    WTSOEMId = 3
    WTSSessionId = 4
    WTSUserName = 5
    WTSWinStationName = 6
    WTSDomainName = 7
    WTSConnectState = 8
    WTSClientBuildNumber = 9
    WTSClientName = 10
    WTSClientDirectory = 11
    WTSClientProductId = 12
    WTSClientHardwareId = 13
    WTSClientAddress = 14
    WTSClientDisplay = 15
    WTSClientProtocolType = 16
    WTSIdleTime = 17
    WTSLogonTime = 18
    WTSIncomingBytes = 19
    WTSOutgoingBytes = 20
    WTSIncomingFrames = 21
    WTSOutgoingFrames = 22
    WTSClientInfo = 23
    WTSSessionInfo = 24
    WTSSessionInfoEx = 25
    WTSConfigInfo = 26
    WTSValidationInfo = 27
    WTSSessionAddressV4 = 28
    WTSIsRemoteSession = 29

info_class_map = {v: k for k, v in WTS_INFO_CLASS.__dict__.items() if not k.startswith("__")}

# WTSQuerySessionInformationW function
wtsapi32.WTSQuerySessionInformationW.restype = wintypes.BOOL
wtsapi32.WTSQuerySessionInformationW.argtypes = [
    wintypes.HANDLE,   # hServer
    wintypes.DWORD,    # SessionId
    wintypes.DWORD,    # WTSInfoClass
    ctypes.POINTER(ctypes.c_wchar_p),  # ppBuffer
    ctypes.POINTER(wintypes.DWORD)     # pBytesReturned
]

# WTSFreeMemory function
wtsapi32.WTSFreeMemory.restype = None
wtsapi32.WTSFreeMemory.argtypes = [ctypes.c_void_p]

def query_wts_info(session_id=WTS_CURRENT_SESSION):
    for info_class in range(30):
        buffer = ctypes.c_wchar_p()
        bytes_returned = wintypes.DWORD()
        success = wtsapi32.WTSQuerySessionInformationW(
            WTS_CURRENT_SERVER_HANDLE,
            session_id,
            info_class,
            ctypes.byref(buffer),
            ctypes.byref(bytes_returned)
        )
        name = info_class_map.get(info_class, f"WTSInfoClass({info_class})")
        if success:
            try:
                value = buffer.value
                print(f"{name}: {value}")
            except Exception:
                print(f"{name}: <non-string data>")
            finally:
                wtsapi32.WTSFreeMemory(buffer)
        else:
            print(f"{name}: <query failed>")

if __name__ == "__main__":
    query_wts_info()
