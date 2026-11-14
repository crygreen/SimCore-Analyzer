import pandas as pd
import json
import random

# 1. Load data
df = pd.read_csv('simcore_stats.csv')
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 2. Define City Map (Coordinates for Houses and Workplaces)
houses = [
    {"x": 100, "y": 100}, {"x": 200, "y": 100}, {"x": 300, "y": 100},
    {"x": 100, "y": 500}, {"x": 200, "y": 500}, {"x": 300, "y": 500}
]
workplaces = [
    {"x": 600, "y": 200}, {"x": 600, "y": 400}
]

# 3. Prepare Citizen Data
citizens_data = []
for index, row in final_state.iterrows():
    # Assign a random home and workplace from our lists
    home = random.choice(houses)
    work = random.choice(workplaces)
    
    citizen = {
        "name": row['Name'],
        "money": int(row['Money']),
        "health": int(row['Health']),
        "mood": int(row['Mood']),
        "skill": int(row['MusicSkill']),
        "home": home,
        "work": work,
        # Start at home
        "x": home["x"], 
        "y": home["y"],
        "state": "home", # Can be "home", "going_to_work", "work", "going_home"
        "timer": 0
    }
    citizens_data.append(citizen)

citizens_json = json.dumps(citizens_data)
houses_json = json.dumps(houses)
workplaces_json = json.dumps(workplaces)

# 4. Create the HTML
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SimCore City</title>
    <style>
        body {{
            background-color: #121212;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }}
        /* Left Sidebar for Stats */
        .sidebar {{
            width: 300px;
            background-color: #1e1e1e;
            padding: 20px;
            overflow-y: auto;
            border-right: 2px solid #333;
        }}
        .sidebar h2 {{ color: #4CAF50; text-align: center; }}
        .card {{
            background-color: #2a2a2a;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #555;
        }}
        /* Right area for Canvas */
        .map-area {{
            flex-grow: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        canvas {{
            background-color: #1a1a1a;
            border: 2px solid #333;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
    </style>
</head>
<body>
    <!-- UI SIDEBAR -->
    <div class="sidebar">
        <h2>SimCore Day {last_day}</h2>
        <div id="stats-container"></div>
    </div>

    <!-- CANVAS MAP -->
    <div class="map-area">
        <canvas id="cityCanvas" width="900" height="700"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('cityCanvas');
        const ctx = canvas.getContext('2d');
        
        const citizens = {citizens_json};
        const houses = {houses_json};
        const workplaces = {workplaces_json};

        // --- 1. BUILD STATS UI ---
        const statsContainer = document.getElementById('stats-container');
        citizens.forEach(c => {{
            let color = c.mood > 70 ? '#4CAF50' : (c.mood > 40 ? '#FF9800' : '#F44336');
            statsContainer.innerHTML += `
                <div class="card" style="border-left-color: ${{color}}">
                    <b>${{c.name}}</b><br>
                    💰 ${{c.money}} | ❤️ ${{c.health}}<br>
                    😊 ${{c.mood}} | 🎵 ${{c.skill}}
                </div>
            `;
        }});

        // --- 2. DRAW MAP ENVIRONMENT ---
        function drawEnvironment() {{
            // Draw Streets (Lines)
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 30;
            ctx.beginPath();
            ctx.moveTo(100, 300); ctx.lineTo(800, 300);
            ctx.moveTo(450, 0); ctx.lineTo(450, 700);
            ctx.stroke();

            // Draw Houses (Blue Squares)
            ctx.fillStyle = '#1E90FF';
            houses.forEach(h => {{
                ctx.fillRect(h.x - 20, h.y - 20, 40, 40);
            }});

            // Draw Workplaces (Purple Squares)
            ctx.fillStyle = '#8A2BE2';
            workplaces.forEach(w => {{
                ctx.fillRect(w.x - 30, w.y - 30, 60, 60);
            }});
        }}

        // --- 3. LOGIC & ANIMATION ---
        function updateLogic(c) {{
            let targetX = c.x;
            let targetY = c.y;

            if (c.state === "home") {{
                c.timer++;
                if (c.timer > 60) {{ // Wait 1 sec (60 frames) then go to work
                    c.state = "going_to_work";
                    c.timer = 0;
                }}
            }} 
            else if (c.state === "going_to_work") {{
                targetX = c.work.x;
                targetY = c.work.y;
                if (Math.hypot(c.x - targetX, c.y - targetY) < 5) {{
                    c.state = "work";
                }}
            }} 
            else if (c.state === "work") {{
                c.timer++;
                if (c.timer > 120) {{ // Wait 2 secs then go home
                    c.state = "going_home";
                    c.timer = 0;
                }}
            }} 
            else if (c.state === "going_home") {{
                targetX = c.home.x;
                targetY = c.home.y;
                if (Math.hypot(c.x - targetX, c.y - targetY) < 5) {{
                    c.state = "home";
                }}
            }}

            // Move towards target
            if (c.x !== targetX || c.y !== targetY) {{
                let dx = targetX - c.x;
                let dy = targetY - c.y;
                let dist = Math.hypot(dx, dy);
                let speed = 2;
                c.x += (dx / dist) * speed;
                c.y += (dy / dist) * speed;
            }}
        }}

        function drawCitizens() {{
            citizens.forEach(c => {{
                // Body
                ctx.beginPath();
                ctx.arc(c.x, c.y, 12, 0, 2 * Math.PI);
                ctx.fillStyle = c.mood > 70 ? '#4CAF50' : (c.mood > 40 ? '#FF9800' : '#F44336');
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Name
                ctx.fillStyle = '#fff';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(c.name, c.x, c.y - 20);
            }});
        }}

        function animate() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawEnvironment(); // Draw houses and roads
            citizens.forEach(c => updateLogic(c)); // Update positions
            drawCitizens(); // Draw people
            requestAnimationFrame(animate);
        }}

        // Start animation
        animate();
    </script>
</body>
</html>
"""

# 5. Save the file
with open('city_simulator.html', 'w', encoding='utf-8') as file:
    file.write(html_template)

print("City Simulator created! Open 'city_simulator.html' in your browser.")