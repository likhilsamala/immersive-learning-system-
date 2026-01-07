"""
Code Generator - Generates complete HTML/JS code from config
"""
from typing import Dict, Any, List, Optional
import logging
from .prompt_engine import PromptEngine

# Import template generators
from .templates.network_template_py import NetworkTemplate
from .templates.particles_template_py import ParticlesTemplate
from .templates.flocking_template_py import FlockingTemplate
from .templates.waves_template_py import WavesTemplate
from .templates.generic_template_py import GenericTemplate
from .templates.base_template import BaseTemplate


logger = logging.getLogger(__name__)


class CodeGenerator:
    """Generates complete HTML/JS code from configuration"""
    
    def __init__(self):
        self.prompt_engine = PromptEngine()
        
        # Register all available templates
        self.templates = {
            "network": NetworkTemplate(),
            "particles": ParticlesTemplate(),
            "flocking": FlockingTemplate(),
            "waves": WavesTemplate(),
            "generic": GenericTemplate()
        }
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of all available templates with metadata"""
        template_info = self.prompt_engine.get_all_templates()
        result = []
        
        for template_id, info in template_info.items():
            result.append({
                "id": template_id,
                "name": info["name"],
                "description": info["description"],
                "params": info["params"],
                "examples": info["examples"]
            })
        
        return result
    
    def generate_html(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Generate complete HTML file from configuration
        
        Args:
            config: Validated configuration dictionary with:
                - template: Template ID (network, particles, etc.)
                - params: Template-specific parameters
                - title: Experiment title
                - description: Experiment description
        
        Returns:
            str: Complete HTML code ready to save/serve
        """
        try:
            template_id = config.get("template")
            
            if template_id not in self.templates:
                logger.error(f"Template '{template_id}' not found")
                return None
            
            template = self.templates[template_id]
            
            # Generate HTML using the template
            html_code = template.generate(config)
            
            logger.info(f"Successfully generated HTML for template: {template_id}")
            return html_code
            
        except Exception as e:
            logger.error(f"Error generating HTML: {e}", exc_info=True)
            return None
    
    def get_template_metadata(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for a specific template"""
        return self.prompt_engine.get_template_info(template_id)


# Standalone testing
if __name__ == "__main__":
    generator = CodeGenerator()
    
    # Test config
    test_config = {
        "template": "network",
        "params": {
            "nodeCount": 8,
            "packetRate": 2,
            "routingMode": "shortest",
            "layout": "circular"
        },
        "title": "Test Network Simulation",
        "description": "A test network simulation"
    }
    
    html = generator.generate_html(test_config)
    
    if html:
        print("✓ Successfully generated HTML")
        print(f"Length: {len(html)} characters")
        
        # Save to file for testing
        with open("test_output.html", "w") as f:
            f.write(html)
        print("✓ Saved to test_output.html")
    else:
        print("✗ Failed to generate HTML")
