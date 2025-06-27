import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from utils.utils import get_deepseek_response
from agent_utils.agents import hotel_agent, itinerary_agent
from langchain_openai import ChatOpenAI
import pandas as pd
import time
import datetime
import yaml
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_community.callbacks.manager import get_openai_callback

# load env vars
load_dotenv()


st.title("Travel Agent")

# Get current year
current_year = datetime.datetime.now().year


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_history" not in st.session_state:
    st.session_state.message_history = ""

if "formatted_chat_history" not in st.session_state:
    st.session_state.formatted_chat_history = []

if "conv_end_flag" not in st.session_state:
    st.session_state.conv_end_flag = 0

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "prompt_tokens" not in st.session_state:
    st.session_state.prompt_tokens = 0
if "completion_tokens" not in st.session_state:
    st.session_state.completion_tokens = 0
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# Add new session state variables for hotels and itinerary
if "hotels_df" not in st.session_state:
    st.session_state.hotels_df = None

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

# sidebar
with st.sidebar:
    hist_btn = st.button("clear chat history")

    model = st.radio("Choose chat model:", ["gpt-4o", "gpt-4"])

    if hist_btn:
        st.session_state.messages = []
        st.session_state.message_history = ""
        st.session_state.formatted_chat_history = []
        st.session_state.conv_end_flag = 0
        st.session_state.total_tokens = 0
        st.session_state.prompt_tokens = 0
        st.session_state.completion_tokens = 0
        st.session_state.total_cost = 0.0
        st.session_state.hotels_df = None  # Clear hotels
        st.session_state.itinerary = None  # Clear itinerary

    if st.session_state.conv_end_flag == 1:
        chat_btn = st.button("resume chat")
        if chat_btn:
            st.session_state.conv_end_flag = 0
            time.sleep(2)
            st.rerun()


# initialize chat ( replace with other models later)
chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

flag_llm = ChatOpenAI(
    model="gpt-4o", temperature=0.7, max_tokens=None, timeout=None, max_retries=2
)

chat_llm = ChatOpenAI(
    model="gpt-4" if model == "gpt-4" else "gpt-4o",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


search = GoogleSearchAPIWrapper()

# Create a Tool instance for the agent
search_tool = Tool(
    name="google_search",
    description="Search Google for recent information.",
    func=search.run,
)


# load prompts
with open("prompts\chat_prompts.yaml", "r") as file:
    prompt_data = yaml.safe_load(file)

# Create the system message that includes instructions about using search
system_message = prompt_data["system_chat_template1"]


# Initialize the agent with additional formatting instructions
agent = initialize_agent(
    tools=[search_tool],
    llm=chat_llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={"system_message": system_message},
)


# print(st.session_state.message_history)
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "hotels_df" in message:  # If message contains a DataFrame, display it
            st.dataframe(message["hotels_df"])

# Agent function

if st.session_state.conv_end_flag == 1:
    with st.spinner("Fetching the best deals for you"):
        st.divider()
        response = hotel_agent(st.session_state.message_history, True)
        hotels_df = pd.DataFrame(response)
        # Add hotels to message history with the DataFrame
        hotel_message = {
            "role": "assistant",
            "content": "I have found the best hotels for you!",
            "hotels_df": hotels_df,  # Store DataFrame directly in the message
        }
        st.session_state.messages.append(hotel_message)

        with st.chat_message("assistant"):
            st.markdown("I have found the best hotels for you!")
            st.dataframe(hotels_df)

        # Itinerary agent
    with st.spinner("Crafting the best itinerary for you"):
        itinerary = itinerary_agent(st.session_state.message_history, True)
        # Add itinerary to message history
        itinerary_message = {
            "role": "assistant",
            "content": f"I have the perfect itinerary crafted for you!\n\n{itinerary}",
        }
        st.session_state.messages.append(itinerary_message)

        with st.chat_message("assistant"):
            st.markdown("I have the perfect itinerary crafted for you!")
            st.markdown(itinerary)

    # Display cost metrics after conversation end
    st.sidebar.divider()
    st.sidebar.subheader("Final Usage Metrics")
    st.sidebar.write(f"Total Tokens: {st.session_state.total_tokens}")
    st.sidebar.write(f"Prompt Tokens: {st.session_state.prompt_tokens}")
    st.sidebar.write(f"Completion Tokens: {st.session_state.completion_tokens}")
    st.sidebar.write(f"Total Cost (USD): ${st.session_state.total_cost:.4f}")

# Chat
else:
    if prompt := st.chat_input("Hello there! How may i help you today?"):
        # Add user message to chat history
        # user questions
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.message_history += "Human Response:" + prompt + "\n"

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        prompt_ending = ChatPromptTemplate.from_messages(
            [("system", prompt_data["system_chat_ending"])]
        )

        chain_ending = prompt_ending | flag_llm

        response_ending = chain_ending.invoke(
            {"msg_history": st.session_state.message_history, "human_msg": prompt}
        )
        ending_flag = int(response_ending.content)
        print(ending_flag)

        if ending_flag == 1:
            st.session_state.conv_end_flag = 1
            with st.chat_message("assistant"):
                st.markdown(
                    "Thank you for provding all the information and confirming it. Have a pleasant day!"
                )
                time.sleep(2)
                st.rerun()
        else:
            with st.chat_message("assistant"):
                with get_openai_callback() as cb:
                    response1 = agent.invoke(
                        {
                            "input": prompt,
                            "chat_history": st.session_state.formatted_chat_history,
                            "current_year": current_year,
                        }
                    )
                    response = response1["output"]

                    # Display current call metrics in sidebar
                    st.sidebar.divider()
                    st.sidebar.subheader("Current Call Metrics")
                    st.sidebar.write(f"Total Tokens: {cb.total_tokens}")
                    st.sidebar.write(f"Prompt Tokens: {cb.prompt_tokens}")
                    st.sidebar.write(f"Completion Tokens: {cb.completion_tokens}")
                    st.sidebar.write(f"Cost (USD): ${cb.total_cost:.4f}")

                    # Update cumulative metrics
                    st.session_state.total_tokens += cb.total_tokens
                    st.session_state.prompt_tokens += cb.prompt_tokens
                    st.session_state.completion_tokens += cb.completion_tokens
                    st.session_state.total_cost += cb.total_cost

                    # Display cumulative metrics in sidebar expander
                    with st.sidebar.expander("View Cumulative Usage Metrics"):
                        st.write(f"Total Tokens: {st.session_state.total_tokens}")
                        st.write(f"Prompt Tokens: {st.session_state.prompt_tokens}")
                        st.write(
                            f"Completion Tokens: {st.session_state.completion_tokens}"
                        )
                        st.write(
                            f"Total Cost (USD): ${st.session_state.total_cost:.4f}"
                        )

                # for deepseek

                st.markdown(response)

                # Update both chat history formats
                st.session_state.formatted_chat_history.append(("human", prompt))

                # responses
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.session_state.message_history += (
                    "Agent Response:" + response + "\n\n"
                )
                st.session_state.formatted_chat_history.append(("assistant", response))
