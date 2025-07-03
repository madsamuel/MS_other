import ctypes
from ctypes import wintypes

# Load wtsapi32.dll
wtsapi32 = ctypes.WinDLL('wtsapi32.dll')

# Constants
WTS_CURRENT_SERVER_HANDLE = ctypes.c_void_p(0)
WTS_CURRENT_SESSION = -1


# WTS_INFO_CLASS enum (from wtsapi32.h, up to Windows 11)
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
    WTSApplicationUserModelId = 30
    WTSApplicationType = 31
    WTSSessionInfoEx2 = 32
    WTSSessionInfoEx3 = 33

info_class_map = {v: k for k, v in WTS_INFO_CLASS.__dict__.items() if not k.startswith("__")}

# Structures for complex info classes
class WTS_CLIENT_ADDRESS(ctypes.Structure):
    _fields_ = [
        ("AddressFamily", wintypes.DWORD),
        ("Address", wintypes.BYTE * 20)
    ]

class WTS_CLIENT_DISPLAY(ctypes.Structure):
    _fields_ = [
        ("HorizontalResolution", wintypes.DWORD),
        ("VerticalResolution", wintypes.DWORD),
        ("ColorDepth", wintypes.DWORD)
    ]

# Add more structures as needed for other info classes

# WTSQuerySessionInformationW function
wtsapi32.WTSQuerySessionInformationW.restype = wintypes.BOOL
wtsapi32.WTSQuerySessionInformationW.argtypes = [
    wintypes.HANDLE,   # hServer
    wintypes.DWORD,    # SessionId
    wintypes.DWORD,    # WTSInfoClass
    ctypes.POINTER(ctypes.c_void_p),   # ppBuffer (generic pointer)
    ctypes.POINTER(wintypes.DWORD)     # pBytesReturned
]

# WTSFreeMemory function
wtsapi32.WTSFreeMemory.restype = None
wtsapi32.WTSFreeMemory.argtypes = [ctypes.c_void_p]

def query_wts_info(session_id=WTS_CURRENT_SESSION):
    # Map info class to type: 'str', 'dword', 'struct', etc.
    info_class_types = {
        0: 'str', 1: 'str', 2: 'str', 3: 'str', 4: 'dword', 5: 'str', 6: 'str', 7: 'str',
        8: 'dword', 9: 'dword', 10: 'str', 11: 'str', 12: 'dword', 13: 'dword',
        14: 'struct_addr', 15: 'struct_display', 16: 'dword', 17: 'dword', 18: 'dword',
        19: 'dword', 20: 'dword', 21: 'dword', 22: 'dword',
        23: 'struct', 24: 'struct', 25: 'struct', 26: 'struct', 27: 'struct', 28: 'struct_addr',
        29: 'dword', 30: 'str', 31: 'dword', 32: 'struct', 33: 'struct',
    }
    for info_class in range(0, 34):
        name = info_class_map.get(info_class, f"WTSInfoClass({info_class})")
        bytes_returned = wintypes.DWORD()
        typ = info_class_types.get(info_class, 'str')
        buffer = ctypes.c_void_p()
        success = wtsapi32.WTSQuerySessionInformationW(
            WTS_CURRENT_SERVER_HANDLE,
            session_id,
            info_class,
            ctypes.byref(buffer),
            ctypes.byref(bytes_returned)
        )
        if not success or not buffer.value:
            print(f"{name}: <query failed>")
            continue
        try:
            if typ == 'str':
                value = ctypes.wstring_at(buffer)
                print(f"{name}: {value}")
            elif typ == 'dword':
                dword_ptr = ctypes.cast(buffer, ctypes.POINTER(wintypes.DWORD))
                value = dword_ptr.contents.value
                # Special case for WTSClientProtocolType
                if info_class == WTS_INFO_CLASS.WTSClientProtocolType:
                    proto_map = {0: 'Console', 1: 'ICA', 2: 'RDP'}
                    proto_str = proto_map.get(value, f'Unknown ({value})')
                    print(f"{name}: {proto_str}")
                else:
                    print(f"{name}: {value}")
            elif typ == 'struct_addr':
                addr = ctypes.cast(buffer, ctypes.POINTER(WTS_CLIENT_ADDRESS)).contents
                # Only use the first bytes_returned.value bytes
                addr_bytes = bytearray(addr.Address)[:bytes_returned.value-4]  # 4 bytes for AddressFamily
                if addr.AddressFamily == 2 and len(addr_bytes) >= 4:  # AF_INET
                    ip = '.'.join(str(b) for b in addr_bytes[:4])
                    print(f"{name}: family=AF_INET, address={ip}")
                else:
                    addr_str = ':'.join(f'{b:02x}' for b in addr_bytes)
                    print(f"{name}: family={addr.AddressFamily}, address={addr_str}")
            elif typ == 'struct_display':
                disp = ctypes.cast(buffer, ctypes.POINTER(WTS_CLIENT_DISPLAY)).contents
                print(f"{name}: {disp.HorizontalResolution}x{disp.VerticalResolution}, {disp.ColorDepth}bpp")
            else:
                print(f"{name}: <struct or unsupported type, {bytes_returned.value} bytes>")
        except Exception as e:
            print(f"{name}: <error: {e}>")
        finally:
            wtsapi32.WTSFreeMemory(buffer)

if __name__ == "__main__":
    query_wts_info()
