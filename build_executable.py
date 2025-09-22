#!/usr/bin/env python3
"""
AI Game Bot - Standalone Executable Builder
This script builds a standalone executable for the AI Game Bot.
"""

import os
import sys
import subprocess
import platform
import shutil

def check_pyinstaller():
    """Check if PyInstaller is available."""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True

def build_executable():
    """Build the standalone executable."""
    system = platform.system().lower()
    print(f"🏗️  Building executable for {system}")
    
    # Base command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name", "AI_Game_Bot",
    ]
    
    # Add data directories
    data_dirs = [
        ("data", "data"),
        ("static", "static"), 
        ("templates", "templates"),
        ("core", "core"),
        ("utils", "utils"),
        ("attached_assets", "attached_assets")
    ]
    
    # Platform-specific separators
    separator = ";" if system == "windows" else ":"
    
    for src, dst in data_dirs:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src}{separator}{dst}"])
    
    # Platform-specific options
    if system == "windows":
        cmd.append("--windowed")  # Hide console window
    
    # Add main script
    cmd.append("main.py")
    
    print("🔨 Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✓ Build completed successfully!")
        
        # Show output location
        exe_name = "AI_Game_Bot.exe" if system == "windows" else "AI_Game_Bot"
        exe_path = os.path.join("dist", exe_name)
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
        
        # Create distribution package
        create_distribution_package(exe_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def create_distribution_package(exe_path):
    """Create a complete distribution package."""
    print("📦 Creating distribution package...")
    
    dist_dir = "AI_Game_Bot_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    
    os.makedirs(dist_dir)
    
    # Copy executable
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, dist_dir)
    
    # Copy essential files
    essential_files = [
        "README.md",
        "STANDALONE_INSTRUCTIONS.md",
        "requirements.txt"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)
    
    # Create sample config file
    config_content = """# AI Game Bot Configuration
# Add your API keys here for enhanced functionality

OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Change the web interface port
# PORT=5000
"""
    
    with open(os.path.join(dist_dir, "config.env"), "w") as f:
        f.write(config_content)
    
    # Create startup scripts
    if platform.system().lower() == "windows":
        create_windows_startup(dist_dir)
    else:
        create_unix_startup(dist_dir)
    
    print(f"✓ Distribution package created in: {dist_dir}")

def create_windows_startup(dist_dir):
    """Create Windows startup script."""
    bat_content = """@echo off
echo Starting AI Game Bot...
echo.
echo Web interface will be available at: http://localhost:5000
echo Press Ctrl+C to stop the bot
echo.
AI_Game_Bot.exe
pause
"""
    with open(os.path.join(dist_dir, "Start_AI_Game_Bot.bat"), "w") as f:
        f.write(bat_content)

def create_unix_startup(dist_dir):
    """Create Unix startup script."""
    sh_content = """#!/bin/bash
echo "Starting AI Game Bot..."
echo ""
echo "Web interface will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the bot"
echo ""
./AI_Game_Bot
"""
    script_path = os.path.join(dist_dir, "start_ai_game_bot.sh")
    with open(script_path, "w") as f:
        f.write(sh_content)
    
    # Make executable
    os.chmod(script_path, 0o755)

def main():
    """Main build function."""
    print("🤖 AI Game Bot - Standalone Executable Builder")
    print("=" * 50)
    
    if check_pyinstaller():
        build_executable()
        print("\n🎉 Build process completed!")
        print("\nNext steps:")
        print("1. Navigate to the AI_Game_Bot_Distribution folder")
        print("2. Run the startup script to launch the bot")
        print("3. Open http://localhost:5000 in your browser")

if __name__ == "__main__":
    main()