import logging
import re
from config import Config
import requests


WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Simulate external API for appointment scheduling
def create_appointment(date: str, time: str) -> str:
    logging.info(f"Scheduling appointment for {date} at {time}.")
    # Mocked response from an external API
    return f"Appointment successfully scheduled for {date} at {time}."

# Simulate external API for restaurant reservation
def make_reservation(restaurant: str, time: str) -> str:
    logging.info(f"Making reservation at {restaurant} for {time}.")
    # Mocked response from an external API
    return f"Reservation at {restaurant} for {time} confirmed."

def default_response(ai_response: str) -> str:
    return ai_response

def weather_query_location(query):
    """Determine if the user query is related to weather, and return location"""
    print(query)
    patterns = [
        r"what is the weather of (.+)",
        r"what is the weather in (.+)",
        r"tell me the current weather of (.+)",
        r"weather forecast (.+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            print(match.group(1))
            return match.group(1)
    return None


def fetch_weather(location):
    try:
        response = requests.get(WEATHER_API_URL, params={
            "q": location,
            "appid": Config.OPEN_WEATHER_API_KEY,
        })
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.info(f"Error fetching weather data: {str(e)}")
        
    return f"Could not fetch weather for {location}. Please try again."


def summarize_weather(api_response):
    """
    Converts weather API response into a human-readable summary.

    Args:
        api_response (dict): The JSON response from the weather API.

    Returns:
        str: A short summary of the weather.
    """
    try:
        location = api_response.get('name', 'Unknown Location')
        country = api_response.get('sys', {}).get('country', '')
        weather = api_response.get('weather', [{}])[0]
        condition = weather.get('description', 'unknown weather').capitalize()
        temperature = api_response.get('main', {}).get('temp', None)
        feels_like = api_response.get('main', {}).get('feels_like', None)
        humidity = api_response.get('main', {}).get('humidity', None)
        wind_speed = api_response.get('wind', {}).get('speed', None)
        visibility = api_response.get('visibility', None)

        # Convert temperature from Kelvin to Celsius
        if temperature is not None:
            temperature_c = round(temperature - 273.15, 1)
        else:
            temperature_c = "unknown"

        if feels_like is not None:
            feels_like_c = round(feels_like - 273.15, 1)
        else:
            feels_like_c = "unknown"

        # Build the summary
        summary = f"Weather in {location}, {country}: {condition}."
        summary += f" Temperature is {temperature_c}°C (feels like {feels_like_c}°C)."
        if humidity is not None:
            summary += f" Humidity is {humidity}%."
        if wind_speed is not None:
            summary += f" Wind speed is {wind_speed} m/s."
        if visibility is not None:
            summary += f" Visibility is {visibility} meters."

        return summary

    except Exception as e:
        return f"Unable to process weather data: {str(e)}"
