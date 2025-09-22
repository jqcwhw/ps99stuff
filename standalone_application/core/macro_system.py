"""
Macro System for AI Game Bot
Handles recording, storing, and playback of automation macros
"""

import json
import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from collections import deque

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

class MacroSystem:
    """System for recording and playing automation macros"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.macros_file = Path("data/macros.json")
        
        # Macro storage
        self.macros = {}
        self.is_recording = False
        self.current_recording = None
        self.recording_thread = None
        
        # Recording settings
        self.recording_interval = 0.1  # Record every 100ms
        self.max_recording_duration = 300  # 5 minutes max
        self.action_threshold = 5  # Minimum pixels for movement to count
        
        # Playback settings
        self.playback_speed = 1.0
        self.is_playing = False
        self.playback_thread = None
        
        # Load existing macros
        self._load_macros()
        
        self.logger.info("Macro system initialized")
    
    def _load_macros(self):
        """Load macros from storage"""
        try:
            if self.macros_file.exists():
                with open(self.macros_file, 'r') as f:
                    self.macros = json.load(f)
                self.logger.info(f"Loaded {len(self.macros)} macros")
        except Exception as e:
            self.logger.error(f"Failed to load macros: {e}")
            self.macros = {}
    
    def _save_macros(self):
        """Save macros to storage"""
        try:
            self.macros_file.parent.mkdir(exist_ok=True)
            with open(self.macros_file, 'w') as f:
                json.dump(self.macros, f, indent=2)
            self.logger.debug("Macros saved")
        except Exception as e:
            self.logger.error(f"Failed to save macros: {e}")
    
    def start_recording(self, macro_name: str, description: str = "") -> str:
        """
        Start recording a new macro
        
        Args:
            macro_name: Name for the macro
            description: Optional description
            
        Returns:
            Result message
        """
        try:
            if self.is_recording:
                return "Already recording a macro. Stop current recording first."
            
            if macro_name in self.macros:
                return f"Macro '{macro_name}' already exists. Choose a different name."
            
            # Initialize recording
            self.is_recording = True
            self.current_recording = {
                'name': macro_name,
                'description': description,
                'actions': [],
                'start_time': time.time(),
                'last_mouse_pos': (0, 0) if not PYAUTOGUI_AVAILABLE else pyautogui.position(),
                'last_action_time': time.time()
            }
            
            # Start recording thread
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            result = f"Started recording macro '{macro_name}'"
            self.logger.info(result)
            return result
            
        except Exception as e:
            self.is_recording = False
            error_msg = f"Failed to start recording: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def stop_recording(self) -> str:
        """
        Stop current recording and save the macro
        
        Returns:
            Result message
        """
        try:
            if not self.is_recording:
                return "No recording in progress"
            
            # Stop recording
            self.is_recording = False
            
            if self.recording_thread:
                self.recording_thread.join(timeout=2.0)
            
            if not self.current_recording:
                return "No recording data available"
            
            # Finalize macro
            macro_name = self.current_recording['name']
            total_duration = time.time() - self.current_recording['start_time']
            
            macro_data = {
                'name': macro_name,
                'description': self.current_recording['description'],
                'actions': self.current_recording['actions'],
                'duration': total_duration,
                'created_at': time.time(),
                'action_count': len(self.current_recording['actions'])
            }
            
            # Save macro
            self.macros[macro_name] = macro_data
            self._save_macros()
            
            result = f"Stopped recording. Saved macro '{macro_name}' with {len(self.current_recording['actions'])} actions"
            self.logger.info(result)
            
            self.current_recording = None
            return result
            
        except Exception as e:
            self.is_recording = False
            error_msg = f"Failed to stop recording: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _recording_loop(self):
        """Main recording loop"""
        try:
            while self.is_recording and self.current_recording is not None:
                current_time = time.time()
                
                # Check for max duration
                if current_time - self.current_recording['start_time'] > self.max_recording_duration:
                    self.logger.warning("Recording stopped: maximum duration reached")
                    break
                
                # Record mouse position
                if not PYAUTOGUI_AVAILABLE:
                    current_mouse_pos = (0, 0)  # Dummy position
                else:
                    current_mouse_pos = pyautogui.position()
                last_mouse_pos = self.current_recording['last_mouse_pos']
                
                # Check if mouse moved significantly
                if abs(current_mouse_pos[0] - last_mouse_pos[0]) > self.action_threshold or \
                   abs(current_mouse_pos[1] - last_mouse_pos[1]) > self.action_threshold:
                    
                    action = {
                        'type': 'mouse_move',
                        'x': current_mouse_pos[0],
                        'y': current_mouse_pos[1],
                        'timestamp': current_time,
                        'delay': current_time - self.current_recording['last_action_time']
                    }
                    
                    self.current_recording['actions'].append(action)
                    self.current_recording['last_mouse_pos'] = current_mouse_pos
                    self.current_recording['last_action_time'] = current_time
                
                time.sleep(self.recording_interval)
                
        except Exception as e:
            self.logger.error(f"Recording loop error: {e}")
            self.is_recording = False
    
    def play_macro(self, macro_name: str, speed: float = 1.0) -> str:
        """
        Play a recorded macro
        
        Args:
            macro_name: Name of macro to play
            speed: Playback speed multiplier (1.0 = normal speed)
            
        Returns:
            Result message
        """
        try:
            if self.is_playing:
                return "Already playing a macro. Wait for completion."
            
            if macro_name not in self.macros:
                return f"Macro '{macro_name}' not found"
            
            if self.is_recording:
                return "Cannot play macro while recording"
            
            # Start playback
            self.is_playing = True
            self.playback_speed = speed
            
            macro_data = self.macros[macro_name]
            self.playback_thread = threading.Thread(
                target=self._playback_loop, 
                args=(macro_data,)
            )
            self.playback_thread.daemon = True
            self.playback_thread.start()
            
            result = f"Started playing macro '{macro_name}' at {speed}x speed"
            self.logger.info(result)
            return result
            
        except Exception as e:
            self.is_playing = False
            error_msg = f"Failed to play macro: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _playback_loop(self, macro_data: Dict[str, Any]):
        """Main playback loop"""
        try:
            actions = macro_data['actions']
            self.logger.info(f"Playing macro with {len(actions)} actions")
            
            for i, action in enumerate(actions):
                if not self.is_playing:
                    break
                
                # Apply speed adjustment to delay
                delay = action.get('delay', 0) / self.playback_speed
                if delay > 0:
                    time.sleep(min(delay, 5.0))  # Cap delay at 5 seconds
                
                # Execute action
                self._execute_macro_action(action)
                
                self.logger.debug(f"Executed action {i+1}/{len(actions)}: {action['type']}")
            
            self.is_playing = False
            self.logger.info("Macro playback completed")
            
        except Exception as e:
            self.is_playing = False
            self.logger.error(f"Macro playback error: {e}")
    
    def _execute_macro_action(self, action: Dict[str, Any]):
        """Execute a single macro action"""
        try:
            action_type = action['type']
            
            if not PYAUTOGUI_AVAILABLE:
                self.logger.info(f"Demo mode: Would execute {action_type}")
                return
                
            if action_type == 'mouse_move':
                pyautogui.moveTo(action['x'], action['y'], duration=0.1)
            
            elif action_type == 'mouse_click':
                pyautogui.click(
                    action['x'], 
                    action['y'], 
                    button=action.get('button', 'left'),
                    clicks=action.get('clicks', 1)
                )
            
            elif action_type == 'mouse_drag':
                pyautogui.drag(
                    action['end_x'] - action['start_x'],
                    action['end_y'] - action['start_y'],
                    duration=action.get('duration', 0.5),
                    button=action.get('button', 'left')
                )
            
            elif action_type == 'key_press':
                if action.get('key'):
                    pyautogui.press(action['key'])
            
            elif action_type == 'key_combination':
                keys = action.get('keys', [])
                if keys:
                    pyautogui.hotkey(*keys)
            
            elif action_type == 'scroll':
                pyautogui.scroll(
                    action.get('clicks', 1),
                    x=action.get('x'),
                    y=action.get('y')
                )
            
            elif action_type == 'wait':
                time.sleep(action.get('duration', 1.0))
                
        except Exception as e:
            self.logger.error(f"Failed to execute macro action {action}: {e}")
    
    def stop_playback(self) -> str:
        """Stop current macro playback"""
        try:
            if not self.is_playing:
                return "No macro currently playing"
            
            self.is_playing = False
            
            if self.playback_thread:
                self.playback_thread.join(timeout=2.0)
            
            result = "Macro playback stopped"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to stop playback: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def list_macros(self) -> List[str]:
        """Get list of available macro names"""
        return list(self.macros.keys())
    
    def get_macro_info(self, macro_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific macro"""
        if macro_name not in self.macros:
            return None
        
        macro = self.macros[macro_name]
        return {
            'name': macro['name'],
            'description': macro.get('description', ''),
            'duration': macro.get('duration', 0),
            'action_count': macro.get('action_count', 0),
            'created_at': macro.get('created_at', 0)
        }
    
    def delete_macro(self, macro_name: str) -> str:
        """Delete a macro"""
        try:
            if macro_name not in self.macros:
                return f"Macro '{macro_name}' not found"
            
            del self.macros[macro_name]
            self._save_macros()
            
            result = f"Deleted macro '{macro_name}'"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to delete macro: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def create_macro_from_actions(self, macro_name: str, actions: List[Dict[str, Any]], 
                                 description: str = "") -> str:
        """
        Create a macro from a list of actions
        
        Args:
            macro_name: Name for the macro
            actions: List of action dictionaries
            description: Optional description
            
        Returns:
            Result message
        """
        try:
            if macro_name in self.macros:
                return f"Macro '{macro_name}' already exists"
            
            # Calculate total duration
            total_duration = sum(action.get('delay', 0) for action in actions)
            
            macro_data = {
                'name': macro_name,
                'description': description,
                'actions': actions,
                'duration': total_duration,
                'created_at': time.time(),
                'action_count': len(actions)
            }
            
            self.macros[macro_name] = macro_data
            self._save_macros()
            
            result = f"Created macro '{macro_name}' with {len(actions)} actions"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to create macro: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def export_macro(self, macro_name: str, file_path: str) -> str:
        """Export a macro to file"""
        try:
            if macro_name not in self.macros:
                return f"Macro '{macro_name}' not found"
            
            macro_data = self.macros[macro_name]
            
            with open(file_path, 'w') as f:
                json.dump(macro_data, f, indent=2)
            
            result = f"Exported macro '{macro_name}' to {file_path}"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to export macro: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def import_macro(self, file_path: str) -> str:
        """Import a macro from file"""
        try:
            with open(file_path, 'r') as f:
                macro_data = json.load(f)
            
            macro_name = macro_data['name']
            
            if macro_name in self.macros:
                return f"Macro '{macro_name}' already exists"
            
            self.macros[macro_name] = macro_data
            self._save_macros()
            
            result = f"Imported macro '{macro_name}' from {file_path}"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to import macro: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def is_recording_active(self) -> bool:
        """Check if currently recording"""
        return self.is_recording
    
    def is_playback_active(self) -> bool:
        """Check if currently playing back"""
        return self.is_playing
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of macro system"""
        return {
            'total_macros': len(self.macros),
            'is_recording': self.is_recording,
            'is_playing': self.is_playing,
            'current_recording': self.current_recording['name'] if self.current_recording else None,
            'recording_duration': time.time() - self.current_recording['start_time'] if self.current_recording else 0
        }
