from config import Config
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
import speech_recognition as sr
import logging
from groq import Groq
from helpers import tasks
import os
import pyttsx3
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

@app.get("/")
async def root():
    return {"message": "Hello, Voice Agent!"}


# Define a data model for the input
class UserInput(BaseModel):
    text: str

@app.post("/process-input/")
async def process_input(text_input: str = None, audio_file: UploadFile = None, respondWithAudio: bool = False):
    if audio_file:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file.file) as source:
            audio_data = recognizer.record(source)
        try:
            input_text = recognizer.recognize_google(audio_data).lower()
            logging.info(f"Transcribed input: {input_text}")
        except sr.UnknownValueError:
            return {"response": "I couldn’t understand the audio. Please try again."}
        except sr.RequestError as e:
            return {"response": f"Error with the speech recognition service: {e}"}
    elif text_input:
        input_text = text_input.lower()
    else:
        return {"response": "No input provided."}

    # Use Groq to process input text dynamically
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": input_text}],
        )

        ai_response = response.choices[0].message.content

        if respondWithAudio:
            try:
                # Initialize TTS engine
                tts_engine = pyttsx3.init()
                audio_output_dir = "audio_responses"
                os.makedirs(audio_output_dir, exist_ok=True)
                audio_file_path = os.path.join(audio_output_dir, "response.aiff")
                tts_engine.save_to_file(ai_response, audio_file_path)
                logging.info(f"Generated audio response...")
                tts_engine.runAndWait()
                return {
                    "response": ai_response,
                    "audio_url": f"/audio/{os.path.basename(audio_file_path)}"
                }
            except Exception as e:
                tts_engine.stop()
                return {"response": None, "error": f"Error processing input: {str(e)}"}
        else:
            if "schedule" in ai_response and "appointment" in ai_response:
                return {"response": tasks.create_appointment("2024-12-30", "2:00 PM")}
            elif "reserve" in ai_response and "restaurant" in ai_response:
                return {"response": tasks.make_reservation("Cafe Delight", "7:00 PM")}
            else:
                return { "response": ai_response}
    
    except Exception as e:
        return {"response": None, "error": f"Error processing input: {str(e)}"}
    