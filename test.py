from agent_utils.agents import hotel_agent, itinerary_agent
import pandas as pd


chat_history = """
Agent: Hello! How can I assist you with your travel plans today?
User: Hi! I'm planning a trip to india in November 21st 2025 .

Agent: That sounds wonderful! Which cities in india are you interested in visiting?
User: I'd like to visit goa , maybe spend around 10 days total.

Agent: Great choices! What's your approximate budget for this trip, including accommodations and activities?
User: My budget is around 100000 INR for the whole trip.

Agent: Perfect, thank you for sharing those details. Just to confirm - you're planning a 10-day trip to india, visiting goa, with a budget of 100000 INR. Would you prefer luxury, mid-range, or budget accommodations?
User: I would prefer hotels and hostels
"""


response = itinerary_agent(chat_history, True)
hotels_df = pd.DataFrame(response)
