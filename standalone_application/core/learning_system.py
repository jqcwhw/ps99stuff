"""
Learning System for AI Game Bot
Handles pattern recognition, adaptation, and improvement through experience
"""

import json
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import pickle
from collections import defaultdict, deque

class LearningSystem:
    """AI learning system for game automation improvement"""
    
    def __init__(self, max_memory_size: int = 1000):
        self.logger = logging.getLogger(__name__)
        
        # Learning data storage
        self.experience_memory = deque(maxlen=max_memory_size)
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.action_outcomes = defaultdict(lambda: {'success': 0, 'failure': 0})
        
        # Learning statistics
        self.stats = {
            'total_experiences': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'patterns_learned': 0,
            'adaptations_made': 0,
            'items_learned': 0
        }
        
        # Pattern recognition settings
        self.similarity_threshold = 0.8
        self.min_pattern_occurrences = 3
        
        # Load existing learning data
        self._load_learning_data()
        
        self.logger.info("Learning system initialized")
    
    def _load_learning_data(self):
        """Load existing learning data from storage"""
        try:
            learning_file = Path("data/learning_data.pkl")
            if learning_file.exists():
                with open(learning_file, 'rb') as f:
                    data = pickle.load(f)
                    
                self.success_patterns = data.get('success_patterns', defaultdict(list))
                self.failure_patterns = data.get('failure_patterns', defaultdict(list))
                self.action_outcomes = data.get('action_outcomes', defaultdict(lambda: {'success': 0, 'failure': 0}))
                self.stats = data.get('stats', self.stats)
                
                self.logger.info(f"Loaded learning data: {self.stats['total_experiences']} experiences")
        except Exception as e:
            self.logger.error(f"Failed to load learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to storage"""
        try:
            learning_file = Path("data/learning_data.pkl")
            learning_file.parent.mkdir(exist_ok=True)
            
            data = {
                'success_patterns': dict(self.success_patterns),
                'failure_patterns': dict(self.failure_patterns),
                'action_outcomes': dict(self.action_outcomes),
                'stats': self.stats
            }
            
            with open(learning_file, 'wb') as f:
                pickle.dump(data, f)
                
            self.logger.debug("Learning data saved")
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
    
    def record_experience(self, action: str, context: Dict[str, Any], outcome: str, 
                         details: Optional[Dict[str, Any]] = None):
        """
        Record an experience for learning
        
        Args:
            action: The action that was performed
            context: Context information (screen state, positions, etc.)
            outcome: 'success' or 'failure'
            details: Additional details about the experience
        """
        experience = {
            'timestamp': time.time(),
            'action': action,
            'context': context,
            'outcome': outcome,
            'details': details or {}
        }
        
        # Add to memory
        self.experience_memory.append(experience)
        
        # Update statistics
        self.stats['total_experiences'] += 1
        if outcome == 'success':
            self.stats['successful_actions'] += 1
            self.success_patterns[action].append(experience)
        else:
            self.stats['failed_actions'] += 1
            self.failure_patterns[action].append(experience)
        
        # Update action outcomes
        self.action_outcomes[action][outcome] += 1
        
        # Look for patterns
        self._analyze_patterns(action, experience)
        
        # Save periodically
        if self.stats['total_experiences'] % 10 == 0:
            self._save_learning_data()
        
        self.logger.debug(f"Recorded experience: {action} -> {outcome}")
    
    def _analyze_patterns(self, action: str, experience: Dict[str, Any]):
        """Analyze experiences to identify patterns"""
        try:
            # Look for similar successful experiences
            if experience['outcome'] == 'success':
                similar_successes = self._find_similar_experiences(experience, self.success_patterns[action])
                if len(similar_successes) >= self.min_pattern_occurrences:
                    pattern = self._extract_pattern(similar_successes)
                    if pattern:
                        self._learn_pattern(action, pattern, 'success')
            
            # Look for similar failure experiences
            else:
                similar_failures = self._find_similar_experiences(experience, self.failure_patterns[action])
                if len(similar_failures) >= self.min_pattern_occurrences:
                    pattern = self._extract_pattern(similar_failures)
                    if pattern:
                        self._learn_pattern(action, pattern, 'failure')
                        
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
    
    def _find_similar_experiences(self, target_experience: Dict[str, Any], 
                                 experience_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find experiences similar to the target experience"""
        similar = []
        
        target_context = target_experience.get('context', {})
        
        for exp in experience_list:
            exp_context = exp.get('context', {})
            
            # Calculate similarity based on context
            similarity = self._calculate_context_similarity(target_context, exp_context)
            
            if similarity >= self.similarity_threshold:
                similar.append(exp)
        
        return similar
    
    def _calculate_context_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts"""
        try:
            # Simple similarity based on shared keys and value differences
            common_keys = set(context1.keys()) & set(context2.keys())
            if not common_keys:
                return 0.0
            
            total_similarity = 0.0
            compared_keys = 0
            
            for key in common_keys:
                val1, val2 = context1[key], context2[key]
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Numerical similarity
                    max_val = max(abs(val1), abs(val2), 1)  # Prevent division by zero
                    similarity = 1.0 - min(abs(val1 - val2) / max_val, 1.0)
                    total_similarity += similarity
                    compared_keys += 1
                elif isinstance(val1, str) and isinstance(val2, str):
                    # String similarity (exact match for now)
                    similarity = 1.0 if val1 == val2 else 0.0
                    total_similarity += similarity
                    compared_keys += 1
                elif isinstance(val1, list) and isinstance(val2, list):
                    # List similarity (length and content)
                    len_similarity = 1.0 - min(abs(len(val1) - len(val2)) / max(len(val1), len(val2), 1), 1.0)
                    total_similarity += len_similarity
                    compared_keys += 1
            
            return total_similarity / compared_keys if compared_keys > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def _extract_pattern(self, experiences: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract common pattern from similar experiences"""
        try:
            if not experiences:
                return None
            
            # Extract common context elements
            pattern = {
                'occurrences': len(experiences),
                'common_context': {},
                'context_ranges': {},
                'success_rate': 1.0 if all(exp['outcome'] == 'success' for exp in experiences) else 0.0
            }
            
            # Find common context keys
            all_contexts = [exp.get('context', {}) for exp in experiences]
            common_keys = set.intersection(*[set(ctx.keys()) for ctx in all_contexts])
            
            for key in common_keys:
                values = [ctx[key] for ctx in all_contexts]
                
                if all(isinstance(v, (int, float)) for v in values):
                    # Numerical range
                    pattern['context_ranges'][key] = {
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values)
                    }
                elif all(isinstance(v, str) for v in values):
                    # Most common string value
                    value_counts = defaultdict(int)
                    for v in values:
                        value_counts[v] += 1
                    most_common = max(value_counts.items(), key=lambda x: x[1])
                    if most_common[1] / len(values) >= 0.5:  # At least 50% occurrence
                        pattern['common_context'][key] = most_common[0]
            
            return pattern if pattern['common_context'] or pattern['context_ranges'] else None
            
        except Exception as e:
            self.logger.error(f"Pattern extraction failed: {e}")
            return None
    
    def _learn_pattern(self, action: str, pattern: Dict[str, Any], outcome_type: str):
        """Learn a new pattern"""
        pattern_key = f"{action}_{outcome_type}"
        
        # Store the pattern (simplified storage for now)
        pattern_file = Path(f"data/patterns/{pattern_key}.json")
        pattern_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(pattern_file, 'w') as f:
                json.dump(pattern, f, indent=2)
            
            self.stats['patterns_learned'] += 1
            self.logger.info(f"Learned new pattern for {pattern_key}: {pattern['occurrences']} occurrences")
            
        except Exception as e:
            self.logger.error(f"Failed to save pattern: {e}")
    
    def get_action_recommendation(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendation for an action based on learned patterns
        
        Args:
            action: Action to get recommendation for
            context: Current context
            
        Returns:
            Recommendation with confidence and suggestions
        """
        try:
            recommendation = {
                'action': action,
                'confidence': 0.5,  # Default neutral confidence
                'suggestions': [],
                'warnings': [],
                'expected_success_rate': 0.5
            }
            
            # Check action history
            action_stats = self.action_outcomes.get(action, {'success': 0, 'failure': 0})
            total_attempts = action_stats['success'] + action_stats['failure']
            
            if total_attempts > 0:
                success_rate = action_stats['success'] / total_attempts
                recommendation['expected_success_rate'] = success_rate
                recommendation['confidence'] = min(0.9, 0.5 + (success_rate - 0.5))
                
                if success_rate < 0.3:
                    recommendation['warnings'].append("This action has low success rate historically")
                elif success_rate > 0.8:
                    recommendation['suggestions'].append("This action has high success rate")
            
            # Check for learned patterns
            success_patterns = self._find_matching_patterns(action, context, 'success')
            failure_patterns = self._find_matching_patterns(action, context, 'failure')
            
            if success_patterns:
                recommendation['confidence'] = min(0.95, recommendation['confidence'] + 0.2)
                recommendation['suggestions'].append("Similar successful patterns found")
            
            if failure_patterns:
                recommendation['confidence'] = max(0.1, recommendation['confidence'] - 0.3)
                recommendation['warnings'].append("Similar failure patterns found")
            
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendation: {e}")
            return {
                'action': action,
                'confidence': 0.5,
                'suggestions': [],
                'warnings': ['Failed to analyze patterns'],
                'expected_success_rate': 0.5
            }
    
    def _find_matching_patterns(self, action: str, context: Dict[str, Any], outcome_type: str) -> List[Dict[str, Any]]:
        """Find patterns that match the current context"""
        matching_patterns = []
        
        try:
            pattern_file = Path(f"data/patterns/{action}_{outcome_type}.json")
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    pattern = json.load(f)
                    
                # Check if context matches pattern
                if self._context_matches_pattern(context, pattern):
                    matching_patterns.append(pattern)
                    
        except Exception as e:
            self.logger.error(f"Failed to load pattern: {e}")
        
        return matching_patterns
    
    def _context_matches_pattern(self, context: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if context matches a learned pattern"""
        try:
            # Check common context
            for key, expected_value in pattern.get('common_context', {}).items():
                if key not in context or context[key] != expected_value:
                    return False
            
            # Check context ranges
            for key, range_info in pattern.get('context_ranges', {}).items():
                if key not in context:
                    return False
                
                value = context[key]
                if not isinstance(value, (int, float)):
                    return False
                
                if not (range_info['min'] <= value <= range_info['max']):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pattern matching failed: {e}")
            return False
    
    def adapt_strategy(self, action: str, repeated_failures: int = 3) -> Dict[str, Any]:
        """
        Adapt strategy based on repeated failures
        
        Args:
            action: Action that's failing repeatedly
            repeated_failures: Number of consecutive failures
            
        Returns:
            Adaptation suggestions
        """
        adaptations = {
            'original_action': action,
            'suggested_changes': [],
            'alternative_actions': [],
            'parameter_adjustments': {}
        }
        
        try:
            # Analyze recent failures for this action
            recent_failures = [exp for exp in self.experience_memory 
                             if exp['action'] == action and exp['outcome'] == 'failure'][-repeated_failures:]
            
            if len(recent_failures) >= repeated_failures:
                # Look for common failure patterns
                common_contexts = self._find_common_failure_contexts(recent_failures)
                
                # Suggest parameter adjustments
                if 'timing' in common_contexts:
                    adaptations['parameter_adjustments']['timing'] = 'increase_delay'
                    adaptations['suggested_changes'].append("Increase delay between actions")
                
                if 'position_accuracy' in common_contexts:
                    adaptations['parameter_adjustments']['position_tolerance'] = 'increase'
                    adaptations['suggested_changes'].append("Increase position tolerance")
                
                # Suggest alternative actions
                successful_actions = [exp['action'] for exp in self.experience_memory 
                                    if exp['outcome'] == 'success']
                if successful_actions:
                    from collections import Counter
                    common_successful = Counter(successful_actions).most_common(3)
                    adaptations['alternative_actions'] = [action for action, count in common_successful 
                                                        if action != action]
                
                self.stats['adaptations_made'] += 1
                self.logger.info(f"Generated adaptations for {action} after {repeated_failures} failures")
        
        except Exception as e:
            self.logger.error(f"Strategy adaptation failed: {e}")
        
        return adaptations
    
    def _find_common_failure_contexts(self, failures: List[Dict[str, Any]]) -> List[str]:
        """Find common contexts in failure experiences"""
        common_contexts = []
        
        try:
            # Analyze timing issues
            timestamps = [exp['timestamp'] for exp in failures]
            if len(timestamps) > 1:
                intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
                if all(interval < 1.0 for interval in intervals):  # Actions too fast
                    common_contexts.append('timing')
            
            # Analyze position accuracy issues
            position_errors = []
            for failure in failures:
                details = failure.get('details', {})
                if 'position_error' in details:
                    position_errors.append(details['position_error'])
            
            if position_errors and sum(position_errors) / len(position_errors) > 10:  # High position error
                common_contexts.append('position_accuracy')
                
        except Exception as e:
            self.logger.error(f"Common context analysis failed: {e}")
        
        return common_contexts
    
    def learn_from_external_data(self, data: Dict[str, Any], source: str = "external") -> str:
        """
        Learn from external data sources
        
        Args:
            data: External data to learn from
            source: Source of the data
            
        Returns:
            Learning result summary
        """
        try:
            learned_items = 0
            
            # Process game updates
            if 'updates' in data:
                for update in data['updates']:
                    self._process_game_update(update)
                    learned_items += 1
            
            # Process strategies
            if 'strategies' in data:
                for strategy in data['strategies']:
                    self._process_strategy(strategy)
                    learned_items += 1
            
            # Process tips and tricks
            if 'tips' in data:
                for tip in data['tips']:
                    self._process_tip(tip)
                    learned_items += 1
            
            # Update statistics
            self.stats['items_learned'] += learned_items
            
            # Save learning data
            self._save_learning_data()
            
            result = f"Learned {learned_items} items from {source}"
            self.logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Failed to learn from external data: {e}"
            self.logger.error(error_msg)
            return error_msg
    
    def _process_game_update(self, update: Dict[str, Any]):
        """Process a game update for learning"""
        # Extract useful information from game updates
        # This would be customized based on the specific game
        pass
    
    def _process_strategy(self, strategy: Dict[str, Any]):
        """Process a strategy for learning"""
        # Learn new strategies from external sources
        pass
    
    def _process_tip(self, tip: Dict[str, Any]):
        """Process a tip for learning"""
        # Learn tips and tricks
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get learning system statistics"""
        return self.stats.copy()
    
    def reset_learning_data(self):
        """Reset all learning data (use with caution)"""
        self.experience_memory.clear()
        self.success_patterns.clear()
        self.failure_patterns.clear()
        self.action_outcomes.clear()
        
        self.stats = {
            'total_experiences': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'patterns_learned': 0,
            'adaptations_made': 0,
            'items_learned': 0
        }
        
        # Clear saved data
        try:
            learning_file = Path("data/learning_data.pkl")
            if learning_file.exists():
                learning_file.unlink()
            
            patterns_dir = Path("data/patterns")
            if patterns_dir.exists():
                for pattern_file in patterns_dir.glob("*.json"):
                    pattern_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to clear learning files: {e}")
        
        self.logger.info("Learning data reset")
