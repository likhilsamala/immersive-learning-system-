"""
Wave Simulation Template
Generates interactive wave pattern visualization
"""
from typing import Dict, Any
from .base_template import BaseTemplate


class WavesTemplate(BaseTemplate):
    """Wave simulation with frequency and amplitude control"""
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate complete HTML for wave simulation"""
        
        params = config.get("params", {})
        frequency = params.get("frequency", 1.0)
        amplitude = params.get("amplitude", 50)
        wave_type = params.get("waveType", "sine")
        color_scheme = params.get("colorScheme", "blue")
        
        title = config.get("title", "Wave Simulation")
        description = config.get("description", "Interactive wave patterns")
        
        body = f"""
        <div class="controls">
            <h1>{self.escape_js_string(title)}</h1>
            <p>{self.escape_js_string(description)}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Frequency</div>
                    <div class="stat-value" style="color: #60a5fa;">{frequency}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Amplitude</div>
                    <div class="stat-value" style="color: #10b981;">{amplitude}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Wave Type</div>
                    <div class="stat-value" style="color: #a78bfa; text-transform: capitalize;">{wave_type}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Colors</div>
                    <div class="stat-value" style="color: #f59e0b; text-transform: capitalize;">{color_scheme}</div>
                </div>
            </div>
            
            <div class="buttons">
                <button id="pause-btn" class="btn-primary">Pause</button>
                <button id="reset-btn" class="btn-secondary">Reset</button>
            </div>
        </div>
        
        <div id="canvas-container">
            <canvas id="canvas" width="800" height="600"></canvas>
        </div>
        """
        
        script = f"""
        const CONFIG = {{
            frequency: {frequency},
            amplitude: {amplitude},
            waveType: '{wave_type}',
            colorScheme: '{color_scheme}',
            canvasWidth: 800,
            canvasHeight: 600
        }};
        
        let isRunning = true;
        let time = 0;
        
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        function getWaveValue(x, t, frequency) {{
            if (CONFIG.waveType === 'sine') {{
                return Math.sin((x * 0.02 + t) * frequency);
            }} else if (CONFIG.waveType === 'square') {{
                return Math.sign(Math.sin((x * 0.02 + t) * frequency));
            }} else if (CONFIG.waveType === 'triangle') {{
                return Math.asin(Math.sin((x * 0.02 + t) * frequency)) * 2 / Math.PI;
            }}
            return Math.sin((x * 0.02 + t) * frequency);
        }}
        
        function getColor(index, total) {{
            if (CONFIG.colorScheme === 'blue') {{
                return `hsl(220, 80%, ${{40 + (index / total) * 40}}%)`;
            }} else if (CONFIG.colorScheme === 'rainbow') {{
                return `hsl(${{(index / total) * 360}}, 80%, 60%)`;
            }} else if (CONFIG.colorScheme === 'fire') {{
                return `hsl(${{40 - (index / total) * 40}}, 100%, 60%)`;
            }}
            return `hsl(220, 80%, 60%)`;
        }}
        
        function animate() {{
            if (isRunning) {{
                time += 0.05;
            }}
            
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
            
            const numWaves = 5;
            const centerY = CONFIG.canvasHeight / 2;
            
            // Draw multiple wave layers
            for (let wave = 0; wave < numWaves; wave++) {{
                ctx.beginPath();
                ctx.strokeStyle = getColor(wave, numWaves);
                ctx.lineWidth = 3;
                ctx.globalAlpha = 0.6;
                
                const phaseShift = wave * 0.5;
                
                for (let x = 0; x < CONFIG.canvasWidth; x += 5) {{
                    const waveValue = getWaveValue(x, time + phaseShift, CONFIG.frequency);
                    const y = centerY + waveValue * CONFIG.amplitude * (1 - wave * 0.15);
                    
                    if (x === 0) {{
                        ctx.moveTo(x, y);
                    }} else {{
                        ctx.lineTo(x, y);
                    }}
                }}
                
                ctx.stroke();
            }}
            
            ctx.globalAlpha = 1;
            
            // Draw center line
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(0, centerY);
            ctx.lineTo(CONFIG.canvasWidth, centerY);
            ctx.stroke();
            
            requestAnimationFrame(animate);
        }}
        
        document.getElementById('pause-btn').addEventListener('click', () => {{
            isRunning = !isRunning;
            document.getElementById('pause-btn').textContent = isRunning ? '⏸ Pause' : '▶ Resume';
        }});
        
        document.getElementById('reset-btn').addEventListener('click', () => {{
            time = 0;
        }});
        
        requestAnimationFrame(animate);
        """
        
        return self.wrap_html(title, description, body, script=script)