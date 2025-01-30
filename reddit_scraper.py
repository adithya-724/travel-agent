from crewai import Agent,Task,Crew
from dotenv import load_dotenv
import os
from tools import hotels_finder
import pandas as pd
import json
from crewai_tools import (
    WebsiteSearchTool
)

load_dotenv()

def reddit_scraper(input):
    web_rag_tool = WebsiteSearchTool()

    subreddit_scraper_agent = Agent(

    role='Subreddit scraping agent',
    goal='Search and find the most relevant sub reddits',
    backstory='''
    You are the best subreddit scraper. You can fetch relevant subreddits related to the user's query.
    ''',
    tools=[web_rag_tool]
    )

    task = Task(
        description=f'''
        You will find the most relevant subreddits based on the user's query : {input}
        ''',
        expected_output='''
        Python list of all relevant subreddits in the order of relevance.
        Do not include any extra characters in the final output
        ''',
        agent = subreddit_scraper_agent
    )

    crew = Crew(
        agents=[subreddit_scraper_agent],
        tasks=[task],
        verbose = True
    )
    result = crew.kickoff()
    result_raw = result.raw
    start_idx = result_raw.find('[')
    end_idx = result_raw.find(']')

    final_result_str = result_raw[start_idx:end_idx+1]
    final_result = json.loads(final_result_str)

    return final_result


print(reddit_scraper('thailand tourism'))