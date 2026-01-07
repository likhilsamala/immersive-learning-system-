"""
Prompt Engineering Engine - Builds optimized prompts for Qwen2.5-Coder
"""
import json
import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PromptEngine:
    def __init__(self):
        # Template definitions - these describe what each template does
        self.templates = {
            "network": {
                "name": "Network Simulation",
                "description": "Simulates data packets flowing through network nodes with routing algorithms",
                "keywords": ["network", "nodes", "packets", "routing", "connection", "graph", "topology"],
                "params": {
                    "nodeCount": {"type": "int", "min": 4, "max": 12, "default": 8},
                    "packetRate": {"type": "int", "min": 1, "max": 10, "default": 2},
                    "routingMode": {"type": "select", "options": ["shortest", "random", "multipath"], "default": "shortest"},
                    "layout": {"type": "select", "options": ["circular", "grid", "random"], "default": "circular"}
                },
                "examples": [
                    "Create a network with many nodes",
                    "Show me packet routing with random paths",
                    "Network simulation with grid layout"
                ]
            },
            "particles": {
                "name": "Particle System",
                "description": "Simulates particles with physics like gravity, attraction, and motion",
                "keywords": ["particles", "physics", "gravity", "attraction", "motion", "swarm", "dots"],
                "params": {
                    "particleCount": {"type": "int", "min": 50, "max": 1000, "default": 200},
                    "gravity": {"type": "float", "min": 0, "max": 2, "default": 0.5},
                    "attractionMode": {"type": "select", "options": ["center", "mouse", "none"], "default": "center"},
                    "color": {"type": "select", "options": ["rainbow", "blue", "fire", "purple"], "default": "rainbow"}
                },
                "examples": [
                    "Particle system with strong gravity",
                    "Lots of colorful particles",
                    "Zero gravity particle simulation"
                ]
            },
            "flocking": {
                "name": "Flocking Simulation",
                "description": "Simulates bird-like flocking behavior with cohesion, separation, and alignment",
                "keywords": ["flocking", "birds", "boids", "swarm", "group", "cohesion", "flock"],
                "params": {
                    "boidCount": {"type": "int", "min": 20, "max": 200, "default": 50},
                    "cohesion": {"type": "float", "min": 0, "max": 2, "default": 1},
                    "separation": {"type": "float", "min": 0, "max": 2, "default": 1},
                    "alignment": {"type": "float", "min": 0, "max": 2, "default": 1},
                    "maxSpeed": {"type": "float", "min": 1, "max": 5, "default": 3}
                },
                "examples": [
                    "Bird flocking simulation",
                    "Tight swarm behavior",
                    "Boids with high separation"
                ]
            },
            "waves": {
                "name": "Wave Simulation",
                "description": "Generates wave patterns with frequency, amplitude, and different wave types",
                "keywords": ["waves", "wave", "sine", "ripple", "oscillation", "frequency", "amplitude", "sound"],
                "params": {
                    "frequency": {"type": "float", "min": 0.1, "max": 5, "default": 1},
                    "amplitude": {"type": "int", "min": 10, "max": 100, "default": 50},
                    "waveType": {"type": "select", "options": ["sine", "square", "triangle"], "default": "sine"},
                    "colorScheme": {"type": "select", "options": ["blue", "rainbow", "fire"], "default": "blue"}
                },
                "examples": [
                    "Wave simulation with high frequency",
                    "Sine waves with rainbow colors",
                    "Square wave pattern"
                ]
            }
        }
    
    def build_prompt(self, user_prompt: str, template_hint: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None) -> str:
        """
        Build the complete prompt for Qwen2.5-Coder
        
        This uses few-shot learning to teach the model the expected format
        """
        
        # Select template based on keywords if no hint
        suggested_template = template_hint or self._detect_template(user_prompt)
        
        # Check if the request matches any known template
        matches_template = self._check_template_match(user_prompt)
        
        # Enhance user prompt with title/description if provided separately
        enhanced_prompt = user_prompt
        if title and title not in user_prompt:
            enhanced_prompt = f"{title}. {user_prompt}"
        if description and description not in user_prompt:
            enhanced_prompt = f"{enhanced_prompt} {description}"
        
        prompt = f"""You are an expert at generating configuration files for interactive simulations.
Your task is to analyze the user's request and generate a valid JSON configuration.

Available Templates:
{self._format_templates_info()}

GENERIC TEMPLATE:
- id: "generic"
- name: "Generic/Custom Experiment"
- description: "Use this for experiments that don't match any specific template (e.g., sorting algorithms, data structures, custom visualizations)"
- params: {{
    "experimentType": "string describing the experiment type (e.g., 'sorting', 'graph', 'algorithm', 'data-structure')",
    "customCode": "optional: if you can generate complete HTML/JS code, include it here as a string",
    "arraySize": "optional: number of elements for array-based experiments (5-100)",
    "nodeCount": "optional: number of nodes for graph/tree experiments (1-100)",
    "algorithm": "optional: specific algorithm name (e.g., 'bubble-sort', 'quick-sort', 'dfs', 'bfs')"
  }}

User Request: "{enhanced_prompt}"

Instructions:
1. FIRST, check if the request matches any specific template (network, particles, flocking, waves)
2. If it matches a specific template, use that template with appropriate parameters
3. If it DOES NOT match any specific template (e.g., "bubble sort", "binary tree", "graph algorithm"), use "generic" template
4. For generic template:
   - Set "experimentType" to describe the experiment (e.g., "bubble-sort", "binary-search-tree", "graph-traversal")
   - If you can generate HTML/JS code directly, include it in "customCode" field
   - Otherwise, leave "customCode" empty and the system will generate a basic visualization
5. Set parameter values that match what the user described
6. Create a descriptive title and description based on the user's request
7. Return ONLY valid JSON, no other text or explanation
8. All parameter values must be within the specified ranges for specific templates

Response Format (JSON only):
{{
  "template": "template_name" or "generic",
  "params": {{
    "param1": value1,
    "param2": value2,
    // For generic template, include:
    "experimentType": "description",
    "customCode": "optional HTML/JS code"
  }},
  "title": "Descriptive Title",
  "description": "Brief description of what this experiment shows"
}}

Examples:

Example 1:
User: "Create a network simulation with many nodes and fast packets"
{{
  "template": "network",
  "params": {{
    "nodeCount": 12,
    "packetRate": 8,
    "routingMode": "shortest",
    "layout": "circular"
  }},
  "title": "High-Speed Network Simulation",
  "description": "Dense network topology with rapid packet transmission showing efficient routing"
}}

Example 2:
User: "Show me particles with zero gravity"
{{
  "template": "particles",
  "params": {{
    "particleCount": 300,
    "gravity": 0,
    "attractionMode": "none",
    "color": "rainbow"
  }},
  "title": "Zero-Gravity Particle Field",
  "description": "Particles floating freely in space without gravitational forces"
}}

Example 3:
User: "Bird flocking with tight groups"
{{
  "template": "flocking",
  "params": {{
    "boidCount": 100,
    "cohesion": 1.8,
    "separation": 0.5,
    "alignment": 1.5,
    "maxSpeed": 3
  }},
  "title": "Tight Formation Flocking",
  "description": "Birds forming cohesive groups with strong attraction to flock center"
}}

Example 4:
User: "Wave simulation with high frequency"
{{
  "template": "waves",
  "params": {{
    "frequency": 3.5,
    "amplitude": 60,
    "waveType": "sine",
    "colorScheme": "blue"
  }},
  "title": "High-Frequency Wave Pattern",
  "description": "Rapid oscillating wave patterns with increased frequency"
}}

Example 5:
User: "Bubble sort algorithm visualization"
{{
  "template": "generic",
  "params": {{
    "experimentType": "bubble-sort",
    "arraySize": 20
  }},
  "title": "Bubble Sort Visualization",
  "description": "Interactive visualization of the bubble sort algorithm showing step-by-step sorting process"
}}

Example 6:
User: "Binary search tree visualization"
{{
  "template": "generic",
  "params": {{
    "experimentType": "binary-search-tree",
    "nodeCount": 15
  }},
  "title": "Binary Search Tree Visualization",
  "description": "Interactive visualization of binary search tree operations including insertion and traversal"
}}

Now generate the JSON configuration for the user's request. Remember: return ONLY the JSON object, nothing else.
"""
        return prompt
    
    def build_refinement_prompt(self, current_config: Dict[str, Any], refinement_request: str) -> str:
        """
        Build prompt for refining an existing configuration
        """
        prompt = f"""You are refining an existing simulation configuration based on user feedback.

Current Configuration:
{json.dumps(current_config, indent=2)}

User Refinement Request: "{refinement_request}"

Instructions:
1. Modify the appropriate parameters based on the user's request
2. Keep the same template unless explicitly requested to change
3. Keep parameters within valid ranges
4. Return ONLY the updated JSON configuration

Return the complete updated configuration as JSON:
"""
        return prompt
    
    def _detect_template(self, user_prompt: str) -> str:
        """
        Detect which template to use based on keywords in user prompt
        """
        prompt_lower = user_prompt.lower()
        
        # Check for generic experiment keywords (algorithms, data structures, etc.)
        generic_keywords = [
            "sort", "algorithm", "tree", "graph", "data structure", "binary", "heap",
            "queue", "stack", "linked list", "array", "hash", "search", "traversal",
            "merge", "quick", "insertion", "selection", "bubble", "heap sort",
            "dfs", "bfs", "dijkstra", "pathfinding", "recursion", "iteration"
        ]
        
        if any(keyword in prompt_lower for keyword in generic_keywords):
            logger.info("Detected generic experiment type from keywords")
            return "generic"
        
        # Count keyword matches for each template
        scores = {}
        for template_id, template_info in self.templates.items():
            score = sum(1 for keyword in template_info["keywords"] if keyword in prompt_lower)
            scores[template_id] = score
        
        # Return template with highest score, or default to generic
        if max(scores.values()) > 0:
            best_template = max(scores, key=scores.get)
            logger.info(f"Detected template '{best_template}' from keywords")
            return best_template
        
        logger.info("No keywords matched, defaulting to 'generic'")
        return "generic"
    
    def _check_template_match(self, user_prompt: str) -> bool:
        """
        Check if the user prompt matches any specific template
        """
        prompt_lower = user_prompt.lower()
        
        # Check for generic keywords first
        generic_keywords = [
            "sort", "algorithm", "tree", "graph", "data structure", "binary"
        ]
        if any(keyword in prompt_lower for keyword in generic_keywords):
            return False
        
        # Check for specific template keywords
        for template_id, template_info in self.templates.items():
            if any(keyword in prompt_lower for keyword in template_info["keywords"]):
                return True
        
        return False
    
    def _format_templates_info(self) -> str:
        """
        Format template information for the prompt
        """
        lines = []
        for template_id, info in self.templates.items():
            lines.append(f"\n{template_id.upper()}: {info['name']}")
            lines.append(f"  Description: {info['description']}")
            lines.append(f"  Parameters:")
            for param_name, param_info in info['params'].items():
                if param_info['type'] == 'select':
                    lines.append(f"    - {param_name}: {param_info['options']} (default: {param_info['default']})")
                else:
                    lines.append(f"    - {param_name}: {param_info['min']}-{param_info['max']} (default: {param_info['default']})")
        return '\n'.join(lines)
    
    def extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from AI response, handling various formats
        """
        # Try to find JSON in the response
        # Pattern 1: Look for JSON object
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                logger.info("Successfully extracted JSON from response")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON match: {e}")
        
        # Pattern 2: Try parsing the entire response
        try:
            parsed = json.loads(response.strip())
            logger.info("Successfully parsed entire response as JSON")
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Pattern 3: Look for code blocks
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if code_block_match:
            try:
                parsed = json.loads(code_block_match.group(1))
                logger.info("Successfully extracted JSON from code block")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse code block JSON: {e}")
        
        logger.error("Could not extract valid JSON from response")
        return None
    
    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific template
        """
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> Dict[str, Any]:
        """
        Get all available templates
        """
        return self.templates