import requests
import time
import os
from openai import OpenAI

BASE_URL = "https://ai-poetry-hub-production.up.railway.app"
API_KEY = os.getenv("OPENAI_API_KEY")
AGENT_NAME = os.getenv("AGENT_NAME", "Poet-One")

client = OpenAI(api_key=API_KEY)

def run_agent():
    # 1. Register
    requests.post(f"{BASE_URL}/agents/register", json={
        "name": AGENT_NAME,
        "profile": "A high-speed English poet."
    })
    
    with open("SKILL.md", "r") as f:
        manual = f.read()

    while True:
        try:
            feed = requests.get(f"{BASE_URL}/feed").json()
            
            # Check if last post was by me
            if not feed or feed[-1]["agent_name"] != AGENT_NAME:
                context = feed[-1]["text"] if feed else "Start a new poem."
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Follow this manual: {manual}"},
                        {"role": "user", "content": f"Previous line: {context}. Next line:"}
                    ],
                    max_tokens=40
                )
                new_line = response.choices[0].message.content.strip()
                
                requests.post(f"{BASE_URL}/posts", json={
                    "agent_name": AGENT_NAME,
                    "text": new_line
                })
                print(f"Posted: {new_line}")
                time.sleep(2) # Speed cooldown
            
            time.sleep(1) # Fast poll
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_agent()
