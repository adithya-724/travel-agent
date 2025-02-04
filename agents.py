from crewai import Agent,Task,Crew,LLM
from dotenv import load_dotenv
import os
from tools import hotels_finder, get_reddit_comments ,fetch_reddit_content
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
        role='Location Extractor',
        goal='Identify and extract country or location names mentioned in the conversation history.',
        backstory='''
        You specialize in parsing conversations to detect and extract geographical locations, such as country names or cities, mentioned by the user.
        Your primary objective is to identify these locations to assist in itinerary planning or travel-related inquiries.
        '''
    )


    # Define the Itinerary Planning Agent
    itinerary_agent = Agent(
        role='Itinerary Planner',
        goal='Craft a detailed travel itinerary based on extracted keywords, chat history, and relevant Reddit insights.',
        backstory='''You specialize in creating comprehensive travel itineraries tailored to user preferences. 
        By leveraging extracted keywords, detailed chat history, and insights from Reddit, you design itineraries that include optimal activity times and daily schedules.''',
        tools=[fetch_reddit_content],
        max_iter=2
    )

    # Task for the Summarizing Agent
    task1 = Task(
        description=f'''
        Analyze the following conversation to identify and extract all country or city names mentioned:
        {chat_history}
        Focus on listing each unique location found in the conversation.
        Provide these locations as a single string, separated by commas.
        ''',
        expected_output='A single string containing the extracted locations, separated by commas.',
        agent=summarizing_agent
    )


    # Task for the Itinerary Planning Agent
    task2 = Task(
        description=f'''
        Using the extracted information and the detailed chat history, perform the following:
        1. Research the specified destination to identify key attractions and activities related to the user's interests.
        2. Gather relevant Reddit comments to incorporate actual user experiences and additional insights.
        3. Determine the best times for each activity, considering factors like weather, peak hours, and seasonal events.
        4. Organize activities into a daily schedule, ensuring a balanced and enjoyable itinerary.
        5. Provide recommendations for dining, relaxation, and other leisure activities that align with the user's preferences.
        Ensure that the itinerary is detailed, practical, and tailored to the user's interests.
        Chat history:
        {chat_history}
        ''',
        expected_output='A Python string containing a detailed daily itinerary with scheduled activities, times, and additional recommendations. It should not be a dictionary.',
        agent=itinerary_agent,
        context=[task1]
    )

    # Create the Crew with both agents and their tasks
    crew = Crew(
        agents=[summarizing_agent, itinerary_agent],
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
    final_result = json.loads(result_raw)
    # start_idx = result_raw.find('[')
    # end_idx = result_raw.find(']')

    # final_result_str = result_raw[start_idx:end_idx+1]
    # final_result = json.loads(final_result_str)

    return final_result

