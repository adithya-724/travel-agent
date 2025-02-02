from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
from tools import hotels_finder, get_reddit_comments
import pandas as pd
import json
from pydantic import BaseModel, HttpUrl
from datetime import date
from pprint import pprint


load_dotenv()

class HotelBooking(BaseModel):
    name: str
    price_inr : float
    ratings: float
    room: str
    booking_link: str
    hotel_type: str
    check_in: date
    check_out: date



def create_detailed_itinerary(chat_history, verbose):
    # Define the Summarizing Agent
    summarizing_agent = Agent(
        role='Travel Conversation Summarizer',
        goal='Extract key travel details and user preferences from the conversation to inform itinerary planning.',
        backstory='''
        You are an expert in analyzing travel-related conversations. 
        Your primary objective is to identify and extract essential details such as destinations, preferred activities, travel dates, and any specific user preferences. 
        This information will serve as the foundation for crafting a personalized and detailed travel itinerary.
        '''
    )

    # Define the Reddit Insights Agent
    reddit_agent = Agent(
        role='Detailed Itinerary Planner',
        goal='Utilize extracted travel details to gather in-depth information and craft a comprehensive daily itinerary, including optimal times for activities and scheduling considerations.',
        backstory='''
        You specialize in creating detailed travel itineraries by leveraging various information sources. 
        Your role involves understanding user preferences, researching relevant details, and organizing activities into a coherent daily schedule. 
        You ensure that each day is well-planned, considering factors like the best times for activities, travel logistics, and user interests.
        ''',
        tools=[get_reddit_comments],
        max_iter=2
    )

    # Task for the Summarizing Agent
    task1 = Task(
        description=f'''
        Analyze the following conversation to extract key travel details:
        {chat_history}
        Focus on identifying:
        1. Destination country and specific locations.
        2. Preferred activities or interests.
        3. Proposed travel dates or time frames.
        4. Any additional user preferences or requirements.
        Limit your extraction to a maximum of 3 keywords that best represent the user's travel intentions.
        Provide a concise summary highlighting these details.
        ''',
        expected_output='A Python string containing up to 3 extracted keywords representing travel details such as destinations, activities, dates, and preferences',
        agent=summarizing_agent
    )

    # Task for the Reddit Insights Agent
    task2 = Task(
        description='''
        Using the extracted travel details, perform the following:
        1. Research each destination to identify must-see attractions and activities.
        2. Determine the optimal times for each activity (e.g., best time of day, seasonal considerations).
        3. Organize activities into a daily schedule, ensuring a balanced and enjoyable itinerary.
        4. Incorporate travel logistics between locations, considering realistic time allocations.
        5. Provide recommendations for dining, relaxation, and other leisure activities.
        Ensure that the itinerary is detailed, practical, and aligns with the user's preferences and interests.
        ''',
        expected_output='A Python string containing a detailed daily itinerary with scheduled activities, times, and additional recommendations.',
        agent=reddit_agent
    )

    crew = Crew(
        agents=[summarizing_agent, reddit_agent],
        tasks=[task1, task2],
        verbose=verbose
    )

    # Execute the Crew's tasks
    result = crew.kickoff()
    return result.raw




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
        {chat_history}
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
    # start_idx = result_raw.find('[')
    # end_idx = result_raw.find(']')

    # final_result_str = result_raw[start_idx:end_idx+1]
    # final_result = json.loads(final_result_str)

    return result_raw

