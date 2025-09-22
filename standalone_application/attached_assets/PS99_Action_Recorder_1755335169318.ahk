#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SendMode Input
SetBatchLines -1
CoordMode, Mouse, Screen
CoordMode, Pixel, Screen

;PS99 Action Recorder
;
;This script records mouse movements, clicks, and keyboard actions
;and formats them in AutoHotkey syntax for easy use in other scripts.
;
;Controls:
;F1 - Start/Stop Recording
;F2 - Save Recording to File
;F3 - Clear Recording
;F4 - Capture Current Window Info
;Esc - Exit

;Configuration
global Recording := false         ; Whether currently recording
global RecordingStartTime := 0    ; When recording started
global LastActionTime := 0        ; Time of last recorded action
global RecordedActions := []      ; Array of recorded actions
global CaptureInterval := 100     ; How often to check for new actions (ms)
global MinMouseMove := 5          ; Minimum pixels moved to record movement
global SavedWindow := ""          ; Information about captured window
global LastMouseX := 0            ; Last recorded mouse X
global LastMouseY := 0            ; Last recorded mouse Y
global KeysToWatch := "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  ; Keys to monitor
                     . "Space,Tab,Enter,Escape,Up,Down,Left,Right"
                     . "LButton,RButton,MButton"

;Create GUI
Gui, +AlwaysOnTop
Gui, Color, 0x2D2D2D
Gui, Font, s12 cWhite, Segoe UI
Gui, Add, Text, w500 Center, PS99 Action Recorder

Gui, Font, s10 cLime
Gui, Add, Text, w500 vStatusText, Status: Ready

Gui, Font, s10 cWhite
Gui, Add, Text, w100, Recording:
Gui, Add, Text, x+10 w390 vRecordingStatus cRed, Not Recording

Gui, Add, Text, xm w100, Duration:
Gui, Add, Text, x+10 w390 vDurationText, 00:00:00

Gui, Add, Text, xm w100, Actions:
Gui, Add, Text, x+10 w390 vActionsCount, 0 actions recorded

Gui, Font, s10 cWhite
Gui, Add, GroupBox, xm w500 h30, Window Information
Gui, Font, s9 cYellow
Gui, Add, Text, xm+10 yp+15 w480 vWindowText, No window captured yet. Press F4 to capture.

Gui, Font, s10 cWhite
Gui, Add, GroupBox, xm w500 h280, Recorded Actions
Gui, Font, s9 cLime
Gui, Add, Edit, xm+10 yp+20 w480 h250 vRecordingText ReadOnly, Press F1 to start recording...

Gui, Font, s9 c7CFC00
Gui, Add, Text, xm w500 Center, F1: Start/Stop | F2: Save | F3: Clear | F4: Capture Window | Esc: Exit

Gui, Show, w520 h480, PS99 Action Recorder

;Set up hotkeys
F1::ToggleRecording()
F2::SaveRecording()
F3::ClearRecording()
F4::CaptureWindow()
Esc::ExitApp

;Start the record loop timer (disabled until recording starts)
SetTimer, RecordLoop, %CaptureInterval%, Off

;Toggle recording
ToggleRecording() {
    global Recording, RecordingStartTime, LastMouseX, LastMouseY
    
    Recording := !Recording
    
    if (Recording) {
        ; Start recording
        GuiControl,, StatusText, Status: RECORDING
        GuiControl,, RecordingStatus, % "RECORDING"
        GuiControl, +cGreen, RecordingStatus
        RecordingStartTime := A_TickCount
        
        ; Initialize last position
        MouseGetPos, LastMouseX, LastMouseY
        
        ; Start the recording loop
        SetTimer, RecordLoop, %CaptureInterval%, On
        
        ; Record initial window position for reference
        CaptureWindow()
        
        ; Add recording header
        AddToRecording("; Recording started on " . A_YYYY . "-" . A_MM . "-" . A_DD . " at " . A_Hour . ":" . A_Min . ":" . A_Sec)
        AddToRecording("; Window: " . SavedWindow)
        AddToRecording("")
    } else {
        ; Stop recording
        GuiControl,, StatusText, Status: Recording Stopped
        GuiControl,, RecordingStatus, % "Not Recording"
        GuiControl, +cRed, RecordingStatus
        
        ; Stop the recording loop
        SetTimer, RecordLoop, Off
        
        ; Add recording end marker
        AddToRecording("")
        AddToRecording("; Recording ended - " . RecordedActions.Length() . " actions recorded")
        AddToRecording("; Total duration: " . FormatTime((A_TickCount - RecordingStartTime) / 1000))
    }
}

