import asyncio
import aiohttp
from config import Config

async def query_gpt4_async(prompt: str) -> str:
    """Async GPT-4 query for parallel processing"""
    if not Config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
        
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
    
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", 
                               headers=headers, json=json_data) as resp:
            response_data = await resp.json()
            return response_data['choices'][0]['message']['content']

# --- Synchronous wrapper ---
def query_gpt4(prompt: str) -> str:
    """Synchronous wrapper for GPT-4"""
    return asyncio.run(query_gpt4_async(prompt))
