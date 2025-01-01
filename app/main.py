from config import Config
from fastapi import FastAPI
from pydantic import BaseModel
import logging
from groq import Groq
from app.helpers import tasks
from fastapi.middleware.cors import CORSMiddleware

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

conversation_history = []

@app.get("/")
async def root():
    return {"message": "Success!"}

# Define a data model for the input
class UserInput(BaseModel):
    text: str

@app.post("/process-input/")
async def process_input(text_input: str):
    global conversation_history

    if text_input:
        input_text = text_input.lower()
    else:
        return {"response": "No input provided."}

    conversation_history.append({"role": "user", "content": input_text})

    # Use Groq to process input text dynamically with history
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=conversation_history,  # Include history
        )

        ai_response = response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": ai_response})

        # Handle specific tasks based on keywords
        if "schedule" in ai_response and "appointment" in ai_response:
            return {"response": tasks.create_appointment("2024-12-30", "2:00 PM")}
        elif "reserve" in ai_response and "restaurant" in ai_response:
            return {"response": tasks.make_reservation("Cafe Delight", "7:00 PM")}
        else:
            return {"response": ai_response}

    except Exception as e:
        return {"response": None, "error": f"Error processing input: {str(e)}"}
