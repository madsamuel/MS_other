; Simulate the key combination Win + R to open the Run dialogue window.
Send("#r")

; Wait 10 seconds for the Run dialogue window to appear.
WinWait("Run", "", 10)

; Simulate entering notepad.exe and pressing the 'ENTER' key.
Send("notepad.exe{Enter}")

; Wait 10 seconds for the Notepad window to appear.
Local $hWnd = WinWait("[CLASS:Notepad]", "", 10)

; Simulate entering the following string and pressing the 'F5' key to input the date and time into edit control of Notepad.
Send("Today's time/date is {F5}")
Send("{LWINDOWN}{UP}")
Send("{LWIN up}")

; Close the Notepad window using the handle returned by WinWait.
; WinClose($hWnd)

