#!/usr/bin/env python3
"""
AI Game Automation Bot - Main Entry Point
A comprehensive game automation system with computer vision and learning capabilities
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.logger import setup_logger
from utils.config import Config
from core.vision_system import VisionSystem
from core.automation_engine import AutomationEngine
from core.learning_system import LearningSystem
from core.knowledge_manager import KnowledgeManager
from core.macro_system import MacroSystem
from core.command_processor import CommandProcessor
from core.autonomous_learning_system import AutonomousLearningSystem
from core.interactive_trainer import InteractiveTrainer

class GameBot:
    """Main game automation bot class"""
    
    def __init__(self):
        self.logger = setup_logger('GameBot')
        self.config = Config()
        
        # Initialize core systems
        self.vision_system = VisionSystem()
        self.automation_engine = AutomationEngine()
        self.learning_system = LearningSystem()
        self.knowledge_manager = KnowledgeManager()
        self.macro_system = MacroSystem()
        
        # Initialize interactive trainer
        self.interactive_trainer = InteractiveTrainer(
            enhanced_vision=self.vision_system,
            automation_engine=self.automation_engine
        )
        
        # Initialize autonomous learning system
        self.autonomous_learning = AutonomousLearningSystem()
        self.autonomous_learning.start_autonomous_learning()
        self.command_processor = CommandProcessor(
            vision=self.vision_system,
            automation=self.automation_engine,
            learning=self.learning_system,
            knowledge=self.knowledge_manager,
            macro=self.macro_system
        )
        
        self.logger.info("🤖 GameBot initialized with autonomous self-learning capabilities")
    
    def start_interactive_mode(self):
        """Start interactive command-line interface"""
        self.logger.info("Starting interactive mode...")
        print("AI Game Bot - Interactive Mode")
        print("Type 'help' for available commands or 'quit' to exit")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input:
                    result = self.command_processor.process_command(user_input)
                    if result:
                        print(f"Result: {result}")
                        
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")
    
    def show_help(self):
        """Display available commands"""
        help_text = """
Available Commands:
  Game Actions:
    open chests              - Find and open treasure chests
    hatch eggs              - Find and hatch eggs
    stay in breakables      - Move to and stay in breakables area
    farm [item]             - Farm specific items or resources
    
  Learning & Knowledge:
    learn from [file/url]   - Learn from file or website
    update knowledge        - Update knowledge base from developer blogs
    analyze screen          - Analyze current screen state
    
  Macro System:
    record macro [name]     - Start recording a macro
    stop recording          - Stop macro recording
    play macro [name]       - Play recorded macro
    list macros            - List available macros
    
  System:
    status                  - Show system status
    config                  - Show configuration
    help                   - Show this help message
    quit/exit/q            - Exit the program
        """
        print(help_text)
    
    def process_single_command(self, command):
        """Process a single command (useful for web interface)"""
        try:
            return self.command_processor.process_command(command)
        except Exception as e:
            self.logger.error(f"Error processing command '{command}': {e}")
            return f"Error: {e}"

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Game Automation Bot')
    parser.add_argument('--web', action='store_true', help='Start web interface')
    parser.add_argument('--port', type=int, default=5000, help='Web interface port')
    parser.add_argument('--command', type=str, help='Execute single command')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create bot instance
    bot = GameBot()
    
    if args.command:
        # Execute single command
        result = bot.process_single_command(args.command)
        print(result)
    elif args.web:
        # Start web interface
        from app import create_app
        app = create_app(bot)
        app.run(host='0.0.0.0', port=args.port, debug=args.debug)
    else:
        # Start interactive mode
        bot.start_interactive_mode()

if __name__ == '__main__':
    main()
