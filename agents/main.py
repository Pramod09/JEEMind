import streamlit as st
from pathlib import Path
import base64
import re
import html
import imghdr
import os
import boto3
import json

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


def normalize_markdown_for_ui(raw: str) -> str:
    """Normalize raw LLM output to clean markdown for UI rendering.

    - convert literal \n sequences into real newlines
    - collapse extra blank lines
    - fix double-backslashes for LaTeX
    - format inline option labels into list items
    """
    if not raw:
        return ""

    s = raw
    # Unescape common escape sequences produced by LLMs
    s = s.replace("\\r", "")
    s = s.replace("\\t", " ")
    s = s.replace("\\n", "\n")
    # Reduce doubled backslashes to single (so \\frac -> \frac for LaTeX)
    s = s.replace("\\\\", "\\")

    # If the text already looks like our formatted output (e.g. produced by
    # format_question), don't re-run aggressive label conversions which can
    # produce duplicated '**' markers. Detect existing Question header or
    # already-present labeled bullets like "- **A." and skip label recipes.
    already_formatted = bool(
        re.search(r"^\*\*Question:\*\*", s) or re.search(r"(?m)^[ \t]*-\s+\*\*[A-Z]\\.", s)
    )

    if not already_formatted:
        # Convert inline A) B) C) into list items if present
        if re.search(r"\bA[\)\.]\s*.*\bB[\)\.]", s, flags=re.S):
            s = re.sub(r"\s*([A-Z])[\)\.]\s*", r"\n- **\1.** ", s)

        # Convert leading label lines to bullets (A. option -> - **A.** option)
        s = re.sub(r"(?m)^[ \t]*([A-Z])[\.\)]\s+", r"- **\1.** ", s)

    # Collapse multiple blank lines
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    s = s.strip()
    return s


