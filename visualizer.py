import pandas as pd

# 1. Load data from CSV
df = pd.read_csv('simcore_stats.csv')

# 2. Get the last day's data to visualize the final state
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 3. Start building the HTML string
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SimCore City Visualizer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1e1e1e;
            color: #ffffff;
            text-align: center;
            padding: 20px;
        }
        h1 { color: #4CAF50; }
        .city-grid {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-top: 30px;
        }
        .citizen-card {
            border: 2px solid #333;
            border-radius: 10px;
            padding: 15px;
            width: 150px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        .citizen-card:hover { transform: scale(1.05); }
        .name { font-size: 1.2em; font-weight: bold; margin-bottom: 5px; }
        .stat { font-size: 0.9em; margin: 2px 0; }
    </style>
</head>
<body>
    <h1>SimCore City Visualizer</h1>
    <h2>Day {day}</h2>
    <div class="city-grid">
""".replace("{day}", str(last_day))

# 4. Generate a card for each citizen
for index, row in final_state.iterrows():
    # Determine color based on mood (Green for happy, Red for sad)
    mood = row['Mood']
    if mood > 70:
        bg_color = "#2e7d32"  # Green
    elif mood > 40:
        bg_color = "#f57c00"  # Orange
    else:
        bg_color = "#c62828"  # Red
        
    citizen_html = f"""
        <div class="citizen-card" style="background-color: {bg_color};">
            <div class="name">{row['Name']}</div>
            <div class="stat">💰 Money: {row['Money']}</div>
            <div class="stat">❤️ Health: {row['Health']}</div>
            <div class="stat">😊 Mood: {row['Mood']}</div>
            <div class="stat">🎵 Skill: {row['MusicSkill']}</div>
        </div>
    """
    html_content += citizen_html

# 5. Close the HTML tags
html_content += """
    </div>
</body>
</html>
"""

# 6. Save the HTML file
with open('city_visualization.html', 'w', encoding='utf-8') as file:
    file.write(html_content)

print("Visualization created! Open 'city_visualization.html' in your browser.")