"""
Flocking Simulation Template
Generates boid flocking behavior simulation
"""
from typing import Dict, Any
from .base_template import BaseTemplate


class FlockingTemplate(BaseTemplate):
    """Flocking simulation with cohesion, separation, and alignment"""
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate complete HTML for flocking simulation"""
        
        params = config.get("params", {})
        boid_count = params.get("boidCount", 50)
        cohesion = params.get("cohesion", 1.0)
        separation = params.get("separation", 1.0)
        alignment = params.get("alignment", 1.0)
        max_speed = params.get("maxSpeed", 3.0)
        
        title = config.get("title", "Flocking Simulation")
        description = config.get("description", "Boid flocking behavior")
        
        body = f"""
        <div class="controls">
            <h1>{self.escape_js_string(title)}</h1>
            <p>{self.escape_js_string(description)}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Boids</div>
                    <div class="stat-value" style="color: #60a5fa;">{boid_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Cohesion</div>
                    <div class="stat-value" style="color: #10b981;">{cohesion}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Separation</div>
                    <div class="stat-value" style="color: #ef4444;">{separation}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Alignment</div>
                    <div class="stat-value" style="color: #a78bfa;">{alignment}</div>
                </div>
            </div>
            
            <div class="buttons">
                <button id="pause-btn" class="btn-primary">⏸ Pause</button>
                <button id="reset-btn" class="btn-secondary">↻ Reset</button>
            </div>
        </div>
        
        <div id="canvas-container">
            <canvas id="canvas" width="800" height="600"></canvas>
        </div>
        """
        
        script = f"""
        const CONFIG = {{
            boidCount: {boid_count},
            cohesion: {cohesion},
            separation: {separation},
            alignment: {alignment},
            maxSpeed: {max_speed},
            perceptionRadius: 50,
            canvasWidth: 800,
            canvasHeight: 600
        }};
        
        let boids = [];
        let isRunning = true;
        
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        class Boid {{
            constructor() {{
                this.x = Math.random() * CONFIG.canvasWidth;
                this.y = Math.random() * CONFIG.canvasHeight;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.hue = Math.random() * 360;
            }}
            
            update(boids) {{
                let avgX = 0, avgY = 0;
                let avgVx = 0, avgVy = 0;
                let separateX = 0, separateY = 0;
                let neighbors = 0;
                
                // Check all other boids
                boids.forEach(other => {{
                    if (other === this) return;
                    
                    const dx = other.x - this.x;
                    const dy = other.y - this.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    
                    if (dist < CONFIG.perceptionRadius) {{
                        // Cohesion
                        avgX += other.x;
                        avgY += other.y;
                        
                        // Alignment
                        avgVx += other.vx;
                        avgVy += other.vy;
                        
                        // Separation
                        if (dist < 25) {{
                            separateX -= dx / dist;
                            separateY -= dy / dist;
                        }}
                        
                        neighbors++;
                    }}
                }});
                
                if (neighbors > 0) {{
                    // Cohesion
                    avgX /= neighbors;
                    avgY /= neighbors;
                    this.vx += (avgX - this.x) * 0.001 * CONFIG.cohesion;
                    this.vy += (avgY - this.y) * 0.001 * CONFIG.cohesion;
                    
                    // Alignment
                    avgVx /= neighbors;
                    avgVy /= neighbors;
                    this.vx += (avgVx - this.vx) * 0.05 * CONFIG.alignment;
                    this.vy += (avgVy - this.vy) * 0.05 * CONFIG.alignment;
                    
                    // Separation
                    this.vx += separateX * 0.05 * CONFIG.separation;
                    this.vy += separateY * 0.05 * CONFIG.separation;
                }}
                
                // Limit speed
                const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (speed > CONFIG.maxSpeed) {{
                    this.vx = (this.vx / speed) * CONFIG.maxSpeed;
                    this.vy = (this.vy / speed) * CONFIG.maxSpeed;
                }}
                
                // Update position
                this.x += this.vx;
                this.y += this.vy;
                
                // Wrap around edges
                if (this.x < 0) this.x = CONFIG.canvasWidth;
                if (this.x > CONFIG.canvasWidth) this.x = 0;
                if (this.y < 0) this.y = CONFIG.canvasHeight;
                if (this.y > CONFIG.canvasHeight) this.y = 0;
            }}
            
            draw() {{
                const angle = Math.atan2(this.vy, this.vx);
                
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(angle);
                
                // Triangle shape
                ctx.fillStyle = `hsl(${{this.hue}}, 70%, 60%)`;
                ctx.beginPath();
                ctx.moveTo(8, 0);
                ctx.lineTo(-4, 4);
                ctx.lineTo(-4, -4);
                ctx.closePath();
                ctx.fill();
                
                ctx.restore();
            }}
        }}
        
        function initBoids() {{
            boids = [];
            for (let i = 0; i < CONFIG.boidCount; i++) {{
                boids.push(new Boid());
            }}
        }}
        
        function animate() {{
            if (isRunning) {{
                boids.forEach(boid => boid.update(boids));
            }}
            
            ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
            ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
            
            boids.forEach(boid => boid.draw());
            
            requestAnimationFrame(animate);
        }}
        
        document.getElementById('pause-btn').addEventListener('click', () => {{
            isRunning = !isRunning;
            document.getElementById('pause-btn').textContent = isRunning ? '⏸ Pause' : '▶ Resume';
        }});
        
        document.getElementById('reset-btn').addEventListener('click', () => {{
            initBoids();
        }});
        
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
        initBoids();
        requestAnimationFrame(animate);
        """
        
        return self.wrap_html(title, description, body, script=script)
