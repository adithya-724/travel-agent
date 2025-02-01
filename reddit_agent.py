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

def reddit_info_agent(chat_history,verbose):

    summarising_agent = Agent(

    role='Conversation Summariser Agent',
    goal='Summarise and extract key information from a conversation',
    backstory='''
   You are the best when it comes to summarising and extracting key information from a conversation.
   You will always try to understand what the intention of the user is in the best possible way.
    '''
    )


    

    task1 = Task(
        description=f'''
       You will first summarise the chat history
        {chat_history}:
        You will only extract a maximum of 3 keywords from the conversation which should always include the country of visit followed by other details.
        ''',
        expected_output='''
        A python string containing the extracted keywords.
        ''',
        agent = summarising_agent
    )


   
    crew = Crew(
        agents=[summarising_agent],
        tasks=[task1],
        verbose = verbose
    )
    result = crew.kickoff()
    result_raw = result.raw
    # start_idx = result_raw.find('[')
    # end_idx = result_raw.find(']')

    # final_result_str = result_raw[start_idx:end_idx+1]
    # final_result = json.loads(final_result_str)

    return result_raw


def create_itinerary(chat_history,verbose):
    reddit_agent = Agent(

        role='Itinerary Creation Agent',
        goal='Fetch relevant information from reddit comments  and craft the best possible itinerary',
        backstory='''
        You are the best agent to fetch relevant comments from reddit.
        You always understand the user's requirement perfectly and craft the best possible itinerary according to the user's requirement.
        ''',
        tools=[get_reddit_comments]
        )

    task2 = Task(
            description=f'''
        You will use this information : {chat_history}  to fetch relevant reddit comments 
        Using all the relevant comments, you will craft an itinerary customised to the user's requirements.
            ''',
            expected_output='''
            A python string neatly formatted containing the final itinerary
            ''',
            agent = reddit_agent
        )

    crew = Crew(
        agents=[reddit_agent],
        tasks=[task2],
        verbose = verbose
    )
    result = crew.kickoff()
    result_raw = result.raw



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


# keywords = reddit_info_agent(chat_history,True)

# pprint(keywords)
# print(type(keywords))
iti = create_itinerary(chat_history,True)

pprint(iti)