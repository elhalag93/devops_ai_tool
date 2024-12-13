from typing import Dict, Any, List
import json
from pathlib import Path
import os
from datetime import datetime

class AdaptiveConfig:
    def __init__(self):
        self.config_path = Path("config/adaptive")
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.learning_path = self.config_path / "learned_patterns.json"
        self.integration_path = self.config_path / "integrations.json"
        self._load_configs()

    def _load_configs(self):
        """Load or initialize configuration files"""
        self.learned_patterns = self._load_json(self.learning_path, {
            "code_patterns": {},
            "integration_patterns": {},
            "execution_patterns": {},
            "success_metrics": {}
        })
        
        self.integrations = self._load_json(self.integration_path, {
            "active_integrations": {},
            "available_integrations": {},
            "integration_metrics": {}
        })

    def _load_json(self, path: Path, default: Dict) -> Dict:
        """Load JSON file or create with default values"""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        with open(path, 'w') as f:
            json.dump(default, f, indent=2)
        return default

    def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Learn new patterns from successful operations"""
        timestamp = datetime.now().isoformat()
        
        if pattern_type == "code":
            self.learned_patterns["code_patterns"][timestamp] = pattern_data
        elif pattern_type == "integration":
            self.learned_patterns["integration_patterns"][timestamp] = pattern_data
        elif pattern_type == "execution":
            self.learned_patterns["execution_patterns"][timestamp] = pattern_data

        self._save_learned_patterns()

    def register_integration(self, integration_data: Dict[str, Any]):
        """Register new integration capabilities"""
        integration_id = integration_data.get("id")
        if integration_id:
            self.integrations["available_integrations"][integration_id] = {
                "config": integration_data,
                "registered_at": datetime.now().isoformat(),
                "status": "available"
            }
            self._save_integrations()

    def _save_learned_patterns(self):
        """Save learned patterns to file"""
        with open(self.learning_path, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)

    def _save_integrations(self):
        """Save integration configurations to file"""
        with open(self.integration_path, 'w') as f:
            json.dump(self.integrations, f, indent=2)

    def get_best_pattern(self, pattern_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get the most suitable pattern based on context"""
        patterns = self.learned_patterns.get(f"{pattern_type}_patterns", {})
        if not patterns:
            return {}

        # Score each pattern based on context similarity
        scored_patterns = []
        for timestamp, pattern in patterns.items():
            score = self._calculate_pattern_score(pattern, context)
            scored_patterns.append((score, pattern))

        # Return the highest scoring pattern
        if scored_patterns:
            return max(scored_patterns, key=lambda x: x[0])[1]
        return {}

    def _calculate_pattern_score(self, pattern: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate how well a pattern matches the current context"""
        score = 0.0
        
        # Match context keys
        common_keys = set(pattern.keys()) & set(context.keys())
        score += len(common_keys) / max(len(pattern), len(context))
        
        # Match values for common keys
        for key in common_keys:
            if pattern[key] == context[key]:
                score += 1.0
                
        return score

    def adapt_to_feedback(self, feedback: Dict[str, Any]):
        """Adapt configurations based on feedback"""
        pattern_type = feedback.get("type")
        success = feedback.get("success", False)
        context = feedback.get("context", {})
        
        if success:
            # Learn from successful patterns
            self.learn_pattern(pattern_type, context)
        else:
            # Update metrics for unsuccessful patterns
            self._update_failure_metrics(pattern_type, context)

    def _update_failure_metrics(self, pattern_type: str, context: Dict[str, Any]):
        """Update metrics for failed patterns"""
        metrics = self.learned_patterns["success_metrics"]
        pattern_metrics = metrics.setdefault(pattern_type, {})
        
        # Update failure count
        pattern_key = json.dumps(sorted(context.items()))
        current_metric = pattern_metrics.get(pattern_key, {"success": 0, "failure": 0})
        current_metric["failure"] += 1
        pattern_metrics[pattern_key] = current_metric
        
        self._save_learned_patterns() 