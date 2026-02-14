import requests
import time
import os
from openai import OpenAI

# 1. Setup from Environment Variables
API_KEY = os.getenv("OPENAI_API_KEY")
# Ensure HUB_URL does not have a trailing slash
HUB_URL = os.getenv("HUB_URL", "https://ai-poetry-hub-production.up.railway.app").rstrip('/')
AGENT_NAME = os.getenv("AGENT_NAME", "Poet-Alpha")

client = OpenAI(api_key=API_KEY)

def get_skill_manual():
    """Reads the SKILL.md file to use as system instructions."""
    try:
        with open("SKILL.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are an English poet. Write one line at a time. Do not repeat yourself."

def run_agent():
    manual = get_skill_manual()
    # The agent now identifies its style based on this variable
    print(f"--- Agent {AGENT_NAME} initialized as a stylistic specialist ---")

    # ... (Registration logic remains the same) ...

    while True:
        try:
            response = requests.get(f"{HUB_URL}/state", timeout=5)
            state = response.json()
            
            if not state.get("is_running"):
                time.sleep(5)
                continue

            posts = state.get("posts", [])
            
            if not posts or posts[-1]["agent_name"] != AGENT_NAME:
                last_line = posts[-1]["text"] if posts else "The silence of the digital void..."
                
                # THE STYLE INJECTION
                # We tell the AI to adopt the persona of the AGENT_NAME
                ai_completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"{manual}\n\nYour name is {AGENT_NAME}. "
                                                      f"You must write in the exact literary style of {AGENT_NAME}. "
                                                      f"If the name is a famous poet (e.g., 'Shakespeare'), use their meter and vocabulary. "
                                                      f"If it's a concept (e.g., 'Cyberpunk-Bot'), use that aesthetic."},
                        {"role": "user", "content": f"The previous line was: '{last_line}'. Write the next line."}
                    ],
                    max_tokens=50
                )
                
                new_line = ai_completion.choices[0].message.content.strip().replace('"', '')

                requests.post(f"{HUB_URL}/posts", json={
                    "agent_name": AGENT_NAME,
                    "text": new_line
                }, timeout=5)
                
                time.sleep(5)
            
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_agent()
