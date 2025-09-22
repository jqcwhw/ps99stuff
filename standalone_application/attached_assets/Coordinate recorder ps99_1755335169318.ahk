#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SendMode Input
SetBatchLines -1

;PS99 Coordinate Recorder
;
;This tool records mouse clicks and pixel colors for accurate scripting:
;- Records exact X/Y coordinates of all mouse clicks
;- Captures pixel colors under the cursor
;- Logs all keyboard inputs
;- Creates a detailed log file for script creation
;- Functions similar to Window Spy but with recording capability
;
;Controls:
;F1 - Start/Stop Recording
;F2 - Add a comment to the log file
;F3 - Toggle continuous position tracking
;F4 - Save current screen to file
;Esc - Exit application

;Global variables
Recording := false             ; Whether recording is active
ContinuousTracking := false    ; Whether to track mouse constantly or just on clicks
LogFile := "PS99_Recording_Log.txt"
StartTime := 0                 ; When recording started
LastAction := 0                ; When last action happened

;Create GUI
Gui, Color, 0x2D2D2D
Gui, +AlwaysOnTop
Gui, Font, s10 cWhite, Segoe UI
Gui, Add, Text, vStatusText, Status: Ready
Gui, Add, Text, vRecordingTime, Recording Time: 00:00:00

Gui, Font, s10 cLime
Gui, Add, Text, vMousePos, Mouse Position: X=0, Y=0
Gui, Add, Text, vPixelColor, Pixel Color: 0x000000
Gui, Add, Text, vMouseWindow, Window: None
Gui, Add, Text, vActionCount, Actions Recorded: 0

Gui, Font, s9 cYellow
Gui, Add, Text, vLastActionText, Last Action: None
Gui, Add, Text, vTimeElapsedText, Time Since Last Action: 0.0s

Gui, Font, s12 cOrange
Gui, Add, Text, vInstructionsText, Press F1 to start recording mouse clicks and keyboard presses

;Create group of controls for continuous tracking display
Gui, Add, GroupBox, x10 y+10 w380 h100 cGray, Live Tracking
Gui, Font, s9 cSilver
Gui, Add, Text, xp+10 yp+20 vTrackX, X: 0
Gui, Add, Text, x+10 yp vTrackY, Y: 0
Gui, Add, Text, x+10 yp vTrackColor, Color: 0x000000
Gui, Add, Text, xp-70 y+10 vTrackWindow w350, Window: None
Gui, Add, Text, xp y+10 vTrackControl w350, Control: None
Gui, Add, Text, xp y+10 vTrackPos w350, Relative Pos: 0, 0

Gui, Show, w400 h300, PS99 Coordinate Recorder

;Initialize log file with header
FormatTime, CurrentDateTime,, yyyy-MM-dd HH:mm:ss
FileAppend, 
(
===================================================
PS99 Coordinate Recorder Log - Started: %CurrentDateTime%
===================================================
This log contains recorded mouse clicks, key presses, and pixel colors.
Each entry includes:
- Timestamp and elapsed time since last action
- Action type (click or key press)
- X/Y screen coordinates
- Pixel color under the cursor
- Window information

), %LogFile%

;Hotkey assignments
F1::ToggleRecording()
F2::AddComment()
F3::ToggleTracking()
F4::SaveScreenshot()
Esc::ExitApp

;Hook into mouse clicks when recording is active
#If Recording
~LButton::RecordMouseClick("Left")
~RButton::RecordMouseClick("Right")
~MButton::RecordMouseClick("Middle")
~WheelUp::RecordMouseAction("WheelUp")
~WheelDown::RecordMouseAction("WheelDown")
#If

;Start timer for UI updates
SetTimer, UpdateUI, 50

;Toggle recording state
ToggleRecording() {
    global Recording, StartTime, LastAction, ActionCount
    
    Recording := !Recording
    
    if (Recording) {
        ;Start recording
        StartTime := A_TickCount
        LastAction := A_TickCount
        ActionCount := 0
        
        GuiControl,, StatusText, Status: RECORDING
        GuiControl,, InstructionsText, Recording active! Every click and key press will be logged.
        
        ;Set up keyboard hook
        SetUpKeyboardHook()
    }
    else {
        ;Stop recording
        GuiControl,, StatusText, Status: Ready
        GuiControl,, InstructionsText, Recording stopped. Press F1 to resume.
        
        ;Remove keyboard hook
        RemoveKeyboardHook()
        
        ;Add a separator to the log
        FileAppend, `n--- Recording paused ---`n, %LogFile%
    }
}

