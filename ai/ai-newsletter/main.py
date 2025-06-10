from tinydb import TinyDB, Query
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import json
from pydantic import Field
from scraper import get_news

app = FastAPI()
async def ask_ollama(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt},
            timeout=None
        )

        # Handle streaming response
        final_response = ""
        async for line in response.aiter_lines():
            if line.strip():  # Skip empty lines
                try:
                    data = json.loads(line)
                    final_response += data.get("response", "")
                except json.JSONDecodeError:
                    continue  # Skip non-JSON lines (like logs)

        return final_response


db = TinyDB('db.json')
UserQuery = Query()

# Define the User model
class User(BaseModel):
    user_id: str
    name: str
    email: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    sub_interests: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    exclusions: List[str] = Field(default_factory=list)
    high_priority_topics: List[str] = Field(default_factory=list)
    chat_history: List[str] = Field(default_factory=list)
    feedback: List[str] = Field(default_factory=list)
    delivery_preference: Optional[str] = "app"
    timezone: Optional[str] = "UTC"
    writing_style: Optional[str] = "neutral"  # New: casual, serious, or neutral
    humor_preference: Optional[str] = "none"  # New: none, light, punny
    flow_preference: Optional[bool] = False  # New: story-like flow for newsletters

class ChatRequest(BaseModel):
    user_id: str
    message: str

# Temporary in-memory storage
users_db = {}

@app.get("/")
def read_root():
    return {"message": "Hello, Teddy! Your API is working!"}

@app.post("/user")
def create_user(user: User):
    # Check if user already exists
    if db.search(UserQuery.user_id == user.user_id):
        return {"message": f"User {user.user_id} already exists."}

    # Insert new user into TinyDB
    db.insert(user.dict())
    return {"message": f"User {user.name} created successfully!", "user": user}


@app.post("/chat")
async def chat_with_lev(chat: ChatRequest):
    user_data = db.search(UserQuery.user_id == chat.user_id)
    if not user_data:
        return {"error": "User not found. Please create a user first."}

    user = user_data[0]
    user['chat_history'].append(chat.message)
    db.update({'chat_history': user['chat_history']}, UserQuery.user_id == chat.user_id)

    # Build Lev's prompt
    scraped_data = get_news()
    prompt = f"""
You are Lev, an AI-powered newsletter assistant. You are creating a personalized newsletter for the user based on their unique interests, preferences, and past conversations. Here is their profile:

Name: {user['name']}
Interests: {', '.join(user['interests'])}
Sub-Interests: {', '.join([f"{k}: {', '.join(v)}" for k, v in user.get('sub_interests', {}).items()])}
Exclusions: {', '.join(user.get('exclusions', []))}
High-Priority Topics: {', '.join(user.get('high_priority_topics', []))}
Preferred Writing Style: {user.get('writing_style', 'neutral')}
Humor Preference: {user.get('humor_preference', 'none')}
Flow Preference (Story-like): {user.get('flow_preference', False)}

Recent Chat History: {user.get('chat_history', [])[-5:]}

Based on this profile, respond to the following message from the user in the requested tone and style. Use a friendly and conversational tone, incorporate their humor preferences, and tie your response to their interests when possible.

User's message: {chat.message}
include news articles from the scraped data below (this is for testing purposes), ensuring they align with the user's interests and preferences. If the user has high-priority topics, prioritize those in your response.
{scraped_data}
Also, at the end of your response, ask a follow-up question to keep the conversation going, such as "Was this helpful?" or "Would you like me to include this in your next newsletter?".
"""


    ai_response = await ask_ollama(prompt)

    return {"response": ai_response}



