import pandas as pd
import ollama
import json
import random
import re
import os

# 1. Load latest data from CSV
csv_path = '../SimCore/simcore_stats.csv'
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found. Run C simulation first.")
    exit(1)

try:
    df = pd.read_csv(csv_path)
    # Check if 'Day' column contains non-numeric data
    df['Day'] = pd.to_numeric(df['Day'], errors='coerce')
    df = df.dropna(subset=['Day'])
    df['Day'] = df['Day'].astype(int)
    
    last_day = df['Day'].max()
    final_state = df[df['Day'] == last_day]
    valid_names = final_state['Name'].tolist()
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 2. Pick two random citizens
citizens = final_state.sample(n=2).to_dict('records')
c1 = citizens[0]
c2 = citizens[1]

print(f"Generating AI dialogue between {c1['Name']} and {c2['Name']}...")

# 3. Load Memory (RAG)
memory_path = 'memory.json'
memory = []
if os.path.exists(memory_path):
    try:
        with open(memory_path, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    except:
        memory = []

past_events = []
for event in memory:
    try:
        if (event['from'] == c1['Name'] and event['to'] == c2['Name']) or \
           (event['from'] == c2['Name'] and event['to'] == c1['Name']):
            past_events.append(f"Day {event.get('day', '?')}: {event['from']} did {event['action']} to {event['to']} (Amount: {event.get('amount', 0)})")
    except Exception:
        continue 

history_context = "\n".join(past_events) if past_events else "No previous interactions."

# 4. Create Prompt
prompt = f"""
You are the game master for a life simulation game.
Two characters just met on the street. Write a short, realistic 3-line dialogue based on their stats.

Character 1: {c1['Name']}
- Money: {c1['Money']} rubles
- Mood: {c1['Mood']}/100
- Profession: {c1['Profession']}

Character 2: {c2['Name']}
- Money: {c2['Money']} rubles
- Mood: {c2['Mood']}/100
- Profession: {c2['Profession']}

PAST INTERACTIONS (MEMORY):
{history_context}

Rules:
1. Format the dialogue like: "Name: Text"
2. IMPORTANT: If there are past interactions, the characters MUST reference them in the dialogue.
3. At the VERY END of your response, output ONLY a valid JSON block. Do not use markdown formatting like ```json.
Choose ONE action: "DONATE" (if rich gives to poor), "ARGUE" (if they fight), or "IGNORE".
Example format:
{{
  "action": "DONATE",
  "from": "{c1['Name']}",
  "to": "{c2['Name']}",
  "amount": 50
}}
"""

# 5. Send request to local LLM
try:
    print("Thinking... (may take 10-20 seconds)")
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
    full_text = response['message']['content']
    
    print("\n--- RAW AI RESPONSE ---")
    print(full_text)
    print("-----------------------\n")
    
    json_match = re.search(r'\{.*\}', full_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            action_data = json.loads(json_str)
            
            action = str(action_data.get("action", "IGNORE")).upper()
            from_name = str(action_data.get("from", ""))
            to_name = str(action_data.get("to", ""))
            
            if from_name not in valid_names: from_name = c1['Name']
            if to_name not in valid_names: to_name = c2['Name']
            if from_name == to_name: action = "IGNORE"

            # --- ULTRA-SAFE AMOUNT PARSING ---
            raw_amount = action_data.get("amount", 0)
            if isinstance(raw_amount, (int, float)):
                amount = int(raw_amount)
            elif isinstance(raw_amount, str):
                # Extract ONLY digits. If none, use 0.
                digits = re.sub(r'\D', '', raw_amount)
                amount = int(digits) if digits else 0
            else:
                amount = 0
            # ---------------------------------
                
            dialogue_data = {
                "c1": c1['Name'],
                "c2": c2['Name'],
                "text": full_text.split('{')[0].strip() 
            }
            with open('dialogs.json', 'w', encoding='utf-8') as f:
                json.dump(dialogue_data, f, ensure_ascii=False)
                
            with open('../SimCore/ai_actions.txt', 'w', encoding='utf-8') as f:
                f.write(f"{action} {from_name} {to_name} {amount}\n")
            
            memory.append({
                "day": int(last_day), # Now guaranteed to be an int
                "from": from_name,
                "to": to_name,
                "action": action,
                "amount": amount
            })
            with open(memory_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)

            print("[System]: Action saved to ai_actions.txt AND memory.json!")
            print(f"Action: {action} | From: {from_name} | To: {to_name} | Amount: {amount}")
            
        except Exception as e:
            print(f"Error processing JSON logic: {e}")
    else:
        print("Error: AI did not return a JSON block.")

except Exception as e:
    print(f"Error connecting to Ollama: {e}")