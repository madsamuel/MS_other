; ====================================================
; AutoIt Script to Automate Microsoft Word via COM
; ====================================================
; Requirements:
;   - Microsoft Word must be installed.
;   - The file "Big_Word_File.dox" must exist on the desktop.
; ====================================================

; ----- Helper Function to Simulate a Mouse Move and Log the Action -----
Func SimulateMouseMove($x, $y)
    ConsoleWrite("Simulating mouse move to (" & $x & ", " & $y & ")" & @CRLF)
    MouseMove($x, $y, 5)
    Sleep(500)
EndFunc

; ----- Step 1: Open Word Application -----
ConsoleWrite("Step 1: Opening Word application." & @CRLF)
SimulateMouseMove(100, 100)
Local $oWord = ObjCreate("Word.Application")
If @error Then
    ConsoleWrite("Error: Could not create Word application object." & @CRLF)
    Exit
EndIf
$oWord.Visible = True
Sleep(1000)

; ----- Step 2: Open Existing Document from Desktop -----
Local $sDesktop = @DesktopDir
Local $sFilePath = $sDesktop & "\Big_Word_File.docx"
ConsoleWrite("Step 2: Opening existing document: " & $sFilePath & @CRLF)
SimulateMouseMove(150, 150)
Local $oDoc = $oWord.Documents.Open($sFilePath)
If Not IsObj($oDoc) Then
    ConsoleWrite("Error: Could not open document." & @CRLF)
    $oWord.Quit()
    Exit
EndIf

; ----- Maximizing Word
WinActivate("[CLASS:OpusApp]")
WinSetState("[CLASS:OpusApp]", "", @SW_MAXIMIZE)

Sleep(1000)

; ----- Step 3: Type and Format Text -----
ConsoleWrite("Step 3: Typing and formatting text." & @CRLF)
SimulateMouseMove(200, 200)
; Move to the end of the document and insert a new paragraph
Local $iStartTime = TimerInit()
While TimerDiff($iStartTime) < 20000
    $oRange = $oDoc.Range($oDoc.Content.End - 1, $oDoc.Content.End - 1) 
    Send("More text is being continuously added to the document. Lorem ipsuNice to meet you, where you been? I could show you incredible things Magic, madness, heaven, sin Saw you there and I thought Oh, my God, look at that face You look like my next mistake Love's a game, wanna play? Ay New money, suit and tie I can read you like a magazineAin't it funny? Rumors fly And I know you heard about me So hey, let's be friendsm dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")    
    Sleep(500)
WEnd
Sleep(1000)

; ----- Step 4: Scroll Through the Document -----
ConsoleWrite("Step 4: Scrolling through the document." & @CRLF)

SimulateMouseMove(300, 300)

Local $startTime = TimerInit()
; Loop for 10,000 milliseconds (10 seconds)
While TimerDiff($startTime) < 10000
    ConsoleWrite("Step 5: Scrolling through the document." & @CRLF)
    SimulateMouseMove(300, 300)
    ; Bring Word to the foreground (Word window class is typically "OpusApp")
    WinActivate("[CLASS:OpusApp]")
    Sleep(500)
    Send("{PGDN}")
    Sleep(500)
    Send("{PGDN}")
    Sleep(500)
    Send("{PGUP}")
    Sleep(500)
WEnd

; ----- Step 7: Open and Close the Print Dialog -----
ConsoleWrite("Step 5: Opening print dialog." & @CRLF)
SimulateMouseMove(400, 400)
; Open print dialog using Ctrl+P
Send("^p")
Sleep(2000) ; Wait for the print dialog to open
ConsoleWrite("Step 6: Closing print dialog." & @CRLF)
; Close print dialog by sending ESC key
Send("{ESC}")
Sleep(1000)

; ----- Step 8: Close Word and Discard Any Unsaved Changes -----
ConsoleWrite("Step 6: Closing Word and discarding any unsaved changes." & @CRLF)
SimulateMouseMove(450, 450)
; Close the document without saving further changes (we already saved)
$oDoc.Close(False)
$oWord.Quit()
Sleep(1000)

ConsoleWrite("Script completed successfully." & @CRLF)

MsgBox(64, "Test completed", "Test completed!")