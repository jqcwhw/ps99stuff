# AI Game Bot - Standalone Application

## Overview
This package contains everything needed to create a standalone executable version of the AI Game Bot that can run on any Windows/Mac/Linux computer without requiring Python installation.

## Creating the Standalone Application

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create Standalone Executable

#### For Windows:
```bash
pyinstaller --onefile --windowed --add-data "data;data" --add-data "static;static" --add-data "templates;templates" --add-data "core;core" --add-data "utils;utils" --add-data "attached_assets;attached_assets" main.py
```

#### For macOS:
```bash
pyinstaller --onefile --windowed --add-data "data:data" --add-data "static:static" --add-data "templates:templates" --add-data "core:core" --add-data "utils:utils" --add-data "attached_assets:attached_assets" main.py
```

#### For Linux:
```bash
pyinstaller --onefile --add-data "data:data" --add-data "static:static" --add-data "templates:templates" --add-data "core:core" --add-data "utils:utils" --add-data "attached_assets:attached_assets" main.py
```

### Step 3: Find Your Executable
The executable will be created in the `dist/` folder:
- Windows: `dist/main.exe`
- macOS: `dist/main`
- Linux: `dist/main`

## Alternative: Create Installer

### Windows Installer with NSIS
1. Install NSIS (Nullsoft Scriptable Install System)
2. Create installer script using the executable

### macOS App Bundle
```bash
pyinstaller --onefile --windowed --add-data "data:data" --add-data "static:static" --add-data "templates:templates" --add-data "core:core" --add-data "utils:utils" --add-data "attached_assets:attached_assets" --name "AI Game Bot" main.py
```

## Running the Standalone Application

### Method 1: Direct Execution
Double-click the executable file. The bot will start with a web interface at `http://localhost:5000`

### Method 2: Command Line Options
```bash
./main --web          # Start web interface
./main --help         # Show all options
```

## Features in Standalone Version
✓ Complete offline functionality
✓ Interactive training system
✓ Computer vision automation
✓ Game element detection
✓ Natural language commands
✓ Zone mapping tools
✓ Macro recording/playback
✓ Knowledge base management
✓ All learning materials included

## Distribution Package Contents
```
standalone_application/
├── core/                    # Bot core systems
├── data/                    # Knowledge base & game data
│   ├── game_elements.json   # Game element templates
│   ├── knowledge_base.json  # Learning data
│   ├── macros.json         # Recorded macros
│   └── reference_macros.json # Reference automation
├── static/                  # Web interface files
├── templates/               # HTML templates
├── utils/                   # Utility functions
├── attached_assets/         # Automation reference files
│   ├── *.ahk               # AutoHotkey scripts
│   ├── *.py                # Python automation examples
│   └── *.js                # JavaScript techniques
├── main.py                 # Main application
├── app.py                  # Web server
└── requirements.txt        # Dependencies
```

## Advanced Options

### Create with Custom Icon
```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "data;data" --add-data "static;static" --add-data "templates;templates" main.py
```

### Create with Hidden Console (Windows)
```bash
pyinstaller --onefile --noconsole --add-data "data;data" --add-data "static;static" --add-data "templates;templates" main.py
```

## System Requirements
- Windows 10+ / macOS 10.14+ / Linux Ubuntu 18.04+
- 4GB RAM minimum (8GB recommended)
- 1GB disk space
- Screen resolution 1280x720 or higher
- Internet connection (for AI features with API keys)

## Troubleshooting

### Common Issues:
1. **Missing dependencies**: Ensure all files are in same directory as executable
2. **Permission errors**: Run as administrator (Windows) or with sudo (Linux/Mac)
3. **Antivirus blocking**: Add executable to antivirus whitelist
4. **Port conflicts**: Change port in config if 5000 is occupied

### Performance Tips:
- Close unnecessary applications for better computer vision performance
- Run on primary monitor for best game detection
- Ensure good lighting for visual recognition

## API Key Configuration
For enhanced AI features, place API keys in a `.env` file next to the executable:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Support
Refer to README.md for detailed usage instructions and feature documentation.