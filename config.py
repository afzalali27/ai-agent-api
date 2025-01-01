import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    APPOINTMENT_API_URL = os.getenv("APPOINTMENT_API_URL")
    RESERVATION_API_URL = os.getenv("RESERVATION_API_URL")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")