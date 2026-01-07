"""
Generic Template - Handles any experiment type not covered by specific templates
Uses AI to generate complete HTML/JS code directly
"""
from typing import Dict, Any
from .base_template import BaseTemplate
import logging

logger = logging.getLogger(__name__)


class GenericTemplate(BaseTemplate):
    """Generic template that uses AI to generate code for any experiment type"""
    
    def generate(self, config: Dict[str, Any]) -> str:
        """
        Generate HTML code for generic/custom experiments
        For now, returns a placeholder that can be enhanced with AI code generation
        """
        title = config.get("title", "Custom Experiment")
        description = config.get("description", "An interactive experiment")
        experiment_type = config.get("params", {}).get("experimentType", "interactive")
        custom_code = config.get("params", {}).get("customCode", "")
        
        # If custom code is provided (from AI generation), use it
        if custom_code:
            return self._wrap_custom_code(title, description, custom_code)
        
        # Otherwise, generate a basic interactive canvas based on experiment type
        return self._generate_basic_experiment(title, description, experiment_type, config.get("params", {}))
    
    def _wrap_custom_code(self, title: str, description: str, code: str) -> str:
        """Wrap AI-generated code in HTML structure"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.escape_js_string(title)}</title>
    <meta name="description" content="{self.escape_js_string(description)}">
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
            overflow-x: hidden;
        }}
        
        .header {{
            background: rgba(15, 23, 42, 0.9);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        
        .header h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: #94a3b8;
            font-size: 0.875rem;
        }}
        
        .content {{
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{self.escape_js_string(title)}</h1>
        <p>{self.escape_js_string(description)}</p>
    </div>
    <div class="content">
        {code}
    </div>
</body>
</html>"""
    
    def _generate_basic_experiment(self, title: str, description: str, experiment_type: str, params: Dict[str, Any]) -> str:
        """Generate a basic interactive experiment based on type"""
        
        # Different basic templates based on experiment type
        if "sort" in experiment_type.lower() or "algorithm" in experiment_type.lower():
            return self._generate_sorting_visualization(title, description, params)
        elif "graph" in experiment_type.lower() or "chart" in experiment_type.lower():
            return self._generate_graph_visualization(title, description, params)
        else:
            return self._generate_default_interactive(title, description, params)
    
    def _generate_sorting_visualization(self, title: str, description: str, params: Dict[str, Any]) -> str:
        """Generate a basic sorting algorithm visualization"""
        array_size = params.get("arraySize", 20)
        algorithm = params.get("algorithm", "bubble")
        
        return self.wrap_html(
            title=title,
            description=description,
            body_content=f"""
            <div class="controls">
                <h1>{self.escape_js_string(title)}</h1>
                <p>{self.escape_js_string(description)}</p>
                <div class="buttons">
                    <button class="btn-primary" onclick="generateArray()">Generate New Array</button>
                    <button class="btn-primary" onclick="startSort()">Start Sorting</button>
                    <button class="btn-secondary" onclick="resetArray()">Reset</button>
                </div>
            </div>
            <div id="canvas-container">
                <canvas id="canvas" width="1200" height="600"></canvas>
            </div>
            """,
            style="""
            #canvas-container {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            
            canvas {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 0.5rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
                background: rgba(15, 23, 42, 0.5);
            }
            """,
            script=f"""
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            let array = [];
            let isSorting = false;
            let animationSpeed = 50;
            
            function generateArray() {{
                array = [];
                for (let i = 0; i < {array_size}; i++) {{
                    array.push(Math.floor(Math.random() * 500) + 10);
                }}
                drawArray();
            }}
            
            function resetArray() {{
                isSorting = false;
                generateArray();
            }}
            
            function drawArray() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const barWidth = canvas.width / array.length;
                
                for (let i = 0; i < array.length; i++) {{
                    const barHeight = (array[i] / 510) * canvas.height;
                    const x = i * barWidth;
                    const y = canvas.height - barHeight;
                    
                    ctx.fillStyle = '#60a5fa';
                    ctx.fillRect(x, y, barWidth - 2, barHeight);
                    
                    ctx.strokeStyle = '#1e40af';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x, y, barWidth - 2, barHeight);
                }}
            }}
            
            async function bubbleSort() {{
                const n = array.length;
                for (let i = 0; i < n - 1; i++) {{
                    for (let j = 0; j < n - i - 1; j++) {{
                        if (!isSorting) return;
                        
                        if (array[j] > array[j + 1]) {{
                            [array[j], array[j + 1]] = [array[j + 1], array[j]];
                            drawArray();
                            await sleep(animationSpeed);
                        }}
                    }}
                }}
                isSorting = false;
            }}
            
            function sleep(ms) {{
                return new Promise(resolve => setTimeout(resolve, ms));
            }}
            
            async function startSort() {{
                if (isSorting) return;
                if (array.length === 0) generateArray();
                isSorting = true;
                await bubbleSort();
            }}
            
            // Initialize
            generateArray();
            """
        )
    
    def _generate_graph_visualization(self, title: str, description: str, params: Dict[str, Any]) -> str:
        """Generate a basic graph/chart visualization"""
        return self.wrap_html(
            title=title,
            description=description,
            body_content="""
            <div class="controls">
                <h1>Graph Visualization</h1>
                <p>Interactive graph visualization</p>
            </div>
            <div id="canvas-container">
                <canvas id="canvas" width="1200" height="600"></canvas>
            </div>
            """,
            script="""
            // Basic graph visualization placeholder
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#60a5fa';
            ctx.font = '24px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Graph Visualization - Customize this template', canvas.width / 2, canvas.height / 2);
            """
        )
    
    def _generate_default_interactive(self, title: str, description: str, params: Dict[str, Any]) -> str:
        """Generate a default interactive canvas"""
        return self.wrap_html(
            title=title,
            description=description,
            body_content="""
            <div class="controls">
                <h1>Interactive Experiment</h1>
                <p>Custom interactive visualization</p>
            </div>
            <div id="canvas-container">
                <canvas id="canvas" width="1200" height="600"></canvas>
            </div>
            """,
            script="""
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#60a5fa';
            ctx.font = '24px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Custom Experiment - Add your code here', canvas.width / 2, canvas.height / 2);
            """
        )

