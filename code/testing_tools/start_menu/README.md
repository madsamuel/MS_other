# Start Menu Automation (Windows)

This small C++ project toggles the Windows Start menu using the left Windows key via SendInput.

Files:
- `automation.h` - UIAutomation class declaration
- `automation.cpp` - implementation that sends the Win key and sleeps
- `main.cpp` - console program, accepts optional args: <initial_ms> <open_ms>
- `test_automation.cpp` - simple unit test that fakes sleeps and key sends

Build (MSVC Developer Command Prompt):

cl /EHsc main.cpp automation.cpp /link user32.lib

Build test:

cl /EHsc test_automation.cpp automation.cpp /link user32.lib

Or with MinGW (g++):

g++ main.cpp automation.cpp -o start_menu.exe -luser32

g++ test_automation.cpp automation.cpp -o test_automation.exe -luser32

Run:

start_menu.exe [initial_ms] [open_ms]

Example:

start_menu.exe 2000 10000

Notes:
- Requires Windows.
- Running as normal user is fine; if UAC or elevated windows appear they may steal focus and break automation.
- Unit test uses a fake subclass and assertions.
