import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from utils.utils import get_deepseek_response
from agents import hotel_agent_response,create_detailed_itinerary
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
import pandas as pd
import time
import datetime



# load env vars
load_dotenv()

st.title("Travel Agent")

# Get current year
current_year = datetime.datetime.now().year


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_history" not in st.session_state:
    st.session_state.message_history = ''

if "conv_end_flag" not in st.session_state:
    st.session_state.conv_end_flag = 0



#sidebar
with st.sidebar:
    hist_btn = st.button('clear chat history')
    
    if hist_btn:
        st.session_state.messages = []
        st.session_state.message_history = ''
        st.session_state.conv_end_flag = 0
    
    if st.session_state.conv_end_flag == 1:
        chat_btn = st.button('resume chat')
        if chat_btn:
            st.session_state.conv_end_flag = 0
            time.sleep(2)
            st.rerun()



# initialize chat ( replace with other models later)
chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2
)


# print(st.session_state.message_history)
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Agent function

if st.session_state.conv_end_flag == 1:     
    with st.spinner('Fetching the best deals for you'): 
        st.divider()   
        response = hotel_agent_response(st.session_state.message_history,True)
        hotels_df = pd.DataFrame(response)
        with st.chat_message('assistant'):
            st.markdown('I have found the best hotels for you!')
            st.dataframe(hotels_df)

        # Itinerary agent
    with st.spinner('Crafting the best itinerary for you'): 
        itinerary = create_detailed_itinerary(st.session_state.message_history,True)
        with st.chat_message('assistant'):
            st.markdown('I have the perfect itinerary crafted or you!')
            st.markdown(itinerary)

   
    


# Chat
else:
    if prompt := st.chat_input("Hello there! How may i help you today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.message_history += 'Human Response:' +  prompt + '\n'
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        system_msg_ending = '''
            You are an assistant tasked with determining if the user has confirmed their travel details.

            Review the user's response within the context of the latest question:

            """
            {msg_history}
            """

            Follow these steps:
            1. Fetch the latest question from the conversation history.
            2. Check if the latest question matches the format: "Just to confirm, you are planning a trip to [Country] for [Number of days] days, with an estimated budget of [Budget], starting from [Date]. Is that correct?"
            3. If the latest question matches this format, determine if the user's response below confirms the details:
                """
                {human_msg}
                """
            4. Return 1 if the user has confirmed the details. Return 0 if the user has not confirmed the details. Do not include any additional text in your response; only return the value 0 or 1.
        '''

        # print(prompt)
        prompt_ending = ChatPromptTemplate.from_messages([("system", system_msg_ending)])
        chain_ending = prompt_ending | llm
        response_ending = chain_ending.invoke({"msg_history":st.session_state.message_history,"human_msg" : prompt })
        ending_flag = int(response_ending.content)
        # ending_flag = get_deepseek_response(system_msg_ending.format(msg_history = st.session_state.message_history,human_msg = prompt),'')
        print(ending_flag)
        

        if ending_flag == 1 :
            st.session_state.conv_end_flag = 1
            with st.chat_message("assistant"):
                st.markdown('Thank you for provding all the information and confirming it. Have a pleasant day!')
                time.sleep(2)
                st.rerun()
        else:
            with st.chat_message("assistant"):

                # v2
                system = '''
                As a helpful travel agent, your goal is to gather necessary travel details from the user through a friendly and engaging conversation.

                Please adhere to the following guidelines:
                0. The current year is {current_year}. If the user does not mention the year when mentioning the check-in and check-out dates, mention the year while confirming
                1. Greet the user warmly and engage in a casual conversation.
                2. Ask one question at a time to gather the following information:
                * "Country of visit"
                * "Number of days"
                * "Estimated budget for the trip"
                * "Check-In Date and "Check-Out Date"
                3. Do not include any dialogue from the chat history in your response.

                Use the provided conversation history to check if any of the required information is already mentioned.
                Conversation History:
                """
                {msg_history}
                """

                Be conversational and include greetings, interjections, and friendly phrases to make the interaction seem human-like. Maintain a natural flow of conversation.

                Once you have collected all the necessary information, confirm the details with the user:
                "Just to confirm, you are planning a trip to [Country] for [Number of days] days, with an estimated budget of [Budget], starting from [Date]. Is that correct?"
                
                If the human says yes or please proceed or acknowledges the detials,end the conversation by thanking the human warmly if they want to proceed and have confirmed the details and offering additional support if necessary.
                '''
                human = ""
                prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

                # for langchain compatible models use this
                chain = prompt | llm
                response1 = chain.invoke({"msg_history": st.session_state.message_history,'current_year':current_year})
                response = response1.content
                # for deepseek


                # response = get_deepseek_response(system.format(msg_history = st.session_state.message_history),'')
                st.markdown(response)
            st.session_state.message_history += 'Agent Response:' + response + '\n\n'
            st.session_state.messages.append({"role": "assistant", "content": response})

