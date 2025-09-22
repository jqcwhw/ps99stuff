#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
CoordMode, Mouse, Screen
CoordMode, Pixel, Screen

;PS99 Window Spy Tool
;Records mouse coordinates and pixel colors for PS99 egg collection

;Create GUI for info display
Gui, +AlwaysOnTop +ToolWindow
Gui, Color, EEEEEE
Gui, Font, s10
Gui, Add, Text, w300 vMousePos, Mouse Position: X=0, Y=0
Gui, Add, Text, w300 vPixelColor, Color: 0x000000
Gui, Add, Text, w300 vWindow, Window: None
Gui, Add, Text, w300 vControl, Control: None
Gui, Add, Button, w80 gCapturePosition, Save Position
Gui, Add, Text, cBlue, Press F1 to start/stop logging
Gui, Add, Text, cBlue, Press F2 to save current position
Gui, Add, Text, cBlue, Press F3 to save screenshot
Gui, Add, Text, cBlue, Press Esc to exit

Gui, Show, w320 h250, PS99 Position Spy

;Create a log file
LogFile := "PS99_Position_Log.txt"
FileDelete, %LogFile%
FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
FileAppend, 
(
===== PS99 Position Logger (%timestamp%) =====

), %LogFile%

;Initialize variables
Logging := false
LogCount := 0

;Set up hotkeys
F1::ToggleLogging()
F2::SaveCurrentPosition()
F3::SaveScreenshot()
Esc::ExitApp

;Start the information update timer
SetTimer, UpdateInfo, 50

;Exit the application when GUI is closed
GuiClose:
ExitApp

;===================== Functions =====================

;Toggle position logging on/off
ToggleLogging() {
    global Logging, LogFile
    Logging := !Logging
    
    if (Logging) {
        FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
        FileAppend, 
(

----- Started logging at %timestamp% -----

), %LogFile%
        
        TrayTip, PS99 Position Spy, Position logging started, 2, 1
    } else {
        FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
        FileAppend, 
(

----- Stopped logging at %timestamp% -----

), %LogFile%
        
        TrayTip, PS99 Position Spy, Position logging stopped, 2, 1
    }
}

;Save current position with label
SaveCurrentPosition() {
    global LogFile
    
    MouseGetPos, mouseX, mouseY, windowID, controlID
    WinGetTitle, windowTitle, ahk_id %windowID%
    WinGetClass, windowClass, ahk_id %windowID%
    PixelGetColor, pixelColor, %mouseX%, %mouseY%, RGB
    
    InputBox, posLabel, Save Position, What is this position for?`n(e.g. "Angelus Egg" or "Buy Button"), , 300, 150
    if (!ErrorLevel) {  ;if user didn't cancel
        FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
        
        FileAppend, 
(
[%timestamp%] SAVED POSITION: "%posLabel%"
  X=%mouseX%, Y=%mouseY%
  Color=%pixelColor%
  Window="%windowTitle%" (Class=%windowClass%)
  Control=%controlID%

), %LogFile%
        
        TrayTip, Position Saved, Saved "%posLabel%" at X=%mouseX%, Y=%mouseY%, 2, 1
    }
}

;Save screenshot with current position
SaveScreenshot() {
    global LogFile
    
    MouseGetPos, mouseX, mouseY, windowID
    WinGetTitle, windowTitle, ahk_id %windowID%
    
    ;Create a unique filename
    FormatTime, timeStamp,, yyyy-MM-dd_HH-mm-ss
    screenshotFile := "PS99_Screenshot_" . timeStamp . ".png"
    
    ;Take screenshot
    Send, {PrintScreen}
    Sleep, 200
    
    ;Use Paint to save it
    Run, mspaint
    WinWaitActive, ahk_class MSPaintApp,,3
    if (ErrorLevel)
        return
        
    Sleep, 500
    Send, ^v
    Sleep, 500
    Send, ^s
    Sleep, 500
    
    WinWaitActive, Save As,,3
    if (ErrorLevel) {
        WinClose, ahk_class MSPaintApp
        return
    }
    
    Sleep, 500
    Send, %screenshotFile%
    Sleep, 200
    Send, {Enter}
    Sleep, 500
    
    ;Close Paint
    WinClose, ahk_class MSPaintApp
    
    ;Log the screenshot
    FormatTime, timestamp,, yyyy-MM-dd HH:mm:ss
    FileAppend, 
(
[%timestamp%] SCREENSHOT: Saved to %screenshotFile%
  Mouse position: X=%mouseX%, Y=%mouseY%
  Window: %windowTitle%

), %LogFile%
    
    TrayTip, Screenshot Saved, Saved to %screenshotFile%, 2, 1
}

;Update the display with current mouse and window info
UpdateInfo:
    MouseGetPos, mouseX, mouseY, windowID, controlID
    PixelGetColor, pixelColor, %mouseX%, %mouseY%, RGB
    WinGetTitle, windowTitle, ahk_id %windowID%
    WinGetClass, windowClass, ahk_id %windowID%
    
    GuiControl,, MousePos, Mouse Position: X=%mouseX%, Y=%mouseY%
    GuiControl,, PixelColor, Color: %pixelColor%
    GuiControl,, Window, Window: %windowTitle%
    GuiControl,, Control, Control: %controlID%
    
    if (Logging) {
        ;Every 10th update (about 0.5 seconds), log the position if mouse has moved
        static lastLogX := 0, lastLogY := 0, updateCount := 0
        
        updateCount++
        if (updateCount >= 10) {
            updateCount := 0
            
            ;Only log if position changed significantly
            if (Abs(lastLogX - mouseX) > 5 || Abs(lastLogY - mouseY) > 5) {
                lastLogX := mouseX
                lastLogY := mouseY
                LogCount++
                
                FileAppend, 
(
[%LogCount%] Position: X=%mouseX%, Y=%mouseY%, Color=%pixelColor%
  Window="%windowTitle%"

), %LogFile%
            }
        }
    }
return

;Capture current position button handler
CapturePosition:
    SaveCurrentPosition()
return