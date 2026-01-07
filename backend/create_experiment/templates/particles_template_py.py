"""
Particle System Template
Generates interactive particle physics simulation
"""
from typing import Dict, Any
from .base_template import BaseTemplate


class ParticlesTemplate(BaseTemplate):
    """Particle system with gravity and attraction forces"""
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate complete HTML for particle simulation"""
        
        # Extract parameters
        params = config.get("params", {})
        particle_count = params.get("particleCount", 200)
        gravity = params.get("gravity", 0.5)
        attraction_mode = params.get("attractionMode", "center")
        color_mode = params.get("color", "rainbow")
        
        title = config.get("title", "Particle System")
        description = config.get("description", "Interactive particle physics simulation")
        
        body = f"""
        <div class="controls">
            <h1>{self.escape_js_string(title)}</h1>
            <p>{self.escape_js_string(description)}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Particles</div>
                    <div class="stat-value" style="color: #60a5fa;">{particle_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Gravity</div>
                    <div class="stat-value" style="color: #10b981;">{gravity}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Attraction</div>
                    <div class="stat-value" style="color: #a78bfa; text-transform: capitalize;">{attraction_mode}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Color</div>
                    <div class="stat-value" style="color: #f59e0b; text-transform: capitalize;">{color_mode}</div>
                </div>
            </div>
            
            <div class="buttons">
                <button id="pause-btn" class="btn-primary">⏸ Pause</button>
                <button id="reset-btn" class="btn-secondary">↻ Reset</button>
            </div>
        </div>
        
        <div id="canvas-container">
            <canvas id="canvas" width="800" height="600" style="cursor: crosshair;"></canvas>
        </div>
        """
        
        script = f"""
        // Configuration
        const CONFIG = {{
            particleCount: {particle_count},
            gravity: {gravity},
            attractionMode: '{attraction_mode}',
            colorMode: '{color_mode}',
            canvasWidth: 800,
            canvasHeight: 600
        }};
        
        // State
        let particles = [];
        let isRunning = true;
        let mouseX = CONFIG.canvasWidth / 2;
        let mouseY = CONFIG.canvasHeight / 2;
        
        // Canvas setup
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Initialize particles
        function initParticles() {{
            particles = [];
            for (let i = 0; i < CONFIG.particleCount; i++) {{
                particles.push({{
                    x: Math.random() * CONFIG.canvasWidth,
                    y: Math.random() * CONFIG.canvasHeight,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    hue: Math.random() * 360,
                    life: 1.0
                }});
            }}
        }}
        
        // Get particle color
        function getColor(particle) {{
            if (CONFIG.colorMode === 'rainbow') {{
                return `hsl(${{particle.hue}}, 80%, 60%)`;
            }} else if (CONFIG.colorMode === 'blue') {{
                return '#3b82f6';
            }} else if (CONFIG.colorMode === 'fire') {{
                return `hsl(${{20 + Math.random() * 40}}, 100%, 60%)`;
            }} else {{
                return '#a855f7';
            }}
        }}
        
        // Update simulation
        function update() {{
            if (!isRunning) return;
            
            particles.forEach(p => {{
                // Apply gravity
                p.vy += CONFIG.gravity * 0.1;
                
                // Apply attraction
                if (CONFIG.attractionMode === 'center') {{
                    const dx = CONFIG.canvasWidth / 2 - p.x;
                    const dy = CONFIG.canvasHeight / 2 - p.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance > 0) {{
                        p.vx += (dx / distance) * 0.1;
                        p.vy += (dy / distance) * 0.1;
                    }}
                }} else if (CONFIG.attractionMode === 'mouse') {{
                    const dx = mouseX - p.x;
                    const dy = mouseY - p.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance > 0 && distance < 200) {{
                        p.vx += (dx / distance) * 0.2;
                        p.vy += (dy / distance) * 0.2;
                    }}
                }}
                
                // Apply velocity
                p.x += p.vx;
                p.y += p.vy;
                
                // Damping
                p.vx *= 0.99;
                p.vy *= 0.99;
                
                // Bounce off walls
                if (p.x < 0 || p.x > CONFIG.canvasWidth) {{
                    p.vx *= -0.8;
                    p.x = Math.max(0, Math.min(CONFIG.canvasWidth, p.x));
                }}
                if (p.y < 0 || p.y > CONFIG.canvasHeight) {{
                    p.vy *= -0.8;
                    p.y = Math.max(0, Math.min(CONFIG.canvasHeight, p.y));
                }}
                
                // Update hue for rainbow
                if (CONFIG.colorMode === 'rainbow') {{
                    p.hue = (p.hue + 0.5) % 360;
                }}
            }});
        }}
        
        // Render
        function render() {{
            // Fade effect instead of clear
            ctx.fillStyle = 'rgba(15, 23, 42, 0.15)';
            ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
            
            particles.forEach(p => {{
                const color = getColor(p);
                
                // Particle glow
                const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 10);
                gradient.addColorStop(0, color);
                gradient.addColorStop(1, 'rgba(0,0,0,0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 10, 0, Math.PI * 2);
                ctx.fill();
                
                // Particle core
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
                ctx.fill();
            }});
        }}
        
        // Animation loop
        function animate() {{
            update();
            render();
            requestAnimationFrame(animate);
        }}
        
        // Mouse tracking
        canvas.addEventListener('mousemove', (e) => {{
            const rect = canvas.getBoundingClientRect();
            mouseX = e.clientX - rect.left;
            mouseY = e.clientY - rect.top;
        }});
        
        // Event listeners
        document.getElementById('pause-btn').addEventListener('click', () => {{
            isRunning = !isRunning;
            document.getElementById('pause-btn').textContent = isRunning ? '⏸ Pause' : '▶ Resume';
        }});
        
        document.getElementById('reset-btn').addEventListener('click', () => {{
            initParticles();
            // Clear canvas
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
        }});
        
        // Initialize and start
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
        initParticles();
        requestAnimationFrame(animate);
        """
        
        return self.wrap_html(title, description, body, script=script)
