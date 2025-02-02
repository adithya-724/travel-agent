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

# Example chat history
chat_history = '''
Travel Agent: Hi! Welcome to Wanderlust Travels. How can I help you today?

Customer: Hi! I’m planning a trip to Thailand and want to focus on water activities. Can you help?

Travel Agent: Absolutely! Thailand is perfect for that. When are you planning to go?

Customer: Late November or early December, for about 10 days.

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