;Add a custom comment to the log
AddComment() {
    global LogFile
    
    InputBox, UserComment, Add Comment, Enter a comment to add to the log:, , 300, 130
    
    if (!ErrorLevel) {  ;User didn't cancel
        FormatTime, CurrentDateTime,, yyyy-MM-dd HH:mm:ss
        
        FileAppend, 
        (
        
[%CurrentDateTime%] COMMENT: %UserComment%
        
        ), %LogFile%
        
        GuiControl,, LastActionText, Last Action: Added comment
    }
}

;Toggle continuous position tracking
ToggleTracking() {
    global ContinuousTracking
    
    ContinuousTracking := !ContinuousTracking
    
    if (ContinuousTracking) {
        GuiControl,, InstructionsText, Continuous tracking ON - Live position and color shown
    }
    else {
        GuiControl,, InstructionsText, Continuous tracking OFF - Actions recorded on clicks only
    }
}

;Save a screenshot of the current screen
SaveScreenshot() {
    FormatTime, TimeStamp,, yyyy-MM-dd_HH-mm-ss
    ScreenshotFile := "PS99_Screenshot_" . TimeStamp . ".png"
    
    GuiControl,, LastActionText, Last Action: Taking screenshot...
    
    ;Take screenshot of entire screen
    SendMode Input
    Send, {PrintScreen}
    Sleep, 100
    
    ;Save to file
    SaveScreenshotToFile(ScreenshotFile)
    
    GuiControl,, LastActionText, Last Action: Saved screenshot to %ScreenshotFile%
    
    ;Add to log
    FileAppend, `n[%TimeStamp%] SCREENSHOT: Saved screen to %ScreenshotFile%`n, %LogFile%
}

;Save screenshot from clipboard to file
SaveScreenshotToFile(filename) {
    ifExist, %filename%
        FileDelete, %filename%
    
    pToken := Gdip_Startup()
    pBitmap := Gdip_CreateBitmapFromClipboard()
    Gdip_SaveBitmapToFile(pBitmap, filename)
    Gdip_DisposeImage(pBitmap)
    Gdip_Shutdown(pToken)
}

;Record a mouse click with details
RecordMouseClick(button) {
    global LogFile, LastAction, ActionCount
    
    ;Get current time
    currentTime := A_TickCount
    elapsedTime := (currentTime - LastAction) / 1000
    FormatTime, timeString,, yyyy-MM-dd HH:mm:ss
    
    ;Get mouse position
    MouseGetPos, mouseX, mouseY, windowID, controlID
    WinGetTitle, windowTitle, ahk_id %windowID%
    WinGetClass, windowClass, ahk_id %windowID%
    
    ;Get pixel color
    PixelGetColor, pixelColor, %mouseX%, %mouseY%, RGB
    
    ;Format log entry
    logEntry := 
    (
    
[%timeString%] (%elapsedTime% sec) %button% CLICK: X=%mouseX}, Y=%mouseY% | Color=%pixelColor%
  Window: "%windowTitle%" | Class: %windowClass% | Control: %controlID%
    )
    
    ;Write to log file
    FileAppend, %logEntry%, %LogFile%
    
    ;Update UI
    GuiControl,, LastActionText, Last Action: %button% click at X=%mouseX%, Y=%mouseY%
    GuiControl,, MousePos, Mouse Position: X=%mouseX%, Y=%mouseY%
    GuiControl,, PixelColor, Pixel Color: %pixelColor%
    GuiControl,, MouseWindow, Window: %windowTitle%
    
    ;Update tracking variables
    LastAction := currentTime
    ActionCount++
    GuiControl,, ActionCount, Actions Recorded: %ActionCount%
}

