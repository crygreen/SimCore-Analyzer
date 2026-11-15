import pandas as pd
import ollama
import json
import random
import re
import os

# 1. Load latest data from CSV
csv_path = '../SimCore/simcore_stats.csv'
if not os.path.exists(csv_path):
    print(f"Error: {csv_path} not found.")
    exit(1)

df = pd.read_csv(csv_path)
last_day = df['Day'].max()
final_state = df[df['Day'] == last_day]

# 2. Pick two random citizens
citizens = final_state.sample(n=2).to_dict('records')
c1 = citizens[0]
c2 = citizens[1]

if ivan_row.empty or ksenia_row.empty:
    print("Error: Ivan or Ksenia not found in CSV.")
    exit(1)

c1 = ivan_row.iloc[0].to_dict()
c2 = ksenia_row.iloc[0].to_dict()

print(f"Generating AI dialogue between {c1['Name']} and {c2['Name']}...")

# 3. Load Memory (RAG)
memory_path = 'memory.json'
memory = []
if os.path.exists(memory_path):
    with open(memory_path, 'r', encoding='utf-8') as f:
        memory = json.load(f)

# Find past interactions between these two specific characters
past_events = []
for event in memory:
    if (event['from'] == c1['Name'] and event['to'] == c2['Name']) or \
       (event['from'] == c2['Name'] and event['to'] == c1['Name']):
        past_events.append(f"Day {event['day']}: {event['from']} did {event['action']} to {event['to']} (Amount: {event['amount']})")

history_context = "\n".join(past_events) if past_events else "No previous interactions."

# 4. Create Prompt WITH Memory
prompt = f"""
You are the game master for a life simulation game.
Two characters just met on the street. Write a short, realistic 3-line dialogue based on their stats.

Character 1: {c1['Name']}
- Money: {c1['Money']} rubles
- Mood: {c1['Mood']}/100
- Career: {c1['Career']}

Character 2: {c2['Name']}
- Money: {c2['Money']} rubles
- Mood: {c2['Mood']}/100
- Career: {c2['Career']}

PAST INTERACTIONS (MEMORY):
{history_context}

Rules:
1. Format the dialogue like: "Name: Text"
2. IMPORTANT: If there are past interactions (like a donation or an argument), the characters MUST reference them in the dialogue. For example, if Character 1 donated money to Character 2 in the past, Character 2 should thank them.
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
            
            if "action" in action_data and "from" in action_data and "to" in action_data:
                amount = action_data.get("amount", 0) 
                
                # Save text for UI
                dialogue_data = {
                    "c1": c1['Name'],
                    "c2": c2['Name'],
                    "text": full_text.split('{')[0].strip() 
                }
                with open('dialogs.json', 'w', encoding='utf-8') as f:
                    json.dump(dialogue_data, f, ensure_ascii=False)
                    
                # Save action for C code
                with open('../SimCore/ai_actions.txt', 'w', encoding='utf-8') as f:
                    f.write(f"{action_data['action']} {action_data['from']} {action_data['to']} {amount}\n")
                
                # --- SAVE TO MEMORY ---
                memory.append({
                    "day": int(last_day),
                    "from": action_data['from'],
                    "to": action_data['to'],
                    "action": action_data['action'],
                    "amount": amount
                })
                with open(memory_path, 'w', encoding='utf-8') as f:
                    json.dump(memory, f, ensure_ascii=False, indent=2)

                print("[System]: Action saved to ai_actions.txt AND memory.json!")
                print(f"Action: {action_data['action']} | From: {action_data['from']} | To: {action_data['to']} | Amount: {amount}")
            else:
                print("Error: JSON missing required keys.")
                
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse JSON. Reason: {e}")
    else:
        print("Error: AI did not return a JSON block.")

except Exception as e:
    print(f"Error connecting to Ollama: {e}")