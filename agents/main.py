import streamlit as st
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_chatbox import *
import time
import simplejson as json
from backend import bedrock_services
from common.utils import get_all_agent_name_as_list, get_agent_config_by_role


def _get_session():
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session.id

session_id = None
llm = FakeLLM()
chat_box_1 = ChatBox(
    use_rich_markdown=True, # use streamlit-markdown
    user_theme="green", # see streamlit_markdown.st_markdown for all available themes
    assistant_theme="blue",
)

chat_box = chat_box_1
chat_box.use_chat_name("Math") # add a chat conversatoin
 # add a chat conversatoin

def on_chat_change():
    chat_box.use_chat_name(st.session_state["chat_name"])
    chat_box.context_to_session() # restore widget values to st.session_state when chat name changed


with st.sidebar:
    st.subheader('Start to chat using streamlit')
    chat_name = st.selectbox("Chat Session:", get_all_agent_name_as_list(), key="chat_name", on_change=on_chat_change)
    chat_box.use_chat_name(chat_name)
    #streaming = st.checkbox('streaming', key="streaming")
    #in_expander = st.checkbox('show messages in expander', key="in_expander")
    #show_history = st.checkbox('show session state', key="show_history")
    streaming = True # disable streaming for this example
    in_expander = True # show messages in expander
    show_history = True # do not show session state

    chat_box.context_from_session(exclude=["chat_name"]) # save widget values to chat context

    st.divider()

    btns = st.container()

    file = st.file_uploader(
        "Load file to chat",
        #type=["pdf", "docx", "doc", "txt"],
    )

    if st.button("Load file") and file:
        data = json.load(file)
        chat_box.from_dict(data)


chat_box.init_session()
chat_box.output_messages()

def on_feedback(
    feedback,
    chat_history_id: str = "",
    history_index: int = -1,
):
    reason = feedback["text"]
    score_int = chat_box.set_feedback(feedback=feedback, history_index=history_index) # convert emoji to integer
    # do something
    st.session_state["need_rerun"] = True


feedback_kwargs = {
    "feedback_type": "thumbs",
    "optional_text_label": "wellcome to feedback",
}

if query := st.chat_input('input your question here'):
    chat_box.user_say(query)
    if streaming:
        import uuid
        import boto3

        if session_id is None:
            session_id = _get_session() # Get the current session ID
    
        agent_id = None  # Replace with your actual agent ID
        alias_id = None  # Replace with your actual alias ID
        region = None  # Replace with your actual AWS region

        config = get_agent_config_by_role(chat_name)
        print("###"*33)
        print(config)
        if config:
            agent_id = config.get("agent_id", agent_id)
            alias_id = config.get("alias_id", alias_id)
            region = config.get("region", region)
        #generator = llm.chat_stream(query)
     
        
        client = boto3.client(
                service_name = "bedrock-agent-runtime",
                region_name =  region,
            )
        
        generator = client.invoke_agent(
            agentId = agent_id,
            agentAliasId = alias_id,
            enableTrace = True,
            sessionId = session_id,
            inputText = query,
            streamingConfigurations = { 
            "applyGuardrailInterval" : 20,
            "streamFinalResponse" : False
            }
        )
        elements = chat_box.ai_say(
            [
                # you can use string for Markdown output if no other parameters provided
                Markdown("thinking", in_expander=in_expander,
                         expanded=True, title="answer"),
                #Markdown("", in_expander=in_expander, title="references"),
            ]
        )
        
        completion = ""
        for event in generator.get("completion"):
            if 'chunk' in event:
                chunk = event["chunk"]
                text = chunk["bytes"].decode()
                completion += text
                chat_box.update_msg(completion, element_index=0, streaming=True)
            # update the element without focus
            chat_box.update_msg(completion, element_index=0, streaming=False, state="complete")
            #chat_box.update_msg("\n\n".join(completion), element_index=1, streaming=False, state="complete")
            
        unique_feedback_key = f"chat_history_{len(chat_box.history) - 1}_{uuid.uuid4()}"
        chat_box.show_feedback(**feedback_kwargs,
                    key=unique_feedback_key,
                    on_submit=on_feedback,
                    kwargs={"chat_history_id": unique_feedback_key, "history_index": len(chat_box.history) - 1})
    else:
        print("Streaming is disabled, using non-streaming response.")