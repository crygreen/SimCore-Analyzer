import ollama
import os

# 1. Define the prompt for the AI
prompt = """
You are a game designer creating a job and hobby list for a life simulation game.
Generate exactly 20 professions and 10 hobbies.

Format each line EXACTLY like this, with no extra text, no markdown formatting, and no spaces after commas:
Name,HourlyPay,HoursPerDay,StressLevel

Example:
Engineer,500,8,10
Hobby_Gaming,0,3,0

Rules:
- HourlyPay must be between 200 and 800 for jobs, and exactly 0 for hobbies.
- HoursPerDay must be between 6 and 12 for jobs, and 1 to 4 for hobbies.
- StressLevel must be between 5 and 30.
- Make the names interesting (e.g., CyberSecurity, Hobby_Parkour, DataScientist, Hobby_Photography).
"""

print("Asking AI to generate world content... (This may take 20-30 seconds)")

try:
    # 2. Get response from Ollama
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
    raw_text = response['message']['content']
    
    # 3. Clean up the text
    lines = raw_text.strip().split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('```'):
            continue
        if line.count(',') == 3:
            clean_lines.append(line)
            
    # 4. Save to the C project folder
    output_path = '../SimCore/professions.txt'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in clean_lines:
            f.write(line + '\n')
            
    print(f"\n[System]: Successfully generated {len(clean_lines)} professions/hobbies!")
    print(f"Saved to: {output_path}")

except Exception as e:
    print(f"Error connecting to Ollama: {e}")