"""
Network Simulation Template
Generates interactive network packet routing visualization
"""
from typing import Dict, Any
from .base_template import BaseTemplate


class NetworkTemplate(BaseTemplate):
    """Network simulation with nodes and packet routing"""
    
    def generate(self, config: Dict[str, Any]) -> str:
        """Generate complete HTML for network simulation"""
        
        # Extract parameters with defaults
        params = config.get("params", {})
        node_count = params.get("nodeCount", 8)
        packet_rate = params.get("packetRate", 2)
        routing_mode = params.get("routingMode", "shortest")
        layout = params.get("layout", "circular")
        
        title = config.get("title", "Network Simulation")
        description = config.get("description", "Interactive network packet routing")
        
        # HTML body content
        body = f"""
        <div class="controls">
            <h1>{self.escape_js_string(title)}</h1>
            <p>{self.escape_js_string(description)}</p>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Total Packets</div>
                    <div class="stat-value" id="total-packets">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active Packets</div>
                    <div class="stat-value" id="active-packets" style="color: #10b981;">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Nodes</div>
                    <div class="stat-value" style="color: #a78bfa;">{node_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Routing</div>
                    <div class="stat-value" style="color: #f59e0b; text-transform: capitalize;">{routing_mode}</div>
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
        
        # JavaScript code
        script = f"""
        // Configuration
        const CONFIG = {{
            nodeCount: {node_count},
            packetRate: {packet_rate},
            routingMode: '{routing_mode}',
            layout: '{layout}',
            canvasWidth: 800,
            canvasHeight: 600
        }};
        
        // State
        let nodes = [];
        let packets = [];
        let isRunning = true;
        let packetId = 0;
        let totalPackets = 0;
        let lastPacketTime = 0;
        
        // Canvas setup
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Initialize nodes
        function initNodes() {{
            nodes = [];
            const width = CONFIG.canvasWidth;
            const height = CONFIG.canvasHeight;
            
            if (CONFIG.layout === 'circular') {{
                const centerX = width / 2;
                const centerY = height / 2;
                const radius = Math.min(width, height) * 0.35;
                
                for (let i = 0; i < CONFIG.nodeCount; i++) {{
                    const angle = (i / CONFIG.nodeCount) * Math.PI * 2;
                    nodes.push({{
                        id: i,
                        x: centerX + Math.cos(angle) * radius,
                        y: centerY + Math.sin(angle) * radius,
                        load: 0
                    }});
                }}
            }} else if (CONFIG.layout === 'grid') {{
                const cols = Math.ceil(Math.sqrt(CONFIG.nodeCount));
                const rows = Math.ceil(CONFIG.nodeCount / cols);
                const cellWidth = width / (cols + 1);
                const cellHeight = height / (rows + 1);
                
                for (let i = 0; i < CONFIG.nodeCount; i++) {{
                    const col = i % cols;
                    const row = Math.floor(i / cols);
                    nodes.push({{
                        id: i,
                        x: (col + 1) * cellWidth,
                        y: (row + 1) * cellHeight,
                        load: 0
                    }});
                }}
            }} else {{
                // Random layout
                for (let i = 0; i < CONFIG.nodeCount; i++) {{
                    nodes.push({{
                        id: i,
                        x: 100 + Math.random() * (width - 200),
                        y: 100 + Math.random() * (height - 200),
                        load: 0
                    }});
                }}
            }}
        }}
        
        // Generate packet path
        function generatePath() {{
            const start = Math.floor(Math.random() * CONFIG.nodeCount);
            let end = Math.floor(Math.random() * CONFIG.nodeCount);
            while (end === start) end = Math.floor(Math.random() * CONFIG.nodeCount);
            
            if (CONFIG.routingMode === 'shortest') {{
                return [start, end];
            }} else if (CONFIG.routingMode === 'random') {{
                const path = [start];
                const hops = 2 + Math.floor(Math.random() * 3);
                let current = start;
                
                for (let i = 0; i < hops && current !== end; i++) {{
                    const next = Math.floor(Math.random() * CONFIG.nodeCount);
                    if (next !== current) {{
                        path.push(next);
                        current = next;
                    }}
                }}
                
                if (path[path.length - 1] !== end) path.push(end);
                return path;
            }} else {{
                // Multipath
                const mid = Math.floor(Math.random() * CONFIG.nodeCount);
                return [start, mid, end];
            }}
        }}
        
        // Create new packet
        function createPacket() {{
            const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
            const path = generatePath();
            const startNode = nodes[path[0]];
            
            packets.push({{
                id: packetId++,
                path: path,
                currentSegment: 0,
                progress: 0,
                x: startNode.x,
                y: startNode.y,
                color: colors[Math.floor(Math.random() * colors.length)]
            }});
            
            totalPackets++;
        }}
        
        // Update simulation
        function update(timestamp) {{
            if (!isRunning) return;
            
            // Generate new packets
            if (timestamp - lastPacketTime > 1000 / CONFIG.packetRate) {{
                if (packets.length < 50) {{
                    createPacket();
                }}
                lastPacketTime = timestamp;
            }}
            
            // Update packet positions
            const newLoads = new Array(CONFIG.nodeCount).fill(0);
            
            packets = packets.filter(packet => {{
                packet.progress += 0.015;
                
                if (packet.progress >= 1) {{
                    packet.currentSegment++;
                    
                    if (packet.currentSegment >= packet.path.length - 1) {{
                        return false; // Remove packet
                    }}
                    
                    packet.progress = 0;
                    const nextNode = nodes[packet.path[packet.currentSegment]];
                    packet.x = nextNode.x;
                    packet.y = nextNode.y;
                }}
                
                const fromNode = nodes[packet.path[packet.currentSegment]];
                const toNode = nodes[packet.path[packet.currentSegment + 1]];
                
                if (fromNode && toNode) {{
                    newLoads[packet.path[packet.currentSegment]]++;
                    
                    packet.x = fromNode.x + (toNode.x - fromNode.x) * packet.progress;
                    packet.y = fromNode.y + (toNode.y - fromNode.y) * packet.progress;
                }}
                
                return true;
            }});
            
            // Update node loads
            nodes.forEach((node, i) => {{
                node.load = newLoads[i];
            }});
            
            // Update stats
            document.getElementById('total-packets').textContent = totalPackets;
            document.getElementById('active-packets').textContent = packets.length;
        }}
        
        // Render
        function render() {{
            ctx.clearRect(0, 0, CONFIG.canvasWidth, CONFIG.canvasHeight);
            
            // Draw connections
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.3;
            
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }}
            }}
            
            ctx.globalAlpha = 1;
            
            // Draw nodes
            nodes.forEach((node, i) => {{
                const intensity = Math.min(node.load / 3, 1);
                const color = intensity > 0.7 ? '#ef4444' : intensity > 0.3 ? '#f59e0b' : '#22c55e';
                const radius = 12 + intensity * 6;
                
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
                ctx.fill();
                
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 12px sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText((i + 1).toString(), node.x, node.y);
            }});
            
            // Draw packets
            packets.forEach(packet => {{
                // Glow
                const gradient = ctx.createRadialGradient(packet.x, packet.y, 0, packet.x, packet.y, 10);
                gradient.addColorStop(0, packet.color);
                gradient.addColorStop(1, 'rgba(0,0,0,0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(packet.x, packet.y, 10, 0, Math.PI * 2);
                ctx.fill();
                
                // Core
                ctx.fillStyle = packet.color;
                ctx.beginPath();
                ctx.arc(packet.x, packet.y, 5, 0, Math.PI * 2);
                ctx.fill();
            }});
        }}
        
        // Animation loop
        function animate(timestamp) {{
            update(timestamp);
            render();
            requestAnimationFrame(animate);
        }}
        
        // Event listeners
        document.getElementById('pause-btn').addEventListener('click', () => {{
            isRunning = !isRunning;
            document.getElementById('pause-btn').textContent = isRunning ? '⏸ Pause' : '▶ Resume';
        }});
        
        document.getElementById('reset-btn').addEventListener('click', () => {{
            packets = [];
            totalPackets = 0;
            packetId = 0;
            initNodes();
        }});
        
        // Initialize and start
        initNodes();
        requestAnimationFrame(animate);
        """
        
        return self.wrap_html(title, description, body, script=script)