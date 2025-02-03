from crewai_tools import WebsiteSearchTool
from crewai import Agent,Task,Crew,LLM
from dotenv import load_dotenv
import os
from tools import hotels_finder, get_reddit_comments
import pandas as pd
import json
from pydantic import BaseModel, HttpUrl
from datetime import date
from pprint import pprint

# Example of initiating tool that agents can use 
# to search across any discovered websites
tool = WebsiteSearchTool()


query = input('Enter query')
agent= Agent(

    role='Scraping agent',
    goal='Search and fetch relevant information from the internet',
    backstory='''
    You always have a knack to find the best and most relevant information based on the user's query.
    You always extract the right and proper information from the internet.
    ''',
    tools=[tool]
    )

task = Task(
    description=f'''
    You will fetch the most relevant pieces of information based on this query
    {query}
    ''',
    expected_output='''
    You will return a string contianing relevant information
    ''',
    agent = agent
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose = True
)
result = crew.kickoff()
result_raw = result.raw
final_result = json.loads(result_raw)