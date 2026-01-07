"""
Configuration Validator - Ensures generated configs are safe and valid
"""
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    def __init__(self):
        # Define validation schemas for each template
        self.schemas = {
            "network": {
                "nodeCount": {"type": int, "min": 4, "max": 12},
                "packetRate": {"type": int, "min": 1, "max": 10},
                "routingMode": {"type": str, "allowed": ["shortest", "random", "multipath"]},
                "layout": {"type": str, "allowed": ["circular", "grid", "random"]}
            },
            "particles": {
                "particleCount": {"type": int, "min": 50, "max": 1000},
                "gravity": {"type": (int, float), "min": 0, "max": 2},
                "attractionMode": {"type": str, "allowed": ["center", "mouse", "none"]},
                "color": {"type": str, "allowed": ["rainbow", "blue", "fire", "purple"]}
            },
            "flocking": {
                "boidCount": {"type": int, "min": 20, "max": 200},
                "cohesion": {"type": (int, float), "min": 0, "max": 2},
                "separation": {"type": (int, float), "min": 0, "max": 2},
                "alignment": {"type": (int, float), "min": 0, "max": 2},
                "maxSpeed": {"type": (int, float), "min": 1, "max": 5}
            },
            "waves": {
                "frequency": {"type": (int, float), "min": 0.1, "max": 5},
                "amplitude": {"type": int, "min": 10, "max": 100},
                "waveType": {"type": str, "allowed": ["sine", "square", "triangle"]},
                "colorScheme": {"type": str, "allowed": ["blue", "rainbow", "fire"]}
            },
            "generic": {
                "experimentType": {"type": str},  # Any string is allowed
                "customCode": {"type": str, "optional": True},  # Optional HTML/JS code
                "arraySize": {"type": int, "min": 5, "max": 100, "optional": True},
                "nodeCount": {"type": int, "min": 1, "max": 100, "optional": True},
                "algorithm": {"type": str, "optional": True}
            }
        }
    
    def validate(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a configuration object
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check required top-level fields
            required_fields = ["template", "params", "title", "description"]
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"
            
            # Check template exists
            template = config["template"].lower()
            config["template"] = template  # Update to lowercase
            if template not in self.schemas:
                if template == "none":
                    template = "generic"
                    config["template"] = "generic"
                    logger.info("Defaulting unknown template 'none' to 'generic'")
                else:
                    # For unknown templates, default to generic
                    logger.warning(f"Unknown template '{template}', defaulting to 'generic'")
                    template = "generic"
                    config["template"] = "generic"
            
            # Validate params
            params = config["params"]
            if not isinstance(params, dict):
                return False, "params must be a dictionary"
            
            schema = self.schemas[template]
            
            # Check each parameter
            for param_name, param_value in params.items():
                if param_name not in schema:
                    # For generic template, allow unknown parameters
                    if template == "generic":
                        logger.info(f"Allowing unknown parameter '{param_name}' for generic template")
                        continue
                    else:
                        logger.warning(f"Unknown parameter '{param_name}' for template '{template}'")
                        continue
                
                validation_rules = schema[param_name]
                
                # Skip optional parameters if not provided
                if validation_rules.get("optional", False) and param_value is None:
                    continue
                
                # Type check
                expected_type = validation_rules["type"]
                # Handle tuple types (e.g., (int, float))
                if isinstance(expected_type, tuple):
                    if not isinstance(param_value, expected_type):
                        return False, f"Parameter '{param_name}' must be one of types {expected_type}"
                else:
                    if not isinstance(param_value, expected_type):
                        return False, f"Parameter '{param_name}' must be of type {expected_type}"
                
                # Range check for numeric values
                if "min" in validation_rules:
                    if param_value < validation_rules["min"]:
                        return False, f"Parameter '{param_name}' must be >= {validation_rules['min']}"
                
                if "max" in validation_rules:
                    if param_value > validation_rules["max"]:
                        return False, f"Parameter '{param_name}' must be <= {validation_rules['max']}"
                
                # Allowed values check for strings
                if "allowed" in validation_rules:
                    if param_value not in validation_rules["allowed"]:
                        return False, f"Parameter '{param_name}' must be one of {validation_rules['allowed']}"
            
            # Validate title and description
            title = config.get("title", "")
            description = config.get("description", "")
            
            if not isinstance(title, str) or len(title) < 3:
                return False, "Title must be a string with at least 3 characters"
            
            if not isinstance(description, str) or len(description) < 10:
                return False, "Description must be a string with at least 10 characters"
            
            if len(title) > 100:
                return False, "Title must be less than 100 characters"
            
            if len(description) > 500:
                return False, "Description must be less than 500 characters"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def sanitize(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize configuration by clamping values to valid ranges
        """
        template = config.get("template")
        if template not in self.schemas:
            return config
        
        schema = self.schemas[template]
        sanitized_params = {}
        
        for param_name, param_value in config.get("params", {}).items():
            if param_name not in schema:
                continue
            
            rules = schema[param_name]
            
            # Clamp numeric values
            if "min" in rules and "max" in rules:
                if isinstance(param_value, (int, float)):
                    param_value = max(rules["min"], min(rules["max"], param_value))
            
            # Validate allowed values
            if "allowed" in rules:
                if param_value not in rules["allowed"]:
                    param_value = rules["allowed"][0]  # Use first allowed value as default
            
            sanitized_params[param_name] = param_value
        
        return {
            **config,
            "params": sanitized_params
        }
    
    def get_defaults(self, template: str) -> Dict[str, Any]:
        """
        Get default configuration for a template
        """
        defaults = {
            "network": {
                "nodeCount": 8,
                "packetRate": 2,
                "routingMode": "shortest",
                "layout": "circular"
            },
            "particles": {
                "particleCount": 200,
                "gravity": 0.5,
                "attractionMode": "center",
                "color": "rainbow"
            },
            "flocking": {
                "boidCount": 50,
                "cohesion": 1.0,
                "separation": 1.0,
                "alignment": 1.0,
                "maxSpeed": 3.0
            },
            "waves": {
                "frequency": 1.0,
                "amplitude": 50,
                "waveType": "sine",
                "colorScheme": "blue"
            },
            "generic": {
                "experimentType": "interactive",
                "arraySize": 20
            }
        }
        
        return defaults.get(template, {})
