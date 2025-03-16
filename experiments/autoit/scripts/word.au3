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
Sleep(1000)

; ----- Step 3: Type and Format Text -----
ConsoleWrite("Step 3: Typing and formatting text." & @CRLF)
SimulateMouseMove(200, 200)
; Move to the end of the document and insert a new paragraph
Local $oRange = $oDoc.Range()
$oRange.Collapse(0) ; 0 = wdCollapseEnd
$oRange.InsertParagraphAfter()
$oRange.InsertAfter("Automated text: This text is bold, italic, and underlined." & @CRLF)
; Apply formatting
$oRange.Font.Bold = True
$oRange.Font.Italic = True
$oRange.Font.Underline = True
Sleep(1000)

; ----- Step 4: Insert a 2×2 Table -----
ConsoleWrite("Step 4: Inserting a 2×2 table." & @CRLF)
SimulateMouseMove(250, 250)
$oRange.Collapse(0)
$oRange.InsertParagraphAfter()
Local $oTableRange = $oDoc.Range($oDoc.Content.End - 1, $oDoc.Content.End - 1)
Local $oTable = $oDoc.Tables.Add($oTableRange, 2, 2)
If IsObj($oTable) Then
    $oTable.Cell(1, 1).Range.Text = "Cell 1,1"
    $oTable.Cell(1, 2).Range.Text = "Cell 1,2"
    $oTable.Cell(2, 1).Range.Text = "Cell 2,1"
    $oTable.Cell(2, 2).Range.Text = "Cell 2,2"
Else
    ConsoleWrite("Error: Could not insert table." & @CRLF)
EndIf
Sleep(1000)

; ----- Step 5: Scroll Through the Document -----
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

; ----- Step 6: Save the Document -----
ConsoleWrite("Step 6: Saving the document." & @CRLF)
SimulateMouseMove(350, 350)
$oDoc.Save()
Sleep(1000)

; ----- Step 7: Open and Close the Print Dialog -----
ConsoleWrite("Step 7: Opening print dialog." & @CRLF)
SimulateMouseMove(400, 400)
; Open print dialog using Ctrl+P
Send("^p")
Sleep(2000) ; Wait for the print dialog to open
ConsoleWrite("Step 7: Closing print dialog." & @CRLF)
; Close print dialog by sending ESC key
Send("{ESC}")
Sleep(1000)

; ----- Step 8: Close Word and Discard Any Unsaved Changes -----
ConsoleWrite("Step 8: Closing Word and discarding any unsaved changes." & @CRLF)
SimulateMouseMove(450, 450)
; Close the document without saving further changes (we already saved)
$oDoc.Close(False)
$oWord.Quit()
Sleep(1000)

ConsoleWrite("Script completed successfully." & @CRLF)
Exit

MsgBox(64, "Test completed", "Test completed!")