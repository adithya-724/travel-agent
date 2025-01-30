from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
from tools import hotels_finder
import pandas as pd
import json

load_dotenv()

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
        Do not include any extra characters in the final output
        ''',
        agent = hotel_search_agent
    )

    crew = Crew(
        agents=[hotel_search_agent],
        tasks=[task],
        verbose = verbose
    )
    result = crew.kickoff()
    result_raw = result.raw
    start_idx = result_raw.find('[')
    end_idx = result_raw.find(']')

    final_result_str = result_raw[start_idx:end_idx+1]
    final_result = json.loads(final_result_str)

    return final_result