;Save recording to a file
SaveRecording() {
    global RecordedActions
    
    if (RecordedActions.Length() = 0) {
        GuiControl,, StatusText, Status: Nothing to save
        return
    }
    
    ; Generate filename with timestamp
    FormatTime, timestamp,, yyyy-MM-dd_HHmmss
    filename := "PS99_Recording_" . timestamp . ".ahk"
    
    ; Create file content
    fileContent := "#SingleInstance Force`n"
    fileContent .= "#NoEnv`n"
    fileContent .= "SetWorkingDir %A_ScriptDir%`n"
    fileContent .= "SendMode Input`n"
    fileContent .= "SetBatchLines -1`n"
    fileContent .= "CoordMode, Mouse, Screen`n"
    fileContent .= "CoordMode, Pixel, Screen`n`n"
    
    fileContent .= "; PS99 Recorded Actions`n"
    fileContent .= "; Created: " . A_YYYY . "-" . A_MM . "-" . A_DD . " " . A_Hour . ":" . A_Min . ":" . A_Sec . "`n"
    fileContent .= "; Window: " . SavedWindow . "`n`n"
    
    fileContent .= "; Start the script with F1, stop with Esc`n"
    fileContent .= "F1::StartScript()`n"
    fileContent .= "Esc::ExitApp`n`n"
    
    fileContent .= "StartScript() {`n"
    fileContent .= "    ; Activate game window first`n"
    fileContent .= "    WinActivate, " . SavedWindow . "`n"
    fileContent .= "    Sleep, 500`n`n"
    
    fileContent .= "    ; Begin recorded actions`n"
    
    ; Add all recorded actions
    for i, action in RecordedActions {
        fileContent .= "    " . action . "`n"
    }
    
    fileContent .= "`n    MsgBox, Script execution completed!`n"
    fileContent .= "}`n"
    
    ; Write to file
    FileDelete, %filename%
    FileAppend, %fileContent%, %filename%
    
    if (ErrorLevel) {
        GuiControl,, StatusText, Status: Error saving file
    } else {
        GuiControl,, StatusText, % "Status: Saved to " . filename
    }
}

;Clear the current recording
ClearRecording() {
    global RecordedActions
    
    RecordedActions := []
    GuiControl,, RecordingText, Press F1 to start recording...
    GuiControl,, ActionsCount, 0 actions recorded
    GuiControl,, StatusText, Status: Recording cleared
}

;Capture current window info
CaptureWindow() {
    global SavedWindow
    
    ; Get active window
    WinGetTitle, windowTitle, A
    WinGetPos, winX, winY, winWidth, winHeight, A
    WinGet, winID, ID, A
    WinGet, winPID, PID, A
    WinGet, winProcess, ProcessName, A
    
    ; Save window info
    SavedWindow := windowTitle
    
    ; Update UI
    windowInfo := windowTitle . " (" . winProcess . ") - Position: " . winX . "," . winY 
                . " Size: " . winWidth . "x" . winHeight
    
    GuiControl,, WindowText, %windowInfo%
    GuiControl,, StatusText, Status: Captured window information
}

