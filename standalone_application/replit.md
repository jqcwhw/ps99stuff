# AI Game Automation Bot

## Overview

This is a comprehensive AI-powered game automation system that uses computer vision, machine learning, and natural language processing to automate gameplay tasks. The bot can perform actions like opening chests, hatching eggs, and learning from game patterns through an intelligent automation engine. It features a web-based dashboard for monitoring and controlling the bot, along with macro recording/playback capabilities and knowledge management from external sources.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Web Dashboard**: Flask-based web application providing real-time monitoring and control
- **User Interface**: Bootstrap-styled HTML templates with JavaScript for interactive controls
- **Real-time Updates**: AJAX-based status polling for live screen capture and bot status
- **Command Interface**: Natural language command input with quick action buttons

### Backend Architecture
- **Modular Core Systems**: Separate modules for vision, automation, learning, knowledge management, and macros
- **Command Processing**: Natural language processing engine that translates user commands into bot actions
- **Threading Architecture**: Multi-threaded design for concurrent screen capture, automation execution, and web serving
- **Queue-based Actions**: Action queue system for managing automation tasks safely

### Computer Vision System
- **Screen Capture**: Real-time screenshot capture using PyAutoGUI
- **Template Matching**: OpenCV-based image recognition for game elements (chests, eggs, breakables)
- **Color-based Detection**: HSV color range matching for identifying game objects
- **Region of Interest**: Configurable screen regions for focused analysis

### Automation Engine
- **Mouse/Keyboard Control**: PyAutoGUI-based input automation with human-like movement simulation
- **Safety Mechanisms**: Forbidden regions and safe zones to prevent unwanted interactions
- **Action Recording**: Macro system for recording and replaying complex action sequences
- **Queue Management**: Thread-safe action queue with configurable delays and timing

### Learning and Adaptation
- **Pattern Recognition**: Machine learning system that identifies successful action patterns
- **Experience Memory**: Deque-based memory system storing bot experiences for learning
- **Success/Failure Tracking**: Statistical analysis of action outcomes to improve decision making
- **Knowledge Base**: JSON-based storage for game information, strategies, and learned patterns

### Enhanced Web Scraping Integration
- **Multi-Method Scraping**: Advanced content extraction using multiple fallback techniques
- **Gaming-Specific Intelligence**: Specialized scrapers for Roblox, PS99, Discord, Reddit, and API data
- **Knowledge Integration**: Automatic incorporation of structured and unstructured content into knowledge base
- **Rate Limiting & Safety**: User agent rotation, intelligent delays, and comprehensive error handling
- **Metadata Processing**: Automatic extraction and processing of game-specific metadata and IDs

## External Dependencies

### Core Python Libraries
- **Flask**: Web framework for the dashboard interface
- **OpenCV (cv2)**: Computer vision and image processing
- **PyAutoGUI**: Screen capture and input automation
- **NumPy**: Numerical operations for image analysis
- **Requests**: HTTP client for web scraping functionality

### Web Scraping
- **Trafilatura**: Main content extraction library for web scraping
- **BeautifulSoup/lxml**: HTML parsing (implied dependency of trafilatura)

### Frontend Dependencies
- **Bootstrap 5.1.3**: CSS framework for responsive UI design
- **Font Awesome 6.0.0**: Icon library for UI elements
- **Vanilla JavaScript**: Client-side functionality without additional frameworks

### Reference Automation Techniques
- **Direct Memory Scanning**: Advanced memory reading techniques for non-invasive game state detection
- **Coordinate Recording**: Precise mouse position and pixel color recording for automation development
- **API Integration**: Direct API calls to game servers for authoritative data (Roblox, PS99)
- **Multi-Language Support**: Integration of AutoHotkey, Python, JavaScript, and TypeScript automation techniques
- **Adaptive Learning**: Pattern recognition and optimization based on successful automation sequences

### Data Storage
- **JSON Files**: Configuration, knowledge base, macros, and game elements storage
- **Pickle Files**: Binary storage for learning data and experience memory
- **Reference Macros**: Comprehensive library of automation techniques from multiple sources
- **File-based Architecture**: No external database dependencies, all data stored locally

### System Integration
- **Threading**: Python threading for concurrent operations
- **Logging**: Built-in Python logging with rotating file handlers
- **Path Management**: Pathlib for cross-platform file system operations
- **Queue Management**: Python queue for thread-safe action management

## Recent Enhancements

### August 16, 2025 - Enhanced Web Scraper Integration
- **Enhanced Web Scraper**: Replaced basic scraper with advanced multi-method scraper
- **Reference Macros Library**: Added comprehensive automation techniques from user-provided files
- **Gaming-Specific Intelligence**: Added specialized handling for Roblox, PS99, Discord, and API data
- **Knowledge Manager Enhancement**: Updated to process structured metadata and game-specific content
- **Memory Scanning Techniques**: Documented direct memory address scanning methods for PS99
- **Coordinate Recording Systems**: Integrated precise mouse and pixel color recording tools