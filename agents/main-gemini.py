import streamlit as st
from pathlib import Path
import base64

import imghdr
import os
import boto3
from gemini.testModel import invoke_gemini_api

# Set page config early so Streamlit uses the desired layout and title
st.set_page_config(page_title="JEEMind", layout="wide")

from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_chatbox import *


# Display a top-left logo if a JPEG is placed at agents/logo.jpeg or agents/logo.jpg
def _display_top_left_logo(names=("logo",), exts=("jpeg", "jpg", "png", "webp"), width: int = 80, debug: bool = False):
    """Search common locations for a logo file, detect its type, and embed it top-left.

    Search order (first match wins):
      - agents/<name>.<ext>
      - agents/assets/<name>.<ext>
      - <workspace_root>/<name>.<ext>
      - <workspace_root>/assets/<name>.<ext>
    """
    try:
        base_dir = Path(__file__).parent
        workspace_root = Path.cwd()

        search_dirs = [
            base_dir,
            base_dir / "assets",
            workspace_root,
            workspace_root / "assets",
        ]

        logo_path = None
        # Case-insensitive search: check by comparing lowercased names
        for d in search_dirs:
            if not d.exists():
                continue
            for entry in d.iterdir():
                entry_name = entry.name.lower()
                for name in names:
                    for ext in exts:
                        target = f"{name.lower()}.{ext.lower()}"
                        if entry_name == target:
                            logo_path = entry
                            break
                    if logo_path:
                        break
                if logo_path:
                    break
            if logo_path:
                break

        if not logo_path:
            return

        raw = logo_path.read_bytes()
        kind = imghdr.what(None, raw)
        # Fallback: use file suffix if imghdr couldn't detect
        if not kind:
            kind = logo_path.suffix.lstrip('.').lower()

        mime = 'image/' + ('jpeg' if kind == 'jpg' else kind)
        data = base64.b64encode(raw).decode()

        img_html = f"""
        <style>
        .top-left-logo {{
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 9999;
            pointer-events: none; /* allow clicks through the logo */
        }}
        .top-left-logo img {{
            width: {width}px;
            height: auto;
            border-radius: 4px;
            display:block;
        }}
        @media (max-width: 600px) {{
            .top-left-logo {{ display: none; }}
        }}
        </style>
        <div class="top-left-logo">
            <img src="data:{mime};base64,{data}" alt="logo">
        </div>
        """

        st.markdown(img_html, unsafe_allow_html=True)
        if debug:
            # Small non-intrusive indicator in the sidebar about which logo was used
            try:
                with st.sidebar:
                    st.info(f"Logo loaded from: {str(logo_path)}")
            except Exception:
                pass
    except Exception:
        # Safe-fail: never raise from logo rendering
        return


def find_logo_path(names=("logo",), exts=("jpeg", "jpg", "png", "webp")):
    """Return a Path to the first matching logo file in common locations, or None."""
    base_dir = Path(__file__).parent
    workspace_root = Path.cwd()
    search_dirs = [
        base_dir,
        base_dir / "assets",
        workspace_root,
        workspace_root / "assets",
    ]
    for d in search_dirs:
        if not d.exists():
            continue
        for entry in d.iterdir():
            name = entry.name.lower()
            for n in names:
                for ext in exts:
                    if name == f"{n.lower()}.{ext.lower()}":
                        return entry
    return None
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
    # Show logo (if available) inline with the subheader
    logo_path = find_logo_path()
    cols = st.columns([1, 6])
    with cols[0]:
        if logo_path:
            try:
                st.image(str(logo_path), width=64)
            except Exception:
                pass
    with cols[1]:
        st.subheader('JEE Insight ')

    # Place Chat Session and Format selectors on one line with controlled widths
    selector_col1, selector_col2 = st.columns([3, 2])
    with selector_col1:
        chat_name = st.selectbox("Chat Session:", get_all_agent_name_as_list(), key="chat_name", on_change=on_chat_change)
        chat_box.use_chat_name(chat_name)
    
    st.markdown(
        """
        <style>
        /* Increase the width of selectbox containers in the sidebar */
        .sidebar .stSelectbox > div[data-baseweb] { min-width: 180px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    streaming = True # disable streaming for this example
    in_expander = True # show messages in expander
    show_history = True # do not show session state

    chat_box.context_from_session(exclude=["chat_name"]) # save widget values to chat context
    # Ensure a default question format is always present in session state
    try:
        if "question_format" not in st.session_state:
            st.session_state["question_format"] = "MCQ"
    except Exception:
        # defensive: if Streamlit session isn't available yet, ignore
        pass

    st.divider()
    btns = st.container()

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
        print(config)
       
        input_payload = query
        # Ensure we have a session id
        if session_id is None:
            session_id = _get_session()
       
        elements = chat_box.ai_say(
            [
                # you can use string for Markdown output if no other parameters provided
                Markdown("thinking", in_expander=in_expander,
                         expanded=True, title="answer"),
                #Markdown("", in_expander=in_expander, title="references"),
            ]
        )
        

        completion = invoke_gemini_api(input_payload)

        print("session_id:", session_id)
        print("input_payload:", input_payload)
        print("completion:", completion)
        final_text = completion
        print("###"*33)
     
        # final update when complete - always push final formatted text and mark complete
        chat_box.update_msg(final_text, element_index=0, streaming=False, state="complete")
        
        #chat_box.update_msg("\n\n".join(completion), element_index=1, streaming=False, state="complete")

        unique_feedback_key = f"chat_history_{len(chat_box.history) - 1}_{uuid.uuid4()}"
        chat_box.show_feedback(**feedback_kwargs,
                    key=unique_feedback_key,
                    on_submit=on_feedback,
                    kwargs={"chat_history_id": unique_feedback_key, "history_index": len(chat_box.history) - 1})
    else:
        print("Streaming is disabled, using non-streaming response.")