;Record current mouse and keyboard state
RecordLoop:
    if (!Recording)
        return
    
    ; Record duration
    currentTime := A_TickCount
    recordDuration := (currentTime - RecordingStartTime) / 1000
    GuiControl,, DurationText, % FormatTime(recordDuration)
    
    ; Check mouse position
    MouseGetPos, mouseX, mouseY
    
    ; Record significant mouse movements
    if (Abs(mouseX - LastMouseX) > MinMouseMove || Abs(mouseY - LastMouseY) > MinMouseMove) {
        timeFromLast := currentTime - LastActionTime
        
        ; Add sleep if needed
        if (timeFromLast > 100) {
            RecordSleep(timeFromLast)
        }
        
        ; Record movement
        RecordMouseMove(mouseX, mouseY)
        
        ; Update last position
        LastMouseX := mouseX
        LastMouseY := mouseY
        LastActionTime := currentTime
    }
    
    ; Check mouse buttons
    if (GetKeyState("LButton", "P")) {
        timeFromLast := currentTime - LastActionTime
        if (timeFromLast > 100) {
            RecordSleep(timeFromLast)
        }
        
        RecordMouseClick("left", mouseX, mouseY)
        LastActionTime := currentTime
        
        ; Wait for button release
        KeyWait, LButton
    }
    
    if (GetKeyState("RButton", "P")) {
        timeFromLast := currentTime - LastActionTime
        if (timeFromLast > 100) {
            RecordSleep(timeFromLast)
        }
        
        RecordMouseClick("right", mouseX, mouseY)
        LastActionTime := currentTime
        
        ; Wait for button release
        KeyWait, RButton
    }
    
    ; Check keyboard
    Loop, Parse, KeysToWatch, `,
    {
        key := A_LoopField
        if (GetKeyState(key, "P")) {
            timeFromLast := currentTime - LastActionTime
            if (timeFromLast > 100) {
                RecordSleep(timeFromLast)
            }
            
            RecordKeyPress(key)
            LastActionTime := currentTime
            
            ; Wait for key release
            KeyWait, %key%
        }
    }
return

;Record a mouse movement
RecordMouseMove(x, y) {
    action := "MouseMove, " . x . ", " . y . ", 2"
    RecordAction(action)
}

;Record a mouse click
RecordMouseClick(button, x, y) {
    action := "Click"
    if (button != "left") {
        action := button . " " . action
    }
    
    PixelGetColor, pixelColor, %x%, %y%, RGB
    
    ; Add coordinates as comment
    action .= " ; At position " . x . ", " . y . " (Color: " . pixelColor . ")"
    
    RecordAction(action)
}

;Record a key press
RecordKeyPress(key) {
    action := "Send, {" . key . "}"
    RecordAction(action)
}

;Record a sleep command
RecordSleep(ms) {
    ; Round to nearest 100ms for readability
    ms := Round(ms / 100) * 100
    if (ms < 100) ms := 100
    
    action := "Sleep, " . ms
    RecordAction(action)
}

;Add action to recording
RecordAction(action) {
    global RecordedActions
    
    RecordedActions.Push(action)
    GuiControl,, ActionsCount, % RecordedActions.Length() . " actions recorded"
    
    AddToRecording(action)
}

;Add text to the recording display
AddToRecording(text) {
    GuiControlGet, currentText,, RecordingText
    
    if (currentText = "Press F1 to start recording...") {
        GuiControl,, RecordingText, %text%
    } else {
        GuiControl,, RecordingText, %currentText%`n%text%
    }
    
    ; Scroll to bottom
    SendMessage, 0x115, 7, 0, Edit1, A
}

;Format time in HH:MM:SS
FormatTime(seconds) {
    hours := Floor(seconds / 3600)
    minutes := Floor(Mod(seconds, 3600) / 60)
    secs := Floor(Mod(seconds, 60))
    
    return Format("{:02}:{:02}:{:02}", hours, minutes, secs)
}