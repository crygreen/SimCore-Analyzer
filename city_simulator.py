import pandas as pd
import json
import os

# 1. Load data from CSV
df = pd.read_csv('simcore_stats.csv')
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 2. Load AI dialogue (if exists)
dialog_data = None
if os.path.exists('dialogs.json'):
    with open('dialogs.json', 'r', encoding='utf-8') as f:
        dialog_data = json.load(f)

# 3. Prepare Citizen Data
citizens_data = []
for index, row in final_state.iterrows():
    citizen = {
        "name": row['Name'],
        "money": int(row['Money']),
        "health": int(row['Health']),
        "mood": int(row['Mood']),
        "skill": int(row['MusicSkill']),
        "x": int(row['X']), 
        "y": int(row['Y'])
    }
    citizens_data.append(citizen)

citizens_json = json.dumps(citizens_data)
dialog_json = json.dumps(dialog_data) if dialog_data else "null"

# 4. Create the HTML
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SimCore City</title>
    <style>
        body {{ background-color: #121212; color: white; font-family: Arial; display: flex; height: 100vh; margin: 0; overflow: hidden; }}
        .sidebar {{ width: 300px; background-color: #1e1e1e; padding: 20px; border-right: 2px solid #333; overflow-y: auto; }}
        .card {{ background-color: #2a2a2a; border-radius: 8px; padding: 10px; margin-bottom: 10px; border-left: 5px solid #555; }}
        .map-area {{ flex-grow: 1; display: flex; justify-content: center; align-items: center; position: relative; }}
        canvas {{ background-color: #1a1a1a; border: 2px solid #333; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        
        /* AI DIALOGUE BOX */
        .dialog-box {{
            position: absolute;
            bottom: 30px;
            background: #2a2a2a;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 20px;
            max-width: 600px;
            width: 80%;
            display: { 'block' if dialog_data else 'none' };
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
            z-index: 10;
        }}
        .dialog-box h3 {{ margin-top: 0; color: #4CAF50; }}
        .dialog-box pre {{ margin: 0; color: #ddd; font-family: monospace; white-space: pre-wrap; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>SimCore Day {last_day}</h2>
        <div id="stats-container"></div>
    </div>
    <div class="map-area">
        <canvas id="cityCanvas" width="900" height="700"></canvas>
        
        <!-- DIALOGUE OVERLAY -->
        <div class="dialog-box">
            <h3>🤖 AI Event: Street Encounter</h3>
            <pre id="dialog-text"></pre>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('cityCanvas');
        const ctx = canvas.getContext('2d');
        const citizens = {citizens_json};
        const dialogData = {dialog_json};

        // Build Sidebar
        const statsContainer = document.getElementById('stats-container');
        citizens.forEach(c => {{
            let color = c.mood > 70 ? '#4CAF50' : (c.mood > 40 ? '#FF9800' : '#F44336');
            statsContainer.innerHTML += `<div class="card" style="border-left-color: ${{color}}"><b>${{c.name}}</b><br>💰 ${{c.money}} | ❤️ ${{c.health}}</div>`;
        }});

        // Show Dialogue text
        if (dialogData) {{
            document.getElementById('dialog-text').innerText = dialogData.text;
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw Environment
            ctx.strokeStyle = '#333'; ctx.lineWidth = 30;
            ctx.beginPath(); ctx.moveTo(0, 350); ctx.lineTo(900, 350); ctx.moveTo(450, 0); ctx.lineTo(450, 700); ctx.stroke();
            
            // Draw Houses and Workplaces
            ctx.fillStyle = '#1E90FF';
            [[100, 100], [200, 100], [300, 100], [100, 500], [200, 500], [300, 500]].forEach(h => ctx.fillRect(h[0]-20, h[1]-20, 40, 40));
            ctx.fillStyle = '#8A2BE2';
            [[600, 200], [600, 400]].forEach(w => ctx.fillRect(w[0]-30, w[1]-30, 60, 60));
            
            // Draw Citizens
            citizens.forEach(c => {{
                // Determine color safely
                let circleColor = '#FFFFFF';
                if (c.mood !== undefined) {{
                    if (c.mood > 70) circleColor = '#4CAF50';
                    else if (c.mood > 40) circleColor = '#FF9800';
                    else circleColor = '#F44336';
                }}

                // Draw Body
                ctx.beginPath(); 
                ctx.arc(c.x, c.y, 15, 0, 2 * Math.PI);
                ctx.fillStyle = circleColor;
                ctx.fill(); 
                ctx.strokeStyle = '#fff'; 
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Draw Name (with black outline for readability)
                ctx.font = 'bold 14px Arial'; 
                ctx.textAlign = 'center';
                
                // Text outline
                ctx.strokeStyle = '#000';
                ctx.lineWidth = 4;
                ctx.strokeText(c.name, c.x, c.y - 22);
                
                // Text fill
                ctx.fillStyle = '#fff'; 
                ctx.fillText(c.name, c.x, c.y - 22);
            }});
        }}
        draw();
    </script>
</body>
</html>
"""

with open('city_simulator.html', 'w', encoding='utf-8') as file:
    file.write(html_template)
print("Visualizer updated with fixed colors and text outlines.")