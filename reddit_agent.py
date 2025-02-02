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
from tools import hotels_finder, get_reddit_comments
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
        role='Travel Conversation Summarizer',
        goal='Extract two primary keywords from the conversation to inform itinerary planning.',
        backstory='''
        You are adept at analyzing travel-related conversations to identify the most pertinent themes. 
        Your primary objective is to distill the discussion into two main keywords that encapsulate the user's travel intentions and preferences.''',
    )

    # Define the Itinerary Planning Agent
    itinerary_agent = Agent(
        role='Itinerary Planner',
        goal='Craft a detailed travel itinerary based on extracted keywords, chat history, and relevant Reddit insights.',
        backstory='''You specialize in creating comprehensive travel itineraries tailored to user preferences. 
        By leveraging extracted keywords, detailed chat history, and insights from Reddit, you design itineraries that include optimal activity times and daily schedules.''',
        tools=[get_reddit_comments],
        max_iter=2
    )

    # Task for the Summarizing Agent
    task1 = Task(
        description=f'''
        Analyze the following conversation to extract two primary keywords that best represent the user's travel intentions:
        {chat_history}
        Focus on identifying:
        1. The main destination country or city.
        2. The primary theme or type of activities the user is interested in.
        Provide these keywords as a single string, separated by a space.
        ''',
        expected_output='A single string containing the two keywords separated by a space.',
        agent=summarizing_agent
    )

    # Task for the Itinerary Planning Agent
    task2 = Task(
        description=f'''
        Using the extracted keywords and the detailed chat history, perform the following:
        1. Research the specified destination to identify key attractions and activities related to the user's interests.
        2. Gather relevant Reddit comments to incorporate actual user experiences and additional insights.
        3. Determine the best times for each activity, considering factors like weather, peak hours, and seasonal events.
        4. Organize activities into a daily schedule, ensuring a balanced and enjoyable itinerary.
        5. Provide recommendations for dining, relaxation, and other leisure activities that align with the user's preferences.
        Ensure that the itinerary is detailed, practical, and tailored to the user's interests.
        Always use only the extracted keywords from the previous task.
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

Travel Agent: Of course! I’ll book beachfront resorts in Phuket and Krabi, and a cozy bungalow in Phi Phi. I’ll send you a detailed itinerary soon.

Customer: Perfect! Thank you so much.

Travel Agent: You’re welcome! Get ready for an unforgettable trip. I’ll be in touch soon with the details. 😊

Customer: Thanks! Talk to you soon!
'''

# Execute the detailed itinerary creation
detailed_itinerary = create_detailed_itinerary(chat_history, True)
print(detailed_itinerary)
