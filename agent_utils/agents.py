from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from agent_utils.tools import hotels_finder, fetch_reddit_content
import json
from pydantic import BaseModel
from datetime import date


load_dotenv()


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
    # Define the Summarizing Agent
    summarizing_agent = Agent(
        role="Location Extractor",
        goal="Identify and extract country or location names mentioned in the conversation history.",
        backstory="""
        You specialize in parsing conversations to detect and extract geographical locations, such as country names or cities, mentioned by the user.
        Your primary objective is to identify these locations to assist in itinerary planning or travel-related inquiries.
        """,
    )

    # Define the Itinerary Planning Agent
    itinerary_agent = Agent(
        role="Itinerary Planner",
        goal="Craft a detailed travel itinerary based on extracted keywords, chat history, and relevant Reddit insights.",
        backstory="""You specialize in creating comprehensive travel itineraries tailored to user preferences. 
        By leveraging extracted keywords, detailed chat history, and insights from Reddit, you design itineraries that include optimal activity times and daily schedules.""",
        tools=[fetch_reddit_content],
        max_iter=5,
    )

    # Task for the Summarizing Agent
    task1 = Task(
        description=f"""
        Analyze the following conversation to identify and extract all country or city names mentioned:
        {chat_history}
        Focus on listing each unique location found in the conversation.
        Provide these locations as a single string, separated by commas.
        Extract a maximum of three locations where the first location should always be the country
        """,
        expected_output="A single string containing the extracted locations, separated by commas.",
        agent=summarizing_agent,
    )

    # Task for the Itinerary Planning Agent
    task2 = Task(
        description=f"""
        Using the extracted information and the detailed chat history, perform the following:
        1. Research the specified destination to identify key attractions and activities related to the user's interests.
        2. Gather relevant Reddit comments to incorporate actual user experiences and additional insights.
        3. Determine the best times for each activity, considering factors like weather, peak hours, and seasonal events.
        4. Organize activities into a daily schedule, ensuring a balanced and enjoyable itinerary.
        5. Provide recommendations for dining, relaxation, and other leisure activities that align with the user's preferences.
        Ensure that the itinerary is detailed, practical, and tailored to the user's interests.
        Chat history:
        {chat_history}
        """,
        expected_output="A Python string containing a detailed daily itinerary with scheduled activities, times, and additional recommendations. It should not be a dictionary.",
        agent=itinerary_agent,
        context=[task1],
    )

    # Create the Crew with both agents and their tasks
    crew = Crew(
        agents=[summarizing_agent, itinerary_agent],
        tasks=[task1, task2],
        verbose=verbose,
    )

    # Execute the Crew's tasks
    result = crew.kickoff()
    return result.raw


# load helper information
with open("data\google-hotels-property-types.json", "r") as file:
    hotel_types = json.load(file)

with open("data\google-hotels-amenities.json", "r") as file:
    amenities = json.load(file)


def hotel_agent(chat_history, verbose):
    budget_agent = Agent(
        role="Budget calculator",
        goal="Calculate daily hotel budget based on total trip budget",
        backstory="""You are an expert at analyzing travel budgets and determining appropriate 
        daily hotel allocations. You understand how to parse conversations to extract budget 
        information and calculate per-day hotel costs.""",
    )

    hotel_search_agent = Agent(
        role="Hotel searching agent",
        goal="Search hotels according to user requirement",
        backstory="""
        You are the best agent to find the best hotels for customers. 
        You always understand user's requirements from the conversation and find the best hotels.
        People always reach out to you to find their hotels. 
        You always find the best hotels""",
        tools=[hotels_finder],
    )

    budget_task = Task(
        description=f"""
        Analyze the chat history to:
        1. Extract the total trip budget and currency
        2. Extract the number of days for the trip
        3. Calculate 30% of the total budget for hotels
        4. Divide the hotel budget by number of days to get per-day hotel budget

        Chat history:
        {chat_history}
        """,
        expected_output="An integer representing the maximum per day hotel budget in the original currency",
        agent=budget_agent,
    )

    hotel_task = Task(
        description=f'''
        Using the per-day budget calculated, fetch the top 5 hotels based on the information in the chat history:
        "{chat_history}"

        Make sure to return the prices in the currency mentioned by the user.

        Also use the below provided information if necessary:
        "property_types"
        {hotel_types}

        "amenties"
        {amenities}
        ''',
        expected_output="""
        JSON output which has the name of the hotel, total price of the hotel, price per night of the hotel, 
        ratings, room, link to the booking, type of hotel, check-in, check-out.
        # Do not include any extra characters in the final output
        """,
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
