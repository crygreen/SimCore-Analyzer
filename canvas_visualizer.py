import pandas as pd
import json
import random

# 1. Load data from CSV
df = pd.read_csv('simcore_stats.csv')

# 2. Get the last day's data
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 3. Convert data to a JSON list for JavaScript
citizens_data = []
for index, row in final_state.iterrows():
    # Assign random starting positions
    x = random.randint(50, 750)
    y = random.randint(50, 550)
    
    # Assign random velocity for animation (vx and vy)
    vx = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
    vy = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
    
    citizen = {
        "name": row['Name'],
        "money": int(row['Money']),
        "mood": int(row['Mood']),
        "x": x,
        "y": y,
        "vx": vx,
        "vy": vy
    }
    citizens_data.append(citizen)

citizens_json = json.dumps(citizens_data)

# 4. Create the HTML template
html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SimCore City Map - Animated</title>
    <style>
        body {{
            background-color: #1e1e1e;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0;
            padding: 20px;
        }}
        h1 {{ color: #4CAF50; }}
        canvas {{
            background-color: #2a2a2a;
            border: 2px solid #555;
            border-radius: 10px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }}
    </style>
</head>
<body>
    <h1>SimCore City Map - Day {last_day}</h1>
    <canvas id="cityCanvas" width="800" height="600"></canvas>

    <script>
        const canvas = document.getElementById('cityCanvas');
        const ctx = canvas.getContext('2d');
        const citizens = {citizens_json};

        function getMoodColor(mood) {{
            if (mood > 70) return '#4CAF50'; // Green (Happy)
            if (mood > 40) return '#FF9800'; // Orange (Neutral)
            return '#F44336'; // Red (Sad)
        }}

        // --- ANIMATION LOGIC ---
        function updatePositions() {{
            citizens.forEach(c => {{
                // Move citizen
                c.x += c.vx;
                c.y += c.vy;

                // Bounce off walls (X-axis)
                if (c.x < 20 || c.x > canvas.width - 20) {{
                    c.vx *= -1;
                }}
                // Bounce off walls (Y-axis)
                if (c.y < 20 || c.y > canvas.height - 20) {{
                    c.vy *= -1;
                }}
            }});
        }}

        function drawCity() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            citizens.forEach(c => {{
                // Draw Citizen (Circle)
                ctx.beginPath();
                ctx.arc(c.x, c.y, 15, 0, 2 * Math.PI);
                ctx.fillStyle = getMoodColor(c.mood);
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Draw Name
                ctx.fillStyle = '#fff';
                ctx.font = '14px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(c.name, c.x, c.y - 25);
                
                // Draw Money
                ctx.fillStyle = '#ffd700';
                ctx.font = '12px Arial';
                ctx.fillText('$' + c.money, c.x, c.y + 30);
            }});
        }}

        // Main Animation Loop
        function animate() {{
            updatePositions(); // 1. Update coordinates
            drawCity();        // 2. Draw everything again
            requestAnimationFrame(animate); // 3. Loop this function 60 times/sec
        }}

        // Start the game
        animate();
    </script>
</body>
</html>
"""

# 5. Save the file
with open('city_map.html', 'w', encoding='utf-8') as file:
    file.write(html_template)

print("Animated visualization created! Open 'city_map.html' in your browser.")