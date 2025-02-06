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

from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os
from tools import hotels_finder, get_reddit_comments, fetch_reddit_content
import pandas as pd
import json
from pydantic import BaseModel, HttpUrl
from datetime import date
from pprint import pprint

load_dotenv()

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv
import os
from tools import hotels_finder, get_reddit_comments
import pandas as pd
import json
from pydantic import BaseModel, HttpUrl
from datetime import date
from pprint import pprint

load_dotenv()


def create_detailed_itinerary(chat_history, verbose):
    # Define the Summarizing Agent
    summarizing_agent = Agent(
    role='Geographical Information Extractor',
    goal='Identify the main country and the most prominently mentioned city within that country from the conversation.',
    backstory='''
    You specialize in analyzing conversations to extract geographical information.
    Your primary objective is to determine the main country discussed and identify the city within that country that is most frequently or prominently mentioned.
    This information aids in understanding the user's travel intentions and preferences.
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
        Analyze the following conversation to identify:
        1. The primary country mentioned.
        2. The most prominent city within that country mentioned.
        If multiple cities are mentioned, select the one most commonly referenced or contextually significant.
        Provide these as a single string, separated by a comma.
        Conversation:
        {chat_history}
        ''',
        expected_output='A single string containing the country and city separated by a comma.',
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




def create_detailed_itinerary1(chat_history, verbose):
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
        Extract a maximum of three locations where the first location should always be the country
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

# Example chat history
chat_history = '''
Travel Agent: Hi! Welcome to Wanderlust Travels. How can I help you today?

Customer: Hi! I’m planning a trip to Thailand and want to focus on water activities. Can you help?

Travel Agent: Absolutely! Thailand is perfect for that. When are you planning to go?

Customer: Late November or early December, for about 15 days.

Travel Agent: Great timing! The weather is ideal for water activities then. I’d suggest Phuket, Krabi, and the Phi Phi Islands. You can snorkel, dive, kayak, and explore stunning beaches.

Customer: That sounds perfect! What can I do in each place?

Travel Agent: In Phuket, you can dive at Racha Yai Island or kayak in Phang Nga Bay. In Krabi, try the Four Islands Tour for snorkeling and visit Railay Beach. In Phi Phi, don’t miss Maya Bay and snorkeling at Bamboo Island.

Customer: That all sounds amazing! Can you arrange accommodations too?
     v 
Travel Agent: Of course! I’ll book beachfront resorts in Phuket and Krabi, and a cozy bungalow in Phi Phi. I’ll send you a detailed itinerary soon.

Customer: Perfect! Thank you so much.

Travel Agent: You’re welcome! Get ready for an unforgettable trip. I’ll be in touch soon with the details. 😊

Customer: Thanks! Talk to you soon!
'''

# Execute the detailed itinerary creation
detailed_itinerary = create_detailed_itinerary1(chat_history, True)
print(detailed_itinerary)
