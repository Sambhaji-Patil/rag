import asyncio
import requests
from config import Config

async def query_gpt4_async(prompt: str) -> str:
    """Async GPT-4 query for parallel processing"""
    if not Config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, query_gpt4_sync, prompt)

def query_gpt4_sync(prompt: str) -> str:
    """Synchronous GPT-4 query"""
    headers = {
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": Config.GPT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": Config.GPT_TEMPERATURE,
        "max_tokens": Config.GPT_MAX_TOKENS
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying GPT-4: {e}")
        return f"Error: {str(e)}"

# --- Synchronous wrapper ---
def query_gpt4(prompt: str) -> str:
    """Synchronous wrapper for GPT-4"""
    return asyncio.run(query_gpt4_async(prompt))
