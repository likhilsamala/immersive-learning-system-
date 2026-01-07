"""
Base Template - Parent class for all experiment templates
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTemplate(ABC):
    """Abstract base class for all experiment templates"""
    
    @abstractmethod
    def generate(self, config: Dict[str, Any]) -> str:
        """
        Generate complete HTML code for this template
        
        Args:
            config: Configuration dictionary containing:
                - template: Template ID
                - params: Template-specific parameters
                - title: Experiment title
                - description: Experiment description
        
        Returns:
            str: Complete HTML document as string
        """
        pass
    
    def wrap_html(self, title: str, description: str, body_content: str, 
                   style: str = "", script: str = "") -> str:
        """
        Wrap content in complete HTML document structure
        
        Args:
            title: Page title
            description: Meta description
            body_content: HTML content for body
            style: CSS styles
            script: JavaScript code
        
        Returns:
            str: Complete HTML document
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            overflow: hidden;
        }}
        
        #app {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .controls {{
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .controls h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .controls p {{
            color: #94a3b8;
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .stat-card {{
            background: rgba(30, 41, 59, 0.5);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.25rem;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
        }}
        
        .buttons {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        
        button {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        
        .btn-primary {{
            background: linear-gradient(to right, #3b82f6, #8b5cf6);
            color: white;
        }}
        
        .btn-secondary {{
            background: rgba(71, 85, 105, 0.5);
            color: #e2e8f0;
        }}
        
        #canvas-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        
        canvas {{
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 0.5rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            background: rgba(15, 23, 42, 0.5);
        }}
        
        {style}
    </style>
</head>
<body>
    <div id="app">
        {body_content}
    </div>
    
    <script>
        {script}
    </script>
</body>
</html>"""
    
    def escape_js_string(self, text: str) -> str:
        """Escape string for safe use in JavaScript"""
        return text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
