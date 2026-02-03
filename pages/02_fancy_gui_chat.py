"""
This is the file responsible for portraying the fancy GUI through streamlit.
In order for the statemachine to work accordingly, I expect this file to rely on the compute_answer function from helpers.py
"""

# imports:
#//>>
import streamlit as st, time
from statemachine import FSM
from helper import compute_answer, hide_sidebar, TASKS, assign_task_order, _append_msg, _flush_interactions_once
import os, csv, uuid, datetime


INTERACTIONS_CSV = "data/interactions.csv"
CONDITION = "chatbot_fancy"



# set configuration of the page

st.set_page_config(page_title="Chatbot 1", page_icon="🤖")

# make a custom CSS for dark theme + chat bubble colors
st.markdown("""
    <style>
        /* App background */
        .stApp {
            background-color: #000000;
            color: white;
        }

        /* Assistant + User message bubbles (same dark background) */
        .stChatMessage[data-testid="stChatMessage-assistant"],
        .stChatMessage[data-testid="stChatMessage-user"] {
            background-color: #000000 !important;  /* fully black */
            color: white !important;
            border: none !important;
            padding: 0.5rem 0.75rem !important;
        }

        /* --- Chat input area (bottom bar) --- */
        section[data-testid="stChatInput"] {
            background-color: #000000 !important;  /* full black bar */
            border-top: 1px solid #222222 !important;
        }
            
        section[data-testid="stChatInput"] textarea:focus {
            border-color: #555555 !important;
            outline: none !important;
            box-shadow: 0 0 6px #444444 !important;
        }

        /* Send button (arrow) */
        section[data-testid="stChatInput"] button {
            background-color: transparent !important;
            color: #cccccc !important;
        }
        section[data-testid="stChatInput"] button:hover {
            color: white !important;
        }

        /* Captions, text, buttons */
        .stMarkdown, .stCaption {
            color: #cccccc !important;
        }
        .stCheckbox label, .stButton button {
            color: white !important;
        }
        .stButton button {
            background-color: #333333;
            border: 1px solid #666666;
        }
        .stButton button:hover {
            background-color: #444444;
        }
    </style>
""", unsafe_allow_html=True)

hide_sidebar()

if not st.session_state.get("user_id"):
    st.error("Missing user_id; cannot assign tasks deterministically.")
    st.stop()



   
NEXT_PAGE = "pages/03_Pretty_UI_questions.py"


# Title and task
st.title("CHATBOT ONE 🤖")

#  Assign order deterministically
st.session_state.setdefault("task_order", assign_task_order(st.session_state["user_id"]))
order = st.session_state["task_order"]          # e.g., ["A","B"]

#  Define IDs/texts first
st.session_state.setdefault("task1_id", order[0])
st.session_state.setdefault("task2_id", order[1])
st.session_state.setdefault("task1_text", TASKS[order[0]])
st.session_state.setdefault("task2_text", TASKS[order[1]])

#  Now it's safe to tag the current page with the correct task
st.session_state["current_task_id"] = st.session_state["task1_id"]  # "A" or "B"

#  Show the task
task = st.session_state["task1_text"]
st.markdown(f"**Your task is:** {task}")




# 1. Initialize chat history and statemachine and save it to session state to retain message history:

st.session_state.setdefault("session_id", uuid.uuid4().hex)
if "statemachine" not in st.session_state:
    st.session_state.statemachine = FSM()
st.session_state.setdefault("chat1_start_ts", time.time())
st.session_state.setdefault("chat1_done", False)

# logging buffers/trackers
st.session_state.setdefault("interactions", [])
st.session_state.setdefault("interactions_flushed", False)
st.session_state.setdefault("message_index", 0)
st.session_state.setdefault("prev_ts", None)
st.session_state.setdefault("last_user_ts", None)
st.session_state.setdefault("last_assistant_ts", None)

# initial assistant message — create once, render, and BUFFER it
if "messages" not in st.session_state:
    seed = "Hello, welcome to B2's restaurant finder, please inform us of a pricerange, area and foodtype you are interested in"
    st.session_state.messages = [{"role": "assistant", "content": seed}]
    _append_msg("assistant", seed, CONDITION)


# 2. Display chat messages from history on app rerun

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# 3. React to user input

response: str = ""
if prompt := st.chat_input("Type here..."):
    # user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    _append_msg("user", prompt, CONDITION)

    # assistant
    response = compute_answer(prompt, st.session_state.statemachine)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    _append_msg("assistant", response, CONDITION)



# 4. Direct user to next page when done

st.divider()

# 5. set checkbox for reaching goal:
st.checkbox("I wan to end the interaction", key="chat1_done")
if st.session_state.get("chat1_done") and st.button("Continue → Next Task"):
    _flush_interactions_once(CONDITION)
    st.switch_page(NEXT_PAGE)

# implement timer logic:
TIME_LIMIT_SECONDS: int = 60*5
timer_placeholder = st.empty()
elapsed: int = int(time.time() - st.session_state.chat1_start_ts)
remaining: int = max(0, TIME_LIMIT_SECONDS - elapsed)
mm, ss = divmod(remaining, 60)
timer_placeholder.caption(f"⏳ Time remaining: **{mm:02d}:{ss:02d}**")

if remaining > 0:
    time.sleep(1)
    st.rerun()
else:
    st.session_state["chat1_done"] = True
    _flush_interactions_once(CONDITION)
    st.switch_page(NEXT_PAGE)
