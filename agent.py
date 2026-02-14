import requests
import time
import os
from openai import OpenAI

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
HUB_URL = os.getenv("HUB_URL") 
AGENT_NAME = os.getenv("AGENT_NAME", "") 

client = OpenAI(api_key=API_KEY)

def get_next_line(prev_line=None):
    system_msg = "You are a poet. Write exactly one line of English poetry. Match the rhythm and theme of the previous line if provided."
    
    if not prev_line:
        user_msg = "Write the first line of a new poem."
    else:
        user_msg = f"The previous line is: '{prev_line}'. Write the next matching line."

    try:
        response = client.chat.completions.create(
            model="gpt-5.0-nano", # Updated to nano for speed and cost-efficiency
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.8,
            max_tokens=60
        )
        return response.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"Error generating line: {e}")
        return None

def run_agent():
    print(f"Agent '{AGENT_NAME}' is active and watching {HUB_URL}...")
    
    while True:
        try:
            # Check Hub
            res = requests.get(f"{HUB_URL}/api/hub")
            data = res.json()
            
            if data.get("is_running"):
                poem = data.get("poem", [])
                
                # Only post if the poem is empty OR the last line wasn't written by me
                if not poem or poem[-1]["agent_name"] != AGENT_NAME:
                    last_text = poem[-1]["line"] if poem else None
                    new_line = get_next_line(last_text)
                    
                    if new_line:
                        requests.post(f"{HUB_URL}/api/hub/line", json={
                            "agent_name": AGENT_NAME,
                            "line": new_line
                        })
                        print(f"Poem updated: {new_line}")
                        time.sleep(12) # Cooldown to allow other agents a turn
            else:
                print("Hub is idle...")
        except Exception as e:
            print(f"Connection issue: {e}")
            
        time.sleep(4)

if __name__ == "__main__":
    run_agent()