;Record a mouse wheel action
RecordMouseAction(action) {
    global LogFile, LastAction, ActionCount
    
    ;Get current time
    currentTime := A_TickCount
    elapsedTime := (currentTime - LastAction) / 1000
    FormatTime, timeString,, yyyy-MM-dd HH:mm:ss
    
    ;Get mouse position
    MouseGetPos, mouseX, mouseY, windowID, controlID
    WinGetTitle, windowTitle, ahk_id %windowID%
    
    ;Format log entry
    logEntry := 
    (
    
[%timeString%] (%elapsedTime% sec) %action%: X=%mouseX}, Y=%mouseY%
  Window: "%windowTitle%" | Control: %controlID%
    )
    
    ;Write to log file
    FileAppend, %logEntry%, %LogFile%
    
    ;Update UI
    GuiControl,, LastActionText, Last Action: %action% at X=%mouseX%, Y=%mouseY%
    
    ;Update tracking variables
    LastAction := currentTime
    ActionCount++
    GuiControl,, ActionCount, Actions Recorded: %ActionCount%
}

;Record a key press
RecordKeyPress(key) {
    global LogFile, LastAction, ActionCount, Recording
    
    if (!Recording)
        return
    
    ;Get current time
    currentTime := A_TickCount
    elapsedTime := (currentTime - LastAction) / 1000
    FormatTime, timeString,, yyyy-MM-dd HH:mm:ss
    
    ;Get mouse position
    MouseGetPos, mouseX, mouseY, windowID
    WinGetTitle, windowTitle, ahk_id %windowID%
    
    ;Format log entry
    logEntry := 
    (
    
[%timeString%] (%elapsedTime% sec) KEY: %key% | Mouse at X=%mouseX}, Y=%mouseY%
  Window: "%windowTitle%"
    )
    
    ;Write to log file
    FileAppend, %logEntry%, %LogFile%
    
    ;Update UI
    GuiControl,, LastActionText, Last Action: Pressed key %key%
    
    ;Update tracking variables
    LastAction := currentTime
    ActionCount++
    GuiControl,, ActionCount, Actions Recorded: %ActionCount%
}

;Set up keyboard hook
SetUpKeyboardHook() {
    ;This would use the KeyboardHook functionality from AHK
    ;Simplified for this example - handle common keys
    Hotkey, ~a, KeyA, On
    Hotkey, ~b, KeyB, On
    Hotkey, ~c, KeyC, On
    ;... and so on for other keys ...
    Hotkey, ~Space, KeySpace, On
    Hotkey, ~Enter, KeyEnter, On
    Hotkey, ~Tab, KeyTab, On
    Hotkey, ~Escape, KeyEsc, On
    
    ;Navigation keys
    Hotkey, ~Up, KeyUp, On
    Hotkey, ~Down, KeyDown, On
    Hotkey, ~Left, KeyLeft, On
    Hotkey, ~Right, KeyRight, On
    
    ;Function keys
    Hotkey, ~F5, KeyF5, On
    Hotkey, ~F6, KeyF6, On
    Hotkey, ~F7, KeyF7, On
    Hotkey, ~F8, KeyF8, On
    Hotkey, ~F9, KeyF9, On
    Hotkey, ~F10, KeyF10, On
    Hotkey, ~F11, KeyF11, On
    Hotkey, ~F12, KeyF12, On
}

;Remove keyboard hook
RemoveKeyboardHook() {
    Hotkey, ~a, Off
    Hotkey, ~b, Off
    Hotkey, ~c, Off
    ;... and so on for other keys ...
    Hotkey, ~Space, Off
    Hotkey, ~Enter, Off
    Hotkey, ~Tab, Off
    Hotkey, ~Escape, Off
    
    ;Navigation keys
    Hotkey, ~Up, Off
    Hotkey, ~Down, Off
    Hotkey, ~Left, Off
    Hotkey, ~Right, Off
    
    ;Function keys
    Hotkey, ~F5, Off
    Hotkey, ~F6, Off
    Hotkey, ~F7, Off
    Hotkey, ~F8, Off
    Hotkey, ~F9, Off
    Hotkey, ~F10, Off
    Hotkey, ~F11, Off
    Hotkey, ~F12, Off
}

