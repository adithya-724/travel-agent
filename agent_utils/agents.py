from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from agent_utils.tools import hotels_finder, fetch_reddit_content
import json
from pydantic import BaseModel
from datetime import date
import yaml


load_dotenv()

# Load agent prompts from YAML
with open("prompts/agent_prompts.yaml", "r") as file:
    agent_prompts = yaml.safe_load(file)


class HotelBooking(BaseModel):
    name: str
    price_total: float
    price_per_night: float
    ratings: float
    room: str
    booking_link: str
    hotel_type: str
    check_in: date
    check_out: date


def itinerary_agent(chat_history, verbose):
    # Load itinerary agent configurations
    itinerary_config = agent_prompts["itinerary_agents"]

    # Define the Summarizing Agent
    summarizing_agent = Agent(
        role=itinerary_config["summarizing_agent"]["role"],
        goal=itinerary_config["summarizing_agent"]["goal"],
        backstory=itinerary_config["summarizing_agent"]["backstory"],
    )

    # Define the Itinerary Planning Agent
    itinerary_agent = Agent(
        role=itinerary_config["itinerary_agent"]["role"],
        goal=itinerary_config["itinerary_agent"]["goal"],
        backstory=itinerary_config["itinerary_agent"]["backstory"],
        tools=[fetch_reddit_content],
        max_iter=itinerary_config["itinerary_agent"]["max_iter"],
        llm=itinerary_config["itinerary_agent"]["llm"],
    )

    # Load task configurations
    task_config = agent_prompts["tasks"]

    # Task for the Summarizing Agent
    summ_task = Task(
        description=task_config["summarising_task"]["description"].format(
            chat_history=chat_history
        ),
        expected_output=task_config["summarising_task"]["expected_output"],
        agent=summarizing_agent,
    )

    # Task for the Itinerary Planning Agent
    plan_task = Task(
        description=task_config["itinerary_task"]["description"].format(
            chat_history=chat_history
        ),
        expected_output=task_config["itinerary_task"]["expected_output"],
        agent=itinerary_agent,
        context=[summ_task],
    )

    # Create the Crew with both agents and their tasks
    crew = Crew(
        agents=[summarizing_agent, itinerary_agent],
        tasks=[summ_task, plan_task],
        verbose=verbose,
    )

    result = crew.kickoff()
    return result.raw


# load helper information
with open("data\google-hotels-property-types.json", "r") as file:
    hotel_types = json.load(file)

with open("data\google-hotels-amenities.json", "r") as file:
    amenities = json.load(file)


def hotel_agent(chat_history, verbose):
    # Load hotel agent configurations
    hotel_config = agent_prompts["hotel_agents"]

    budget_agent = Agent(
        role=hotel_config["budget_agent"]["role"],
        goal=hotel_config["budget_agent"]["goal"],
        backstory=hotel_config["budget_agent"]["backstory"],
    )

    hotel_search_agent = Agent(
        role=hotel_config["hotel_search_agent"]["role"],
        goal=hotel_config["hotel_search_agent"]["goal"],
        backstory=hotel_config["hotel_search_agent"]["backstory"],
        tools=[hotels_finder],
        llm=hotel_config["hotel_search_agent"]["llm"],
    )

    # Load task configurations
    task_config = agent_prompts["tasks"]

    budget_task = Task(
        description=task_config["budget_task"]["description"].format(
            chat_history=chat_history
        ),
        expected_output=task_config["budget_task"]["expected_output"],
        agent=budget_agent,
    )

    hotel_task = Task(
        description=task_config["hotel_task"]["description"].format(
            chat_history=chat_history, hotel_types=hotel_types, amenities=amenities
        ),
        expected_output=task_config["hotel_task"]["expected_output"],
        output_pydantic=HotelBooking,
        agent=hotel_search_agent,
        context=[budget_task],
    )

    crew = Crew(
        agents=[budget_agent, hotel_search_agent],
        tasks=[budget_task, hotel_task],
        verbose=verbose,
    )

    result = crew.kickoff()
    final_result = json.loads(result.raw)

    return final_result
