"""
Flask Web Application for AI Game Bot
Provides a web interface for monitoring and controlling the game bot
"""

import json
import logging
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime
import base64
import io

def create_app(game_bot):
    """Create Flask application with game bot instance"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'game_bot_secret_key_2024'
    
    # Store bot reference in app config to avoid type issues
    app.config['GAME_BOT'] = game_bot
    
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('index.html')
    
    @app.route('/api/status')
    def get_status():
        """Get current bot status"""
        try:
            # Get screen capture
            game_bot = app.config['GAME_BOT']
            screen_data = game_bot.vision_system.capture_screen()
            screen_b64 = None
            
            if screen_data is not None:
                # Convert to base64 for web display
                import cv2
                import numpy as np
                
                # Resize for web display
                height, width = screen_data.shape[:2]
                if width > 800:
                    scale = 800 / width
                    new_width = 800
                    new_height = int(height * scale)
                    screen_data = cv2.resize(screen_data, (new_width, new_height))
                
                # Convert to base64
                _, buffer = cv2.imencode('.jpg', screen_data)
                screen_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # Get system status
            status = {
                'timestamp': datetime.now().isoformat(),
                'vision_active': game_bot.vision_system.is_active(),
                'automation_active': game_bot.automation_engine.is_active(),
                'learning_stats': game_bot.learning_system.get_stats(),
                'knowledge_count': game_bot.knowledge_manager.get_knowledge_count(),
                'macro_count': len(game_bot.macro_system.list_macros()),
                'screen_capture': screen_b64,
                'last_command': getattr(game_bot.command_processor, 'last_command', 'None'),
                'last_result': getattr(game_bot.command_processor, 'last_result', 'None')
            }
            
            return jsonify(status)
        except Exception as e:
            app.logger.error(f"Error getting status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/command', methods=['POST'])
    def execute_command():
        """Execute a command"""
        try:
            data = request.get_json()
            command = data.get('command', '').strip()
            
            if not command:
                return jsonify({'error': 'No command provided'}), 400
            
            # Execute command
            game_bot = app.config['GAME_BOT']
            result = game_bot.process_single_command(command)
            
            return jsonify({
                'command': command,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error executing command: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/macros')
    def get_macros():
        """Get list of available macros"""
        try:
            game_bot = app.config['GAME_BOT']
            macros = game_bot.macro_system.list_macros()
            return jsonify({'macros': macros})
        except Exception as e:
            app.logger.error(f"Error getting macros: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/knowledge')
    def get_knowledge():
        """Get knowledge base summary"""
        try:
            game_bot = app.config['GAME_BOT']
            knowledge = game_bot.knowledge_manager.get_knowledge_summary()
            return jsonify(knowledge)
        except Exception as e:
            app.logger.error(f"Error getting knowledge: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/learn', methods=['POST'])
    def learn_from_source():
        """Learn from file or URL"""
        try:
            data = request.get_json()
            source = data.get('source', '').strip()
            source_type = data.get('type', 'auto')  # auto, file, url
            
            if not source:
                return jsonify({'error': 'No source provided'}), 400
            
            # Process learning request
            game_bot = app.config['GAME_BOT']
            if source_type == 'url' or (source_type == 'auto' and source.startswith('http')):
                result = game_bot.knowledge_manager.learn_from_url(source)
            else:
                result = game_bot.knowledge_manager.learn_from_file(source)
            
            return jsonify({
                'source': source,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error learning from source: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logs')
    def get_logs():
        """Get recent logs"""
        try:
            # Get recent log entries - placeholder for now
            logs = ["System logs available through file handlers"]
            
            return jsonify({'logs': logs})
        except Exception as e:
            app.logger.error(f"Error getting logs: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Interactive Training API Endpoints
    @app.route('/api/training/start', methods=['POST'])
    def start_training():
        """Start interactive training mode"""
        try:
            data = request.get_json()
            mode = data.get('mode', 'item_learning')
            
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.start_interactive_training(mode)
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error starting training: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/stop', methods=['POST'])
    def stop_training():
        """Stop interactive training mode"""
        try:
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.stop_interactive_training()
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error stopping training: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/spacebar', methods=['POST'])
    def process_spacebar():
        """Process spacebar input for item learning"""
        try:
            data = request.get_json()
            item_type = data.get('item_type')
            
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.process_spacebar_input(item_type)
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error processing spacebar: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/corner', methods=['POST'])
    def process_corner():
        """Process corner click for zone creation"""
        try:
            data = request.get_json()
            x = data.get('x')
            y = data.get('y')
            
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.process_corner_click(x, y)
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error processing corner: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/command', methods=['POST'])
    def process_natural_command():
        """Process natural language training command"""
        try:
            data = request.get_json()
            command = data.get('command', '')
            
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.process_natural_language_command(command)
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error processing command: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/status')
    def get_training_status():
        """Get current training status"""
        try:
            game_bot = app.config['GAME_BOT']
            status = game_bot.interactive_trainer.get_training_status()
            
            return jsonify(status)
        except Exception as e:
            app.logger.error(f"Error getting training status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/training/zone/set', methods=['POST'])
    def set_zone_type():
        """Set zone type and restrictions"""
        try:
            data = request.get_json()
            zone_id = data.get('zone_id')
            zone_type = data.get('zone_type')
            restrictions = data.get('restrictions', [])
            
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer.set_zone_type(zone_id, zone_type, restrictions)
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error setting zone type: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/similarities')
    def analyze_similarities():
        """Analyze similarities between learned items"""
        try:
            game_bot = app.config['GAME_BOT']
            result = game_bot.interactive_trainer._analyze_item_similarities()
            
            return jsonify({'result': result, 'success': True})
        except Exception as e:
            app.logger.error(f"Error analyzing similarities: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/find-items')
    def find_similar_items():
        """Find similar items in current screen"""
        try:
            threshold = float(request.args.get('threshold', 0.8))
            
            game_bot = app.config['GAME_BOT']
            matches = game_bot.interactive_trainer.find_similar_items_in_screen(threshold)
            
            return jsonify({'matches': matches, 'success': True})
        except Exception as e:
            app.logger.error(f"Error finding items: {e}")
            return jsonify({'error': str(e), 'success': False}), 500
    
    @app.route('/api/training/export')
    def export_training_data():
        """Export all training data"""
        try:
            game_bot = app.config['GAME_BOT']
            data = game_bot.interactive_trainer.export_training_data()
            
            return jsonify(data)
        except Exception as e:
            app.logger.error(f"Error exporting data: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app
