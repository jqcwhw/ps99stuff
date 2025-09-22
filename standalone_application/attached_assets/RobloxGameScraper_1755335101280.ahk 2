#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SendMode Input
SetBatchLines -1

; Roblox Game Link Scraper
; This script extracts metadata from Roblox game links:
; - Game/Place ID
; - Universe ID
; - Creator ID and Type
; - Game Name
; - Private Server Info

; Create UI
Gui, +AlwaysOnTop
Gui, Color, 0x2D2D2D
Gui, Font, s12 cWhite, Segoe UI
Gui, Add, Text, w500 Center, Roblox Game Link Scraper

Gui, Font, s10 cWhite
Gui, Add, Text, w100 xm, Game URL:
Gui, Add, Edit, vGameLink w390 x+10, https://www.roblox.com/games/8737899170/Pet-Simulator-99

Gui, Add, Button, xm w150 gScrapeGameInfo, Scrape Info
Gui, Add, Button, x+10 w150 gClearResults, Clear Results
Gui, Add, Button, x+10 w150 gSaveToFile, Save Results

Gui, Font, s10 cLime
Gui, Add, GroupBox, xm w500 h250, Game Information
Gui, Font, s9 cYellow
Gui, Add, Edit, xm+10 yp+20 w480 h220 vResultsBox ReadOnly, Enter a Roblox game link and click "Scrape Info"

Gui, Font, s9 c999999
Gui, Add, Text, xm w500, Status: Ready

Gui, Show, w520 h400, Roblox Game Link Scraper

; Function to extract Game ID from link
ExtractGameID(url) {
    ; Different URL patterns
    if RegExMatch(url, "games/(\d+)", gameID)
        return gameID1
    if RegExMatch(url, "place\?id=(\d+)", gameID)
        return gameID1
    if RegExMatch(url, "places/(\d+)", gameID)
        return gameID1
    
    return "Not found"
}

; Scrape game info
ScrapeGameInfo:
    Gui, Submit, NoHide
    GuiControl,, ResultsBox, Scraping link: %GameLink%...`n`n
    
    ; Extract game ID
    gameID := ExtractGameID(GameLink)
    if (gameID = "Not found") {
        GuiControl,, ResultsBox, Error: Could not extract Game ID from the link.
        return
    }
    
    AppendResult("Game/Place ID: " . gameID)
    
    ; Create temporary file for curl output
    tempFile := A_Temp . "\robloxgamescrape.json"
    
    ; Get universe ID
    RunWait, %comspec% /c curl -s "https://apis.roblox.com/universes/v1/places/%gameID%/universe" > "%tempFile%", , Hide
    FileRead, universeData, %tempFile%
    
    if InStr(universeData, "universeId") {
        RegExMatch(universeData, "universeId""\s*:\s*(\d+)", universeID)
        AppendResult("Universe ID: " . universeID1)
        
        ; Get game details from universe ID
        RunWait, %comspec% /c curl -s "https://games.roblox.com/v1/games?universeIds=%universeID1%" > "%tempFile%", , Hide
        FileRead, gameData, %tempFile%
        
        ; Extract game info
        RegExMatch(gameData, """name""\s*:\s*""(.+?)""", gameName)
        RegExMatch(gameData, """rootPlaceId""\s*:\s*(\d+)", rootPlaceID)
        RegExMatch(gameData, """playing""\s*:\s*(\d+)", playingCount)
        RegExMatch(gameData, """visits""\s*:\s*(\d+)", visitsCount)
        RegExMatch(gameData, """id""\s*:\s*(\d+),\s*""name""\s*:\s*""(.+?)""", creatorInfo)
        RegExMatch(gameData, """type""\s*:\s*""(.+?)""", creatorType)
        
        ; Clean up game name (remove escape sequences)
        cleanName := RegExReplace(gameName1, "\\u[0-9a-fA-F]{4}", "?")
        
        AppendResult("Game Name: " . cleanName)
        AppendResult("Root Place ID: " . rootPlaceID1)
        AppendResult("Creator ID: " . creatorInfo1)
        AppendResult("Creator Name: " . creatorInfo2)
        AppendResult("Creator Type: " . creatorType1)
        AppendResult("Players Online: " . playingCount1)
        AppendResult("Total Visits: " . visitsCount1)
        
        ; Check if private server
        if (gameID != rootPlaceID1) {
            AppendResult("`nThis appears to be a private server or custom place.")
            AppendResult("Main Game: https://www.roblox.com/games/" . rootPlaceID1)
        }
        
        ; Get possible connection methods
        AppendResult("`nAccess Methods:")
        AppendResult("1. Direct Link: " . GameLink)
        AppendResult("2. Universe Link: https://www.roblox.com/universe-id/" . universeID1)
        AppendResult("3. Creator Profile: https://www.roblox.com/" . (creatorType1 = "Group" ? "groups/" : "users/") . creatorInfo1)
        
        ; Get additional connection possibilities
        RunWait, %comspec% /c curl -s "https://games.roblox.com/v1/games/%rootPlaceID1%/servers/public" > "%tempFile%", , Hide
        FileRead, serversData, %tempFile%
        
        if InStr(serversData, "data") {
            AppendResult("`nPublic servers available. Join through main game link.")
        }
        
        ; Check if private servers are allowed
        if InStr(gameData, """createVipServersAllowed""\s*:\s*true") {
            AppendResult("Private servers are allowed for this game.")
        } else {
            AppendResult("Private servers are NOT allowed for the main game.")
        }
    } else {
        AppendResult("Could not retrieve universe information.")
    }
    
    ; Get direct HTML data
    RunWait, %comspec% /c curl -s -L "https://www.roblox.com/games/%gameID%" > "%tempFile%", , Hide
    FileRead, htmlData, %tempFile%
    
    ; Check for alternative place IDs in the HTML
    relatedIDs := ""
    pos := 1
    While pos := RegExMatch(htmlData, "data-place-id=""(\d+)""", placeMatch, pos + StrLen(placeMatch)) {
        if (placeMatch1 != gameID && !InStr(relatedIDs, placeMatch1)) {
            relatedIDs .= placeMatch1 . "`n"
        }
    }
    
    if (relatedIDs) {
        AppendResult("`nRelated Place IDs found:")
        AppendResult(relatedIDs)
    }
    
    ; Clean up
    FileDelete, %tempFile%
return

; Append to results
AppendResult(text) {
    GuiControlGet, currentText,, ResultsBox
    GuiControl,, ResultsBox, %currentText%%text%`n
}

; Clear results
ClearResults:
    GuiControl,, ResultsBox, Enter a Roblox game link and click "Scrape Info"
    GuiControl,, GameLink, https://www.roblox.com/games/8737899170/Pet-Simulator-99
return

; Save results to file
SaveToFile:
    FormatTime, timestamp,, yyyy-MM-dd_HHmmss
    GuiControlGet, results,, ResultsBox
    GuiControlGet, link,, GameLink
    
    gameID := ExtractGameID(link)
    filename := "RobloxGameInfo_" . gameID . "_" . timestamp . ".txt"
    
    FileDelete, %filename%
    FileAppend, %results%, %filename%
    
    if ErrorLevel
        MsgBox, Error saving results to file.
    else
        MsgBox, Results saved to %filename%
return

GuiClose:
ExitApp