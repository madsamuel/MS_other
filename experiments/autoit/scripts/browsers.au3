; Open Edge and navigate to Amazon Movies to Buy
Local $sSearchTerm = "movies to buy"
Local $sURL = "https://www.amazon.com"

; Launch Microsoft Edge using the full path
Run('"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -new-window ' & $sURL)
Sleep(5000)  ; Wait for Edge to load

; Activate Edge window
WinWaitActive("[CLASS:Chrome_WidgetWin_1]", "", 10)
WinSetState("[CLASS:Chrome_WidgetWin_1]", "", @SW_MAXIMIZE)  ; Maximize the window

Sleep(2000)

; Directly click on the Amazon search box
; NOTE: Adjust these coordinates (600, 150) as needed for your screen/resolution.
MouseClick("left", 600, 105, 1, 10)
Sleep(500)

; Type the search term into the search box and press Enter
Send($sSearchTerm)
Sleep(500)
Send("{ENTER}")
Sleep(5000)  ; Wait for results to load

; Scroll down for 5 seconds
Local $iTime = 5000  ; Scroll time in milliseconds
Local $iInterval = 200  ; Time interval for each scroll step
Local $iScrolls = $iTime / $iInterval

For $i = 1 To $iScrolls
    Send("{PGDN}")  ; Scroll down
    Sleep($iInterval)
Next

Sleep(1000)  ; Pause before scrolling back up

; Scroll up for 5 seconds
For $i = 1 To $iScrolls
    Send("{PGUP}")  ; Scroll up
    Sleep($iInterval)
Next

Sleep(2000)  ; Final wait before exiting

; Close Edge window and wait for process to end
WinClose("[CLASS:Chrome_WidgetWin_1]")
ProcessWaitClose("msedge.exe", 10)

Exit
