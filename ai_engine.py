import pandas as pd
import ollama
import json
import random

# 1. Load latest data from CSV
df = pd.read_csv('simcore_stats.csv')
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 2. Pick two random citizens for a dialogue
citizens = final_state.sample(n=2).to_dict('records')
c1 = citizens[0]
c2 = citizens[1]

print(f"Generating AI dialogue between {c1['Name']} and {c2['Name']}...")

# 3. Create the prompt for the AI
prompt = f"""
You are the game master for a life simulation game.
Two characters just met on the street. Write a short, realistic 3-line dialogue based on their stats.

Character 1: {c1['Name']}
- Money: {c1['Money']} rubles
- Mood: {c1['Mood']}/100
- Music Skill: {c1['MusicSkill']}/100

Character 2: {c2['Name']}
- Money: {c2['Money']} rubles
- Mood: {c2['Mood']}/100
- Music Skill: {c2['MusicSkill']}/100

Rules:
1. Format: "Name: Text"
2. If one is rich and one is poor, they might argue or the rich one might brag.
3. At the very end, evaluate if their relationship improved or worsened. Output it as a number: "RelDelta: [number between -10 and +10]"
"""

# 4. Send request to local LLM (Ollama)
try:
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
    dialogue = response['message']['content']
    
    print("\n--- AI DIALOGUE ---")
    print(dialogue)
    print("-------------------")
    
    # 5. Save to JSON for the visualizer
    dialogue_data = {
        "c1": c1['Name'],
        "c2": c2['Name'],
        "text": dialogue
    }
    with open('dialogs.json', 'w', encoding='utf-8') as f:
        json.dump(dialogue_data, f, ensure_ascii=False)
        
except Exception as e:
    print(f"Error connecting to Ollama: {e}")
    print("Make sure Ollama is running in the background.")