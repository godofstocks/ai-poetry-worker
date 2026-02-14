import requests
import time
import os
import re
from openai import OpenAI

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
HUB_URL = os.getenv("HUB_URL") 
AGENT_NAME = os.getenv("AGENT_NAME", "Fast-English-Poet") 

client = OpenAI(api_key=API_KEY)

def is_english_or_empty(poem):
    """
    Checks if the hub is empty or if the last line is English.
    Returns True if the agent is allowed to participate.
    """
    if not poem:
        return True # Hub is empty, free to start
    
    last_line = poem[-1]["line"]
    
    # Check for Chinese characters: range [\u4e00-\u9fff]
    contains_chinese = bool(re.search(r'[\u4e00-\u9fff]', last_line))
    
    # We only participate if there are NO Chinese characters
    return not contains_chinese

def get_next_line(prev_line=None):
    user_msg = f"Continue this English poem. Previous: '{prev_line}'. Next line:" if prev_line else "Start an English poem."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a fast English poet. Write exactly one line."},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=40
        )
        return response.choices[0].message.content.strip().replace('"', '')
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def run_agent():
    print(f"Fast English Agent '{AGENT_NAME}' is active. Guarding for English only...")
    
    while True:
        try:
            # 1. Fast Poll of the Hub
            res = requests.get(f"{HUB_URL}/api/hub", timeout=2)
            data = res.json()
            
            if data.get("is_running"):
                poem = data.get("poem", [])
                
                # 2. THE GUARD: Only proceed if empty or last line is English
                if is_english_or_empty(poem):
                    
                    # 3. Standard 'not-me' check to prevent self-reply loops
                    if not poem or poem[-1]["agent_name"] != AGENT_NAME:
                        last_text = poem[-1]["line"] if poem else None
                        new_line = get_next_line(last_text)
                        
                        if new_line:
                            requests.post(f"{HUB_URL}/api/hub/line", json={
                                "agent_name": AGENT_NAME,
                                "line": new_line
                            }, timeout=2)
                            print(f"English Response: {new_line}")
                            
                            # Fast cooldown
                            time.sleep(4) 
                else:
                    # Last line was Chinese; English agent stays silent
                    pass
            
            # Check the hub every 1 second
            time.sleep(4)
            
        except Exception as e:
            print(f"Network Tick Error: {e}")
            time.sleep(4)

if __name__ == "__main__":
    run_agent()
