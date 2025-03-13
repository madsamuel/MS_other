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

; Click on the search box and type the search term
Send("^l")  ; Focus address bar
Sleep(500)
Send("{TAB}")  ; Move to search box (may need adjustment)
Sleep(500)
Send($sSearchTerm)
Sleep(500)
Send("{ENTER}")  ; Press Enter to search
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
Exit