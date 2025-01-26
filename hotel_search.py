from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
from hotel_tool import hotels_finder

load_dotenv()

query = input('User : ')

hotel_search_agent = Agent(

role='Hotel searching agent',
goal='Search hotels according to user requirement',
backstory='''You are the best agent to find the best hotels for customers.  
People always reach out to you to find their hotels. 
You always find the best hotels''',
 tools=[hotels_finder]
)

task = Task(

    description=f'{query}',
    expected_output='JSON output which has the name of the hotel price of the hotel,ratings,room,link to the booking,type of hotel',
    agent = hotel_search_agent
)

crew = Crew(
    agents=[hotel_search_agent],
    tasks=[task],
    verbose = True
)

print(crew.kickoff())