import os
from dotenv import load_dotenv
from openai import OpenAI
import datetime
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com")

chat_history = """
User: I need to fly from new York to London on May 15th
Agent: How many people will be traveling?
User: Just myself, and I'd like to keep it under $800
"""

current_date = datetime.date.today()

prompt = f"""
        Today's date is {current_date}
       Extract these parameters from the chat history:
       - origin airport code AS origin
       - destination airport code AS destination
       - departure date
       - return date (if round trip)
       - number of travelers AS travelers
       - budget

       Chat History: {chat_history}

       Return python dict format with double quotes, use only null for missing information and dont use python  .

       """


def get_flight_response(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a flight booking assistant."},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    response_content = response.choices[0].message.content
    try:
        response_dict = json.loads(response_content)
        return response_dict
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


extracted_data = get_flight_response(prompt)


def flight_search(extracted_data):
    import os
    from dotenv import load_dotenv
    from amadeus import Client, ResponseError

    load_dotenv()

    amadeus = Client(
        client_id=os.getenv('AMADEUS_CLIENT_ID'),
        client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
    )

    params = {
        "originLocationCode": extracted_data.get('origin'),
        "destinationLocationCode": extracted_data.get('destination'),
        "departureDate": extracted_data.get('departure_date'),
        "adults": extracted_data.get('travelers', 1),
        "maxPrice": extracted_data.get('budget'),
        "currencyCode": "USD",
        "max": 5
    }
    # Add returnDate only if provided
    if extracted_data["return_date"] is not None:
        params["returnDate"] = extracted_data["return_date"]
    # Remove keys with None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = amadeus.shopping.flight_offers_search.get(**params)

        print(f"Flights from {params['originLocationCode']} to {params['destinationLocationCode']}:")
        for flight in response.data:
            offer = flight['itineraries'][0]['segments'][0]
            price = flight['price']['total']

            print(f"\nFlight: {offer['carrierCode']}{offer['number']}")
            print(f"Departure: {offer['departure']['at']} ({offer['departure']['iataCode']})")
            print(f"Arrival: {offer['arrival']['at']} ({offer['arrival']['iataCode']})")
            print(f"Duration: {flight['itineraries'][0]['duration']}")
            print(f"Price: {price} {params['currencyCode']}")

    except ResponseError as error:
        print(f"Error: {error}")


flight_search(extracted_data)