def format_question(text: str, fmt: str) -> str:
    """Robust top-level formatter for question-style LLM outputs.

    Returns a Markdown string with:
      - Question (bold)
      - Metadata line (italic) with Type | Topic | Difficulty when available
      - Options as bullet list items, each on its own line
      - A collapsible 'View answer' section if answer/solution is present

    This function prefers structured JSON parsing, and falls back to heuristics.
    It uses normalize_markdown_for_ui on extracted fields to keep LaTeX intact.
    """
    if not text:
        return ""
    fmt_norm = (fmt or "MCQ").lower()

    parsed = None
    try:
        parsed = json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                parsed = json.loads(m.group(0))
            except Exception:
                parsed = None

    if isinstance(parsed, dict):
        q = parsed.get("question") or parsed.get("prompt") or parsed.get("body") or ""
        opts = parsed.get("options") or parsed.get("choices") or []
        ans = parsed.get("answer") or parsed.get("solution") or parsed.get("correct") or ""
        qtype = parsed.get("type") or parsed.get("format") or fmt_norm.upper()
        topic = parsed.get("topic") or parsed.get("subject") or None
        difficulty = parsed.get("difficulty") or parsed.get("level") or None

        # Use a conservative sanitizer for parsed fields to avoid turning narrative
        # text into option bullets. This preserves LaTeX/backslashes while cleaning
        # literal escape sequences.
        def sanitize_text(s: str) -> str:
            if not s:
                return ""
            s2 = s.replace("\\r", "")
            s2 = s2.replace("\\t", " ")
            s2 = s2.replace("\\n", "\n")
            # collapse repeated blank lines
            s2 = re.sub(r"\n\s*\n+", "\n\n", s2)
            return s2.strip()

        def is_valid_option(opt: str) -> bool:
            if opt is None:
                return False
            t = str(opt).strip()
            if not t:
                return False
            # Exclude obvious narration/tool text or JSON artifacts
            blacklist = ["GET__", "tool", "I will", "I will provide", "```", "{", "}\n", '"type":', '"hint":']
            low = t.lower()
            for bad in blacklist:
                if bad.lower() in low:
                    return False
            # exclude very long non-option blocks (likely narration)
            if len(t) > 1000:
                return False
            return True

        out_lines = []
        if q:
            out_lines.append(f"**Question:** {sanitize_text(q)}")
            out_lines.append("")

        meta_items = []
        if qtype:
            meta_items.append(f"Type: {qtype}")
        if topic:
            meta_items.append(f"Topic: {topic}")
        if difficulty:
            meta_items.append(f"Difficulty: {difficulty}")
        if meta_items:
            out_lines.append("*" + " | ".join(meta_items) + "*")
            out_lines.append("")

        if isinstance(opts, (list, tuple)) and opts:
            # filter irrelevant/empty options
            opts = [o for o in opts if is_valid_option(o)]
            if opts:
                labels = [chr(ord("A") + i) for i in range(len(opts))]
                for lab, opt in zip(labels, opts):
                    out_lines.append(f"- **{lab}.** {sanitize_text(str(opt))}")
                out_lines.append("")

        if ans:
            out_lines.append(f"<details><summary><b>View answer</b></summary>\n\n<pre>{html.escape(str(ans))}</pre>\n</details>")

        return "\n".join(out_lines)

    # Fallback: heuristics for plain text
    if fmt_norm in ("mcq", "msq"):
        s = normalize_markdown_for_ui(text)
        # try to split question and options
        lines = [ln for ln in s.splitlines() if ln.strip()]
        if not lines:
            return s
        # Find option lines (starting with A., A), or a bullet)
        opt_idx = None
        for i, ln in enumerate(lines):
            if re.match(r'^[A-Za-z][\)\.].*', ln) or re.match(r'^-\s+\*\*?[A-Za-z]', ln) or re.match(r'^[A-Z]\.', ln):
                opt_idx = i
                break
        if opt_idx is None and len(lines) > 1:
            q = lines[0]
            opts = lines[1:]
        elif opt_idx is not None:
            q = " ".join(lines[:opt_idx])
            opts = lines[opt_idx:]
        else:
            return s

        out = []
        if q:
            out.append(f"**Question:** {q}")
            out.append("")
        # filter irrelevant/empty options in fallback
        opts = [o for o in opts if is_valid_option(o)]
        labels = [chr(ord('A') + i) for i in range(len(opts))]
        for lab, opt in zip(labels, opts):
            opt_clean = re.sub(r'^[A-Za-z0-9\-\*\u2022\)\.\(\s]+', '', opt).strip()
            out.append(f"- **{lab}.** {opt_clean}")
        return "\n".join(out)

    if fmt_norm in ("numeric/integer", "numeric", "integer"):
        s = normalize_markdown_for_ui(text)
        return "Answer (numeric):\n\n```\n" + s + "\n```"

    # Passage or default: normalize and return
    return normalize_markdown_for_ui(text)

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
    # with selector_col2:
    #     question_format = st.selectbox(
    #         "Format",
    #         options=["MCQ", "MSQ", "Numeric/Integer", "Passage-based"],
    #         key="question_format",
    #         index=0,
    #     )
    # Optional: ensure selectboxes have a minimum width via HTML/CSS
    st.markdown(
        """
        <style>
        /* Increase the width of selectbox containers in the sidebar */
        .sidebar .stSelectbox > div[data-baseweb] { min-width: 180px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    #streaming = st.checkbox('streaming', key="streaming")
    #in_expander = st.checkbox('show messages in expander', key="in_expander")
    #show_history = st.checkbox('show session state', key="show_history")
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

    # Question Generation Mode description area
    # fmt_colA, fmt_colB = st.columns([1, 4])
    # with fmt_colB:
    #     st.markdown("**Question Generation Mode**")
    #     st.markdown(
    #         """
    #         This is the core mode for creating IIT-JEE Advanced–level questions in various formats:

    #         | Format         | Description                                                                 |
    #         |----------------|-----------------------------------------------------------------------------|
    #         | MCQ            | Single correct option                                                       |
    #         | MSQ            | Multiple correct options                                                    |
    #         | Numeric/Integer| Answers are numerical values (integer or decimal)                           |
    #         | Passage-based  | Linked questions based on a common mathematical context or derivation       |
    #         """
    #     )

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
      
        if config:
            agent_id = config.get("agent_id", agent_id)
            alias_id = config.get("alias_id", alias_id)
            region = config.get("region", region)
        #generator = llm.chat_stream(query)
     
        
        # Ensure region is set; prefer explicit config, then env vars, then boto3 session, else default
        if not region:
            region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or boto3.session.Session().region_name
            if not region:
                region = "us-east-1"
                try:
                    st.warning(f"No AWS region configured for agent calls; defaulting to {region}. Set region in agent config or AWS_REGION env var.")
                except Exception:
                    pass

        client = boto3.client(
                service_name = "bedrock-agent-runtime",
                region_name = region,
            )
        
        # Include the selected question format so the agent can generate the requested type
        fmt = st.session_state.get("question_format", "MCQ")
        # Always prefix the query with an explicit format marker the agent can parse
        #input_payload = f"[QUESTION_FORMAT:{fmt}]\n{query}"
        input_payload = query
        # Ensure we have a session id
        if session_id is None:
            session_id = _get_session()
        
        generator = client.invoke_agent(
            agentId = agent_id,
            agentAliasId = alias_id,
            enableTrace = True,
            sessionId = session_id,
            inputText = input_payload,
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
        
        # Use top-level formatter
        pass

        completion = ""
        fmt = st.session_state.get("question_format", "MCQ")
        last_displayed = None
        for event in generator.get("completion"):
            if 'chunk' in event:
                chunk = event["chunk"]
                text = chunk["bytes"].decode()
                completion += text
                # format partial output for streaming display
                try:
                    display_text = format_question(completion, fmt)
                except Exception:
                    display_text = completion
                # Only update the UI when the formatted display changes to avoid sticking on first chunk
                if display_text != last_displayed:
                    chat_box.update_msg(normalize_markdown_for_ui(display_text), element_index=0, streaming=True)
                    last_displayed = display_text

        print("session_id:", session_id)
        print("input_payload:", input_payload)
        print("completion:", completion)
        print("Displayed text:", display_text)
        print("###"*33)
     
        # final update when complete - always push final formatted text and mark complete
        try:
            final_text = format_question(completion, fmt)
        except Exception:
            final_text = completion
        # If final_text differs from last_displayed, replace; otherwise still mark as complete
        # Push the final formatted and normalized text to the UI and mark the message complete.
        chat_box.update_msg(normalize_markdown_for_ui(final_text), element_index=0, streaming=False, state="complete")
        
        #chat_box.update_msg("\n\n".join(completion), element_index=1, streaming=False, state="complete")

        unique_feedback_key = f"chat_history_{len(chat_box.history) - 1}_{uuid.uuid4()}"
        chat_box.show_feedback(**feedback_kwargs,
                    key=unique_feedback_key,
                    on_submit=on_feedback,
                    kwargs={"chat_history_id": unique_feedback_key, "history_index": len(chat_box.history) - 1})
    else:
        print("Streaming is disabled, using non-streaming response.")