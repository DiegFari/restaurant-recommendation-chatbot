import streamlit as st
from typing import List
from helper import compute_answer, hide_sidebar,  _append_msg, _flush_interactions_once
from statemachine import FSM
import os, csv, uuid, datetime, time
from typing import List 



INTERACTIONS_CSV = "data/interactions.csv"
CONDITION = "chatbot_ugly"

# ---------------- UI + state ----------------
st.set_page_config(page_title="Chatbot 2", layout="centered")
st.markdown("""
<style>
  .stApp { background-color:black; color:#00ff00; font-family:monospace; }
  .stTextInput > div > div > input {
      background-color:black !important; color:#00ff00 !important;
      font-family:monospace !important; border:none !important; caret-color:#00ff00 !important;
  }
  .task-box { border:1px solid #00ff00; background:#000; color:#00ff00; font-family:monospace;
              padding:10px 14px; border-radius:6px; margin:12px 0 8px 0; line-height:1.4; }
  .task-box b { color:#00ff00; }
</style>
""", unsafe_allow_html=True)

hide_sidebar()

if not st.session_state.get("user_id"):
    st.error("Missing user_id; cannot proceed.")
    st.stop()
if "task2_text" not in st.session_state:
    st.error("Missing task assignment (task2_text). Did the first chatbot set it?")
    st.stop()


# ---- Stable session id across pages
st.session_state.setdefault("session_id", uuid.uuid4().hex)

# ---- One-time page initialization (CRITICAL)
if "cb2_init" not in st.session_state:
    st.session_state["interactions"] = []
    st.session_state["interactions_flushed"] = False
    st.session_state["message_index"] = 0
    st.session_state["prev_ts"] = None
    st.session_state["last_user_ts"] = None
    st.session_state["last_assistant_ts"] = None
    st.session_state["current_task_id"] = st.session_state["task2_id"]  # "A" or "B"


    st.session_state["cli_start_ts"] = time.time()
    st.session_state["history_cli"] = [
        "Hello, welcome to B2's restaurant finder, please inform us of a pricerange, area and foodtype you are interested in"
    ]
    _append_msg("assistant", st.session_state["history_cli"][0], CONDITION)
    st.session_state["cli_seed_logged"] = True

    st.session_state["statemachine_cb2"] = FSM()

    st.session_state["cb2_init"] = True



fsm = st.session_state["statemachine_cb2"]
task = st.session_state["task2_text"]         


# timer + next page
TIME_LIMIT = 5 * 60
NEXT_PAGE = "pages/07__Ugly_UI_questions.py"

st.title("CHATBOT TWO")
st.markdown(f"<div class='task-box'><b>Task:</b> {task}</div>", unsafe_allow_html=True)

elapsed = int(time.time() - st.session_state["cli_start_ts"])
remaining = max(0, TIME_LIMIT - elapsed)
mm, ss = divmod(remaining, 60)
st.caption(f"⏳ Time remaining: **{mm:02d}:{ss:02d}**")

# Render scrollback
history: List[str] = st.session_state["history_cli"]
formatted_history = ""
for msg in history[-50:]:
    if msg.startswith(">>>"):
        formatted_history += f"<div style='color:#00ff00; margin-top:10px;'><b>{msg}</b></div>"
    else:
        formatted_history += f"<div style='color:#00ff00; margin-left:20px; margin-bottom:10px;'>{msg}</div>"

st.markdown(
    f"""
    <div style='background-color:black; font-family:monospace; 
                border:1px solid #00ff00; border-radius:6px; 
                padding:10px 14px; font-size:18px;'>{formatted_history}</div>
    """,
    unsafe_allow_html=True
)

def process_prompt():
    prompt = st.session_state.get("prompt", "")
    if not prompt:
        return

    # Log user message
    _append_msg("user", prompt, CONDITION)

    # Compute assistant response
    answer = compute_answer(user_utterance=prompt, statemachine=fsm)
    _append_msg("assistant", answer, CONDITION)

    # Update history in session (persist across reruns)
    history = st.session_state["history_cli"]
    history.append(f">>> {prompt}")
    history.append(answer)
    st.session_state["history_cli"] = history

    # Clear input
    st.session_state["prompt"] = ""

# CLI input: submit on Enter
st.text_input(
    "restaurant-cli$",
    key="prompt",
    label_visibility="collapsed",
    on_change=process_prompt
)

st.divider()
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.checkbox("I wan to end the interaction", key="chat1_done")
    if st.session_state.get("chat1_done") and st.button("Continue → Next Task"):
        _flush_interactions_once(CONDITION)
        st.switch_page(NEXT_PAGE)

# timeout / heartbeat
if remaining == 0:
    st.success("⏰ Time's up! Moving to the next part…")
    _flush_interactions_once(CONDITION)
    time.sleep(1)
    st.switch_page(NEXT_PAGE)
else:
    time.sleep(1)
    st.rerun()
