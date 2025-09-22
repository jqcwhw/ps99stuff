"""
Automation Engine for Game Control
Handles mouse and keyboard automation for game interactions
"""

import time
import logging
from typing import Tuple, List, Optional, Dict, Any
import threading
import queue
import json
from pathlib import Path
import random

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None

class AutomationEngine:
    """Main automation engine for game control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_active = False
        self.action_queue = queue.Queue()
        self.worker_thread = None
        
        # Configure PyAutoGUI
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.1  # Small pause between actions
        
        # Movement settings
        self.move_duration = 0.3
        self.click_duration = 0.1
        self.human_like_movement = True
        
        # Safety settings
        self.safe_regions = []  # Regions where clicks are safe
        self.forbidden_regions = []  # Regions to avoid
        
        self.logger.info("Automation engine initialized")
    
    def start(self):
        """Start the automation engine"""
        if self.worker_thread and self.worker_thread.is_alive():
            return
        
        self._is_active = True
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        self.logger.info("Automation engine started")
    
    def stop(self):
        """Stop the automation engine"""
        self._is_active = False
        
        # Clear pending actions
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except queue.Empty:
                break
        
        # Wait for worker thread to finish
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        
        self.logger.info("Automation engine stopped")
    
    def _worker_loop(self):
        """Main worker loop for processing automation actions"""
        while self._is_active:
            try:
                # Get next action from queue (timeout to allow periodic checks)
                action = self.action_queue.get(timeout=1.0)
                
                # Process the action
                self._execute_action(action)
                
                # Mark task as done
                self.action_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Action execution failed: {e}")
    
    def _execute_action(self, action: Dict[str, Any]):
        """Execute a single automation action"""
        try:
            action_type = action.get('type')
            
            if action_type == 'click':
                self._execute_click(action)
            elif action_type == 'move':
                self._execute_move(action)
            elif action_type == 'drag':
                self._execute_drag(action)
            elif action_type == 'key':
                self._execute_key(action)
            elif action_type == 'scroll':
                self._execute_scroll(action)
            elif action_type == 'wait':
                self._execute_wait(action)
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to execute action {action}: {e}")
    
    def _execute_click(self, action: Dict[str, Any]):
        """Execute a click action"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        button = action.get('button', 'left')
        clicks = action.get('clicks', 1)
        
        if not self._is_safe_position(x, y):
            self.logger.warning(f"Unsafe click position: ({x}, {y})")
            return
        
        # Add human-like randomness
        if self.human_like_movement:
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
        
        # Move to position first
        self._move_to_position(x, y)
        
        # Perform click
        if PYAUTOGUI_AVAILABLE:
            pyautogui.click(x, y, clicks=clicks, button=button, duration=self.click_duration)
        else:
            self.logger.info(f"Demo mode: Would click at ({x}, {y})")
        
        self.logger.debug(f"Clicked at ({x}, {y}) with {button} button")
    
    def _execute_move(self, action: Dict[str, Any]):
        """Execute a move action"""
        x = action.get('x', 0)
        y = action.get('y', 0)
        
        if PYAUTOGUI_AVAILABLE:
            self._move_to_position(x, y)
        self.logger.debug(f"Moved to ({x}, {y})")
    
    def _execute_drag(self, action: Dict[str, Any]):
        """Execute a drag action"""
        from_x = action.get('from_x', 0)
        from_y = action.get('from_y', 0)
        to_x = action.get('to_x', 0)
        to_y = action.get('to_y', 0)
        button = action.get('button', 'left')
        
        if not (self._is_safe_position(from_x, from_y) and self._is_safe_position(to_x, to_y)):
            self.logger.warning(f"Unsafe drag positions: ({from_x}, {from_y}) to ({to_x}, {to_y})")
            return
        
        if PYAUTOGUI_AVAILABLE:
            pyautogui.drag(to_x - from_x, to_y - from_y, 
                          duration=self.move_duration, button=button)
        else:
            self.logger.info(f"Demo mode: Would drag from ({from_x}, {from_y}) to ({to_x}, {to_y})")
        
        self.logger.debug(f"Dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})")
    
    def _execute_key(self, action: Dict[str, Any]):
        """Execute a keyboard action"""
        key = action.get('key', '')
        action_type = action.get('action', 'press')  # press, hold, release
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.info(f"Demo mode: Would press key {key}")
            return
            
        if action_type == 'press':
            pyautogui.press(key)
        elif action_type == 'hold':
            pyautogui.keyDown(key)
        elif action_type == 'release':
            pyautogui.keyUp(key)
        
        self.logger.debug(f"Key action: {action_type} {key}")
    
    def _execute_scroll(self, action: Dict[str, Any]):
        """Execute a scroll action"""
        x = action.get('x', None)
        y = action.get('y', None)
        scrolls = action.get('scrolls', 1)
        
        if not PYAUTOGUI_AVAILABLE:
            self.logger.info(f"Demo mode: Would scroll {scrolls}")
            return
            
        if x is not None and y is not None:
            pyautogui.scroll(scrolls, x=x, y=y)
        else:
            pyautogui.scroll(scrolls)
        
        self.logger.debug(f"Scrolled {scrolls} at ({x}, {y})")
    
    def _execute_wait(self, action: Dict[str, Any]):
        """Execute a wait action"""
        duration = action.get('duration', 1.0)
        time.sleep(duration)
        self.logger.debug(f"Waited {duration} seconds")
    
    def _move_to_position(self, x: int, y: int):
        """Move mouse to position with human-like movement"""
        if not PYAUTOGUI_AVAILABLE:
            return
            
        if self.human_like_movement:
            # Add slight curve to movement
            current_x, current_y = pyautogui.position()
            mid_x = (current_x + x) // 2 + random.randint(-10, 10)
            mid_y = (current_y + y) // 2 + random.randint(-10, 10)
            
            # Move in two steps for more natural movement
            pyautogui.moveTo(mid_x, mid_y, duration=self.move_duration / 2)
            pyautogui.moveTo(x, y, duration=self.move_duration / 2)
        else:
            pyautogui.moveTo(x, y, duration=self.move_duration)
    
    def _is_safe_position(self, x: int, y: int) -> bool:
        """Check if position is safe for automation"""
        # Check forbidden regions
        for region in self.forbidden_regions:
            if (region['x'] <= x <= region['x'] + region['width'] and
                region['y'] <= y <= region['y'] + region['height']):
                return False
        
        # If safe regions are defined, position must be in one of them
        if self.safe_regions:
            for region in self.safe_regions:
                if (region['x'] <= x <= region['x'] + region['width'] and
                    region['y'] <= y <= region['y'] + region['height']):
                    return True
            return False
        
        # No restrictions if no safe regions defined
        return True
    
    def queue_click(self, x: int, y: int, button: str = 'left', clicks: int = 1):
        """Queue a click action"""
        action = {
            'type': 'click',
            'x': x,
            'y': y,
            'button': button,
            'clicks': clicks
        }
        self.action_queue.put(action)
    
    def queue_move(self, x: int, y: int):
        """Queue a move action"""
        action = {
            'type': 'move',
            'x': x,
            'y': y
        }
        self.action_queue.put(action)
    
    def queue_drag(self, from_x: int, from_y: int, to_x: int, to_y: int, button: str = 'left'):
        """Queue a drag action"""
        action = {
            'type': 'drag',
            'from_x': from_x,
            'from_y': from_y,
            'to_x': to_x,
            'to_y': to_y,
            'button': button
        }
        self.action_queue.put(action)
    
    def queue_key(self, key: str, action_type: str = 'press'):
        """Queue a keyboard action"""
        action = {
            'type': 'key',
            'key': key,
            'action': action_type
        }
        self.action_queue.put(action)
    
    def queue_wait(self, duration: float):
        """Queue a wait action"""
        action = {
            'type': 'wait',
            'duration': duration
        }
        self.action_queue.put(action)
    
    def click_at_positions(self, positions: List[Tuple[int, int]], delay: float = 0.5):
        """Click at multiple positions with delay between clicks"""
        for i, (x, y) in enumerate(positions):
            self.queue_click(x, y)
            
            # Add delay between clicks (except after the last one)
            if i < len(positions) - 1:
                self.queue_wait(delay)
    
    def open_chests(self, chest_positions: List[Tuple[int, int]]) -> str:
        """Automate opening chests at given positions"""
        if not chest_positions:
            return "No chests found to open"
        
        self.logger.info(f"Opening {len(chest_positions)} chests")
        
        for i, position in enumerate(chest_positions):
            x, y = position[:2]
            confidence = getattr(position, '__getitem__', lambda i: 1.0)(2) if len(position) > 2 else 1.0
            self.logger.debug(f"Opening chest {i+1} at ({x}, {y}) with confidence {confidence}")
            
            # Move to chest position
            self.queue_move(x, y)
            self.queue_wait(0.2)
            
            # Double-click to open chest
            self.queue_click(x, y, clicks=2)
            self.queue_wait(0.8)  # Wait for chest animation
        
        return f"Queued actions to open {len(chest_positions)} chests"
    
    def hatch_eggs(self, egg_positions: List[Tuple[int, int]]) -> str:
        """Automate hatching eggs at given positions"""
        if not egg_positions:
            return "No eggs found to hatch"
        
        self.logger.info(f"Hatching {len(egg_positions)} eggs")
        
        for i, position in enumerate(egg_positions):
            x, y = position[:2]
            confidence = getattr(position, '__getitem__', lambda i: 1.0)(2) if len(position) > 2 else 1.0
            self.logger.debug(f"Hatching egg {i+1} at ({x}, {y}) with confidence {confidence}")
            
            # Move to egg position
            self.queue_move(x, y)
            self.queue_wait(0.2)
            
            # Click to select egg
            self.queue_click(x, y)
            self.queue_wait(0.5)
            
            # Press hatch key (assuming 'h' key hatches eggs)
            self.queue_key('h')
            self.queue_wait(1.0)  # Wait for hatching animation
        
        return f"Queued actions to hatch {len(egg_positions)} eggs"
    
    def move_to_area(self, target_position: Tuple[int, int]) -> str:
        """Move character to specific area"""
        if not target_position:
            return "No target position specified"
        
        x, y = target_position[:2]  # Handle confidence tuple
        
        self.logger.info(f"Moving to area at ({x}, {y})")
        
        # Move to target area
        self.queue_move(x, y)
        self.queue_click(x, y)  # Click to move character
        
        return f"Moving to area at ({x}, {y})"
    
    def stay_in_breakables_area(self, breakables_positions: List[Tuple[int, int]]) -> str:
        """Keep character in breakables area"""
        if not breakables_positions:
            return "No breakables area found"
        
        # Find center of breakables area
        if len(breakables_positions) == 1:
            center_x, center_y = breakables_positions[0][:2]
        else:
            # Calculate center of all breakables
            x_coords = [pos[0] for pos in breakables_positions]
            y_coords = [pos[1] for pos in breakables_positions]
            center_x = sum(x_coords) // len(x_coords)
            center_y = sum(y_coords) // len(y_coords)
        
        # Move to center of breakables area
        result = self.move_to_area((center_x, center_y))
        
        self.logger.info(f"Staying in breakables area at ({center_x}, {center_y})")
        return f"Moving to breakables area. {result}"
    
    def emergency_stop(self):
        """Emergency stop all automation"""
        self.logger.warning("Emergency stop activated")
        self.stop()
        
        # Move mouse to safe position (corner of screen)
        try:
            if PYAUTOGUI_AVAILABLE:
                pyautogui.moveTo(0, 0, duration=0.5)
        except:
            pass
    
    def get_queue_size(self) -> int:
        """Get current action queue size"""
        return self.action_queue.qsize()
    
    def clear_queue(self):
        """Clear all pending actions"""
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("Action queue cleared")
    
    def is_active(self) -> bool:
        """Check if automation engine is active"""
        return self._is_active and (self.worker_thread is not None and self.worker_thread.is_alive())
    
    def set_safe_region(self, x: int, y: int, width: int, height: int):
        """Set a safe region for automation"""
        region = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.safe_regions.append(region)
        self.logger.info(f"Added safe region: {region}")
    
    def set_forbidden_region(self, x: int, y: int, width: int, height: int):
        """Set a forbidden region for automation"""
        region = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.forbidden_regions.append(region)
        self.logger.info(f"Added forbidden region: {region}")
    
    def clear_regions(self):
        """Clear all safe and forbidden regions"""
        self.safe_regions.clear()
        self.forbidden_regions.clear()
        self.logger.info("Cleared all regions")
