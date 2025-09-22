# AI Game Automation Bot

A comprehensive AI-powered game automation system that uses computer vision, machine learning, and natural language processing to automate gameplay tasks. The bot features interactive training capabilities, web-based monitoring, and intelligent game element recognition.

## 🚀 Features

### Interactive Training System
- **Item Learning**: Hover over game items and press SPACE to teach the bot what to recognize
- **Zone Mapping**: Click 4 corners to define custom game areas (breakables, safe zones, fishing spots)
- **Natural Language Commands**: Communicate with the bot using everyday language
- **Smart Recognition**: Distinguishes between similar items (different sized chests, grass vs water)

### Computer Vision & Automation
- **Real-time Screen Capture**: Continuous monitoring of game state
- **Template Matching**: Advanced OpenCV-based item detection
- **Color Analysis**: Smart color signature extraction for item recognition
- **Mouse/Keyboard Automation**: Human-like movement and interaction simulation

### Learning & Knowledge Management
- **Experience Memory**: Learns from successful and failed actions
- **Web Scraping**: Automatically gathers game information from multiple sources
- **Knowledge Base**: Stores strategies, game data, and learned patterns
- **Autonomous Learning**: Continuously improves performance through pattern recognition

### Web Dashboard
- **Real-time Monitoring**: Live screen capture and bot status
- **Interactive Controls**: Start training modes, execute commands, manage macros
- **Command History**: Track all executed commands and results
- **Status Tracking**: Monitor learned items, zones, and system health

### Macro System
- **Record & Playback**: Capture complex action sequences
- **Macro Library**: Store and reuse automation routines
- **Action Queue**: Thread-safe execution of automation tasks

## 🎯 Supported Game Actions

- **Chest Opening**: Automatically find and open treasure chests
- **Egg Hatching**: Locate and hatch eggs throughout the game
- **Breakables Farming**: Stay in designated areas and farm breakable objects
- **Resource Collection**: Gather specific items or resources
- **Zone Navigation**: Move within defined boundaries and avoid restricted areas

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenCV
- Flask
- PyAutoGUI (for desktop environments)

### Quick Start

1. **Start the Bot**:
   ```bash
   python main.py --web
   ```

2. **Access Web Dashboard**:
   Open your browser and go to `http://localhost:5000`

3. **Begin Interactive Training**:
   - Click "Learn Items" and hover over game elements, then press SPACE
   - Click "Map Zones" and define areas by clicking 4 corners
   - Use natural language commands like "map the breakable area"

### Command Line Usage

**Interactive Mode**:
```bash
python main.py
```

**Execute Single Command**:
```bash
python main.py --command "open chests"
```

**Web Interface with Custom Port**:
```bash
python main.py --web --port 8080
```

**Debug Mode**:
```bash
python main.py --web --debug
```

## 📋 Available Commands

### Game Actions
- `open chests` - Find and open treasure chests
- `hatch eggs` - Find and hatch eggs
- `stay in breakables` - Move to and stay in breakables area
- `farm [item]` - Farm specific items or resources

### Learning & Knowledge
- `learn from [file/url]` - Learn from file or website
- `update knowledge` - Update knowledge base from developer blogs
- `analyze screen` - Analyze current screen state

### Macro System
- `record macro [name]` - Start recording a macro
- `stop recording` - Stop macro recording
- `play macro [name]` - Play recorded macro
- `list macros` - List available macros

### System Commands
- `status` - Show system status
- `config` - Show configuration
- `help` - Show available commands

## 🎮 Interactive Training Guide

### Learning Items
1. Start "Learn Items" mode from the web dashboard
2. Hover your mouse over any game item
3. Press SPACE and specify the item type (chest, egg, breakable, etc.)
4. The bot captures a screenshot and learns the item's visual signature

### Mapping Zones
1. Start "Map Zones" mode from the web dashboard
2. Click 4 corners on the screen to define a boundary
3. Specify zone type (breakables, fishing, safe zone)
4. The bot will respect these boundaries during automation

### Natural Language Interaction
Type commands like:
- "map the breakable area"
- "learn chest items" 
- "find similar items on screen"
- "analyze what's currently visible"

## 🏗️ Architecture

### Core Systems
- **Vision System**: OpenCV-based screen analysis and object detection
- **Automation Engine**: PyAutoGUI-based input simulation with safety mechanisms
- **Learning System**: Pattern recognition and experience-based improvement
- **Knowledge Manager**: Information storage and retrieval from multiple sources
- **Interactive Trainer**: Real-time teaching and mapping capabilities

### Data Storage
- **JSON Files**: Configuration, knowledge base, macros, and game elements
- **Pickle Files**: Binary storage for learning data and experience memory
- **Local Storage**: No external database dependencies

### Safety Features
- **Forbidden Regions**: Prevents clicking on unsafe screen areas
- **Boundary Enforcement**: Stays within defined game windows
- **Rate Limiting**: Human-like timing and delays
- **Error Handling**: Graceful recovery from automation failures

## 🔧 Configuration

The bot automatically creates configuration files on first run:
- `config/settings.json` - Main configuration
- `data/learned_items.json` - Interactive training data
- `data/game_zones.json` - Mapped zones and boundaries
- `data/knowledge_base.json` - Game information and strategies

## 📊 Web Dashboard Features

Access the dashboard at `http://localhost:5000` to:
- Monitor real-time screen capture
- Execute commands through a web interface
- Start interactive training modes
- View system status and statistics
- Manage macros and recorded actions
- Track learning progress and knowledge base growth

## 🤖 Autonomous Learning

The bot continuously improves by:
- Analyzing successful action patterns
- Learning from failures and adapting strategies
- Gathering information from game wikis and forums
- Building a comprehensive knowledge base
- Optimizing timing and movement patterns

## 🎯 Game Compatibility

Designed primarily for Roblox games with specific optimizations for:
- Pet Simulator 99
- Chest and egg-based mechanics
- Breakable farming systems
- Zone-based gameplay

The modular architecture allows easy adaptation to other games.

## 📝 Development

The bot is built with a modular architecture:
- `core/` - Main bot systems and logic
- `utils/` - Utility functions and helpers
- `data/` - Storage for learned data and configurations
- `templates/` - Web interface templates
- `static/` - CSS, JavaScript, and assets

## 🔄 Updates & Learning

The bot automatically:
- Downloads game updates and patch notes
- Learns new strategies from community sources
- Adapts to game changes and new content
- Maintains an up-to-date knowledge base

## ⚡ Quick Commands

**Start Bot**: `python main.py --web`
**Train Items**: Hover + SPACE in Learn Items mode
**Map Zones**: Click 4 corners in Map Zones mode
**Execute Command**: Type in command box or use quick action buttons
**Record Macro**: Use Record button, perform actions, then Stop
**Play Macro**: Select macro from dropdown and click Play

---

For support or questions, check the web dashboard status panel or review the command history in the terminal output.