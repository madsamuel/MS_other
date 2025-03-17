; ====================================================
; AutoIt Script to Automate Microsoft Excel via COM
; ====================================================
; Requirements:
;   - Microsoft Excel must be installed.
;   - The file "Big_Excel_File.xlsx" must exist on the desktop.
; ====================================================

; ----- Helper Function to Simulate a Mouse Move and Log the Action -----
Func SimulateMouseMove($x, $y)
    ConsoleWrite("Simulating mouse move to (" & $x & ", " & $y & ")" & @CRLF)
    MouseMove($x, $y, 5)
    Sleep(500)
EndFunc

; ----- Step 1: Open Excel Application -----
ConsoleWrite("Step 1: Opening Excel application." & @CRLF)
SimulateMouseMove(100, 100)
Local $oExcel = ObjCreate("Excel.Application")
If @error Then
    ConsoleWrite("Error: Could not create Excel application object." & @CRLF)
    Exit
EndIf
$oExcel.Visible = True
Sleep(1000)

; ----- Step 2: Open Existing Workbook from Desktop -----
Local $sDesktop = @DesktopDir
Local $sFilePath = $sDesktop & "\Big_Excel.xls"
ConsoleWrite("Step 2: Opening existing workbook: " & $sFilePath & @CRLF)
SimulateMouseMove(150, 150)
Local $oBook = $oExcel.Workbooks.Open($sFilePath)
If Not IsObj($oBook) Then
    ConsoleWrite("Error: Could not open workbook." & @CRLF)
    $oExcel.Quit()
    Exit
EndIf
Sleep(1000)

; ----- Maximizing Excel -----
ConsoleWrite("Maximizing Excel application." & @CRLF)
WinActivate("[CLASS:XLMAIN]")
WinSetState("[CLASS:XLMAIN]", "", @SW_MAXIMIZE)
Sleep(1000)

; ----- Step 3: Type and Format Text in the Active Worksheet -----
ConsoleWrite("Step 3: Typing and formatting text." & @CRLF)
SimulateMouseMove(200, 200)
; Get the first worksheet and activate it
Local $oSheet = $oBook.Worksheets(1)
$oSheet.Activate()

; We'll accumulate text into a variable and then write it into cell A1
Local $sText = "Automated text: This text is bold, italic, and underlined." & @CRLF
Local $iStartTime = TimerInit()
While TimerDiff($iStartTime) < 20000
    $sText &= " More text is being continuously added to the worksheet. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." & @CRLF
    SimulateMouseMove(220, 220)
    Sleep(500)
WEnd
; Write the accumulated text into cell A1
$oSheet.Range("A1").Value = $sText
; Apply formatting to cell A1
$oSheet.Range("A1").Font.Bold = True
$oSheet.Range("A1").Font.Italic = True
$oSheet.Range("A1").Font.Underline = True
Sleep(1000)

; ----- Step 4: Scroll Through the Worksheet -----
ConsoleWrite("Step 4: Scrolling through the worksheet." & @CRLF)
SimulateMouseMove(300, 300)
Local $startTime = TimerInit()
; Loop for 10,000 milliseconds (10 seconds) simulating scroll actions
While TimerDiff($startTime) < 10000
    ConsoleWrite("Scrolling..." & @CRLF)
    SimulateMouseMove(300, 300)
    WinActivate("[CLASS:XLMAIN]")
    Sleep(500)
    Send("{PGDN}")
    Sleep(500)
    Send("{PGUP}")
    Sleep(500)
WEnd

; ----- Step 5: Open and Close the Print Dialog -----
ConsoleWrite("Step 5: Opening print dialog." & @CRLF)
SimulateMouseMove(400, 400)
; Open print dialog using Ctrl+P
Send("^p")
Sleep(2000) ; Wait for the print dialog to open
ConsoleWrite("Step 5: Closing print dialog." & @CRLF)
; Close the print dialog by sending the ESC key
Send("{ESC}")
Sleep(1000)

; ----- Step 6: Close Excel and Discard Any Unsaved Changes -----
ConsoleWrite("Step 6: Closing Excel and discarding any unsaved changes." & @CRLF)
SimulateMouseMove(450, 450)
; Close the workbook without saving further changes
$oBook.Close(False)
$oExcel.Quit()
Sleep(1000)

ConsoleWrite("Script completed successfully." & @CRLF)
Exit

MsgBox(64, "Test completed", "Test completed!")
