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

if "conv_end_flag" not in st.session_state:
    st.session_state.conv_end_flag = 0


# sidebar
with st.sidebar:
    hist_btn = st.button("clear chat history")

    model = st.radio("Choose chat model:", ["gpt", "deepseek"])

    if hist_btn:
        st.session_state.messages = []
        st.session_state.message_history = ""
        st.session_state.conv_end_flag = 0

    if st.session_state.conv_end_flag == 1:
        chat_btn = st.button("resume chat")
        if chat_btn:
            st.session_state.conv_end_flag = 0
            time.sleep(2)
            st.rerun()


# initialize chat ( replace with other models later)
chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

llm = ChatOpenAI(
    model="gpt-4o", temperature=0.7, max_tokens=None, timeout=None, max_retries=2
)

llm1 = ChatOpenAI(
    model="gpt-4", temperature=0.7, max_tokens=None, timeout=None, max_retries=2
)

# load prompts
with open("prompts\chat_prompts.yaml", "r") as file:
    prompt_data = yaml.safe_load(file)


# print(st.session_state.message_history)
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Agent function

if st.session_state.conv_end_flag == 1:
    with st.spinner("Fetching the best deals for you"):
        st.divider()
        response = hotel_agent(st.session_state.message_history, True)
        hotels_df = pd.DataFrame(response)
        with st.chat_message("assistant"):
            st.markdown("I have found the best hotels for you!")
            st.dataframe(hotels_df)

        # Itinerary agent
    with st.spinner("Crafting the best itinerary for you"):
        itinerary = itinerary_agent(st.session_state.message_history, True)
        with st.chat_message("assistant"):
            st.markdown("I have the perfect itinerary crafted or you!")
            st.markdown(itinerary)


# Chat
else:
    if prompt := st.chat_input("Hello there! How may i help you today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.message_history += "Human Response:" + prompt + "\n"
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # print(prompt)
        prompt_ending = ChatPromptTemplate.from_messages(
            [("system", prompt_data["system_chat_ending"])]
        )
        chain_ending = prompt_ending | llm
        if model == "gpt":
            response_ending = chain_ending.invoke(
                {"msg_history": st.session_state.message_history, "human_msg": prompt}
            )
            ending_flag = int(response_ending.content)
        elif model == "deepseek":
            ending_flag = get_deepseek_response(
                prompt_data["system_chat_ending"].format(
                    msg_history=st.session_state.message_history, human_msg=prompt
                ),
                "",
            )
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
                prompt = ChatPromptTemplate.from_messages(
                    [("system", prompt_data["system_chat_template"])]
                )

                # for langchain compatible models use this
                chain = prompt | llm1

                if model == "gpt":
                    response1 = chain.invoke(
                        {
                            "msg_history": st.session_state.message_history,
                            "current_year": current_year,
                        }
                    )
                    response = response1.content
                # for deepseek
                elif model == "deepseek":
                    response = get_deepseek_response(
                        prompt_data["system_chat_template"].format(
                            msg_history=st.session_state.message_history,
                            current_year=current_year,
                        ),
                        "",
                    )
                st.markdown(response)
            st.session_state.message_history += "Agent Response:" + response + "\n\n"
            st.session_state.messages.append({"role": "assistant", "content": response})
