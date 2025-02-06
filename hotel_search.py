from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
from tools import hotels_finder
import pandas as pd
import json
from pydantic import BaseModel, HttpUrl
from datetime import date

class HotelBooking(BaseModel):
    name: str
    price_inr : float
    ratings: float
    room: str
    booking_link: str
    hotel_type: str
    check_in: date
    check_out: date

load_dotenv()

#load helper information
with open(r'C:\Users\adith\OneDrive\Documents\langchain\travel-agent\data\google-hotels-property-types.json', 'r') as file:
    hotel_types = file.read()
with open(r'C:\Users\adith\OneDrive\Documents\langchain\travel-agent\data\google-hotels-amenities.json', 'r') as file:
    amenties = file.read()

def hotel_agent_response(chat_history,verbose):
    hotel_search_agent = Agent(

    role='Hotel searching agent',
    goal='Search hotels according to user requirement',
    backstory='''
    You are the best agent to find the best hotels for customers. 
    You always understand user's requirements from the conversation and find the best hotels.
    People always reach out to you to find their hotels. 
    You always find the best hotels''',
    tools=[hotels_finder]
    )

    task = Task(
        description=f'''
        You will fetch the top 5 hotels based on the information in the chat history given : 
        "{chat_history}"
        Also use the below provided information if necessary:
        "property_types"
        {hotel_types}

        "amenties"
        {amenties}
        ''',
        expected_output='''JSON output which has the name of the hotel price of the hotel,ratings,room,link to the booking,type of hotel,check-in,check-out.
        # Do not include any extra characters in the final output
        # ''',
        output_pydantic=HotelBooking,
        agent = hotel_search_agent
    )

    crew = Crew(
        agents=[hotel_search_agent],
        tasks=[task],
        verbose = verbose
    )
    result = crew.kickoff()
    result_raw = result.raw
    final_result = json.loads(result_raw)

    return final_result


hotel_agent_response('I want to book a room for goa on 21st may 2025 and 30th may 2025 and i prefer hostels and i want the hostel to include wifi and swimming pool',True)