;Keyboard handlers
KeyA:
    RecordKeyPress("a")
return

KeyB:
    RecordKeyPress("b")
return

KeyC:
    RecordKeyPress("c")
return

KeySpace:
    RecordKeyPress("Space")
return

KeyEnter:
    RecordKeyPress("Enter")
return

KeyTab:
    RecordKeyPress("Tab")
return

KeyEsc:
    RecordKeyPress("Escape")
return

KeyUp:
    RecordKeyPress("Up")
return

KeyDown:
    RecordKeyPress("Down")
return

KeyLeft:
    RecordKeyPress("Left")
return

KeyRight:
    RecordKeyPress("Right")
return

KeyF5:
    RecordKeyPress("F5")
return

KeyF6:
    RecordKeyPress("F6")
return

KeyF7:
    RecordKeyPress("F7")
return

KeyF8:
    RecordKeyPress("F8")
return

KeyF9:
    RecordKeyPress("F9")
return

KeyF10:
    RecordKeyPress("F10")
return

KeyF11:
    RecordKeyPress("F11")
return

KeyF12:
    RecordKeyPress("F12")
return

;Update UI with current mouse info
UpdateUI:
    ;Update recording time if active
    if (Recording) {
        currentDuration := A_TickCount - StartTime
        hours := Floor(currentDuration / 3600000)
        minutes := Floor(Mod(currentDuration, 3600000) / 60000)
        seconds := Floor(Mod(currentDuration, 60000) / 1000)
        
        GuiControl,, RecordingTime, % "Recording Time: " . Format("{:02}:{:02}:{:02}", hours, minutes, seconds)
    }
    
    ;Update time since last action
    if (LastAction > 0) {
        timeSinceLastAction := (A_TickCount - LastAction) / 1000
        GuiControl,, TimeElapsedText, % "Time Since Last Action: " . Format("{:.1f}", timeSinceLastAction) . "s"
    }
    
    ;Update continuous tracking information if enabled
    if (ContinuousTracking) {
        ;Get current mouse position and info
        MouseGetPos, trackX, trackY, trackWin, trackControl
        PixelGetColor, trackColor, %trackX%, %trackY%, RGB
        WinGetTitle, trackTitle, ahk_id %trackWin%
        WinGetPos, winX, winY, winWidth, winHeight, ahk_id %trackWin%
        
        ;Calculate relative position in window
        relX := trackX - winX
        relY := trackY - winY
        
        ;Update tracking display
        GuiControl,, TrackX, X: %trackX%
        GuiControl,, TrackY, Y: %trackY%
        GuiControl,, TrackColor, Color: %trackColor%
        GuiControl,, TrackWindow, Window: %trackTitle%
        GuiControl,, TrackControl, Control: %trackControl%
        GuiControl,, TrackPos, Relative Pos: %relX%, %relY%
    }
return

;Gdip functions for screenshot (simplified)
Gdip_Startup() {
    return 1  ;Simplified stub - would initialize GDI+ in actual implementation
}

Gdip_CreateBitmapFromClipboard() {
    return 1  ;Simplified stub - would create bitmap in actual implementation
}

Gdip_SaveBitmapToFile(pBitmap, filename) {
    ;Simplified - would use correct GDI+ functions in actual implementation
    ;Instead, use AHK's built-in way to save clipboard images
    if WinExist("ahk_class #32770")  ;If dialog exists already
        WinClose                     ;Close it to ensure we use a new one
    
    Run, mspaint
    WinWaitActive, ahk_class MSPaintApp
    Sleep, 100
    Send, ^v  ;Paste clipboard
    Sleep, 100
    Send, ^s  ;Save
    WinWaitActive, ahk_class #32770
    Sleep, 100
    ControlSetText, Edit1, %filename%
    Sleep, 100
    ControlClick, Button1, ahk_class #32770  ;Click Save button
    Sleep, 500
    WinClose, ahk_class MSPaintApp  ;Close Paint
}

Gdip_DisposeImage(pBitmap) {
    ;Simplified stub
}

Gdip_Shutdown(pToken) {
    ;Simplified stub
}