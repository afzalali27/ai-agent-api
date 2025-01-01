import logging

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