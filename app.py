import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from utils import get_deepseek_response

# load env vars
load_dotenv()

st.title("Travel Agent")


#sidebar
with st.sidebar:
    hist_btn = st.button('clear chat history')
    if hist_btn:
        st.session_state.messages = []
        st.session_state.message_history = ''




# initialize chat ( replace with other models later)
chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_history" not in st.session_state:
    st.session_state.message_history = ''

# print(st.session_state.message_history)
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Hello there! How may i help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_history += 'Human Response:' +  prompt + '\n'
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system = '''
        You are a helpful travel agent.
        You are supposed to maintain a conversation with the user to understand certain things
        You will maintain and ask questions until you receive the following information mentioned in double quotes:
        "country of visit"
        "number of days"
        "estimated budget for the trip"
        "date"

        You will be given a conversation history from which you will retrieve this information.
        "{msg_history}"

        Your response should strictly be the question you want to ask the user.
        Once you feel that you have all the information you want from the user, close by saying "Thanks for the information! We will get back to you!"
        You should follow a conversation and do not print out the conversation history.
        '''
        human = ""
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

        # for langchain compatible models use this
        chain = prompt | chat
        # response = chain.invoke({"msg_history": st.session_state.message_history})
        # for deepseek
        response = get_deepseek_response(system.format(msg_history = st.session_state.message_history),'')
        st.markdown(response)
    st.session_state.message_history += 'Agent Response:' + response + '\n\n'
    st.session_state.messages.append({"role": "assistant", "content": response})

    