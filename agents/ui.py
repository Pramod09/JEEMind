import streamlit as st

from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx

import os
import boto3

import uuid
from bedrock_agent import chat_with_bedrock_agent
from agent_config import fetch_agent_config_by_role, agents_as_a_list

os.environ["STREAMLIT_SERVER_PORT"] = "80"

def _get_session():
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session.id

def maintain_session_history(agent_name):
    if "history" not in st.session_state:
        st.session_state["history"] = {}
    if agent_name not in st.session_state["history"]:
        st.session_state["history"][agent_name] = {"agent_name": agent_name, "conversations": []}
    return st.session_state["history"][agent_name]["conversations"]

def display_chat_history(agent_name):
    chat_history = maintain_session_history(agent_name)
    for entry in reversed(chat_history):
        st.write("---")
        st.write(f"**You:** {entry['query']}")
        st.write(f"**{agent_name}:** {entry['response']}")

#st.title("Interface to AI specilist doctors")
st.sidebar.header("Select an Agent")

agents = agents_as_a_list()

# Use selectbox for persistent agent selection (dropdown instead of radio)
if "selected_agent" not in st.session_state:
    st.session_state["selected_agent"] = agents[0]

selected_agent = st.sidebar.selectbox(
    "Select an Agent",
    agents,
    index=agents.index(st.session_state["selected_agent"])
)
st.session_state["selected_agent"] = selected_agent

# Main area for displaying interactions
st.markdown(f"<h4>Interacting with {selected_agent}</h4>", unsafe_allow_html=True)

# Input for user query at the bottom
user_query = st.text_input("Enter your query:", key="user_query")

# Initialize session state to maintain history
if "history" not in st.session_state:
    st.session_state["history"] = {}

if st.button("Submit"):
    if user_query:
        print("Agent selected - " + selected_agent)
        agent_conf = fetch_agent_config_by_role(selected_agent)

        
        session_id = None
        if session_id is None:
            session_id = _get_session()
         
        agent_id = agent_conf['agent_id']
        alias_id = agent_conf['alias_id']
        prompt = user_query
        ans = chat_with_bedrock_agent(st, agent_id = agent_id, 
                                    alias_id = alias_id, 
                                    region = agent_conf['region'], 
                                    user_input = prompt, 
                                    session_id = session_id)
    else:
        st.warning("Please enter a query before submitting.")