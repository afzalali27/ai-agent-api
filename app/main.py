from config import Config
from fastapi import FastAPI, Request
from pydantic import BaseModel
import logging
from groq import Groq
from app.helpers import tasks
from app.utils.training_data import initial_context
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

# Set up the OpenAI API key
client = Groq(api_key=Config.GROQ_API_KEY)

app = FastAPI()

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_histories = {}

MAX_HISTORY_LENGTH = 1000
GLOBAL_SESSION = '_global_key'

def get_user_conversation(session_id: str):
    if session_id not in conversation_histories:
        conversation_histories[session_id] = initial_context.copy()
    return conversation_histories[session_id]

def update_user_conversation(session_id: str, message: dict):
    if session_id not in conversation_histories:
        conversation_histories[session_id] = initial_context.copy()
    conversation_histories[session_id].append(message)
    if len(conversation_histories[session_id]) > MAX_HISTORY_LENGTH:
        conversation_histories[session_id] = conversation_histories[session_id][-MAX_HISTORY_LENGTH:]


@app.get("/")
async def root():
    return {"message": "Success!"}

# Define a data model for the input
class UserInput(BaseModel):
    text: str

@app.post("/process-input/")
async def process_input(request: Request, text_input: str):
    session_id = request.headers.get("X-Session-ID", GLOBAL_SESSION)

    if text_input:
        input_text = text_input.lower()
    else:
        return {"response": "No input provided."}

    update_user_conversation(session_id, {"role": "user", "content": input_text})

    # Use Groq to process input text dynamically with history
    try:
        location_for_weather = tasks.weather_query_location(input_text)
        if location_for_weather:
            weather_data = tasks.fetch_weather(location_for_weather)
            weather_summary = tasks.summarize_weather(weather_data)
        else:
            result = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=get_user_conversation(session_id),
            )
            ai_response = result.choices[0].message.content
            
        response = weather_summary if location_for_weather else ai_response
        
        update_user_conversation(session_id, {"role": "assistant", "content": response})

        # Handle specific tasks based on keywords
        if "schedule" in response and "appointment" in response:
            return {"response": tasks.create_appointment("2024-12-30", "2:00 PM")}
        elif "reserve" in response and "restaurant" in response:
            return {"response": tasks.make_reservation("Cafe Delight", "7:00 PM")}
        else:
            return {"response": response}

    except Exception as e:
        return {"response": None, "error": f"Error processing input: {str(e)}"}
