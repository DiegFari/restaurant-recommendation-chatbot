import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from helper import hide_sidebar

import streamlit as st

st.set_page_config(page_title="Post-Chatbot Survey 2", page_icon="🗳️", layout="centered")

UI_TYPE = "Ugly_UI"
NEXT_PAGE = "pages/08_finalmessage.py"

# ---------- Questions ----------
# Base (Likert 1–5), excluding NASA-TLX
BASE_QUESTIONS: List[Tuple[str, str]] = [
    ("personality_realistic_engaging", "The chatbot’s personality was realistic and engaging"),
    ("seemed_too_robotic", "The chatbot seemed too robotic"),
    ("welcoming_initial_setup", "The chatbot was welcoming during initial setup"),
    ("seemed_very_unfriendly", "The chatbot seemed very unfriendly"),
    ("explained_scope_purpose_well", "The chatbot explained its scope and purpose well"),
    ("no_indication_of_purpose", "The chatbot gave no indication as to its purpose"),
    ("easy_to_navigate", "The chatbot was easy to navigate"),
    ("easy_to_get_confused", "It would be easy to get confused when using the chatbot"),
    ("understood_me_well", "The chatbot understood me well"),
    ("failed_to_recognise_inputs", "The chatbot failed to recognise a lot of my inputs"),
    ("responses_useful_informative", "Chatbot responses were useful, appropriate and informative"),
    ("responses_irrelevant", "Chatbot responses were irrelevant"),
    ("coped_well_with_errors", "The chatbot coped well with any errors or mistakes"),
    ("unable_to_handle_errors", "The chatbot seemed unable to handle any errors"),
    ("very_easy_to_use", "The chatbot was very easy to use"),
    ("very_complex", "The chatbot was very complex"),
    ("filler1", "The chatbot serves to suggest you the best restaurant for your needs"),
    ("filler2", "The chatbot does not hold information about traffic in the city"),
    ("man_check", "The user interface of this chatbot was pretty and aesthetically pleasing"),
]

# NASA-TLX questions (at the end, different scale)
NASA_QUESTIONS: List[Tuple[str, str]] = [
    ("Nasa_tlx_1", "How mentally demanding was the interaction?"),
    ("Nasa_tlx_2", "How frustrated or irritated did you feel while interacting with the chatbot?"),
]

# Include binary goal_check in schema
FIXED_COLS: List[str] = (
    ["user_id", "ui_type", "timestamp_iso", "goal_check"]
    + [name for name, _ in BASE_QUESTIONS]
    + [name for name, _ in NASA_QUESTIONS]
    + ["comments", "task_id"]   
)


# ---------- Helpers ----------
def ensure_store():
    if "survey_responses" not in st.session_state:
        st.session_state["survey_responses"] = {}

def get_user_id():
    return st.session_state.get("user_id")

# Likert options shown to user; we map to numeric 1..5
LIKERT_OPTIONS = [
    "Strongly disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly agree",
]
SCORE_MAP = {label: i + 1 for i, label in enumerate(LIKERT_OPTIONS)}  # 1..5

# NASA-TLX custom Likert
NASA_OPTIONS = [
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High",
]
NASA_SCORE_MAP = {label: i + 1 for i, label in enumerate(NASA_OPTIONS)}  # 1..5

# ---------- UI ----------
st.title("🗳️ Post-Chatbot Survey 2")
st.markdown("After using this UI, please answer the goal check and rate each statement.")
hide_sidebar()

user_id = get_user_id()
if not user_id:
    st.warning("Missing required session context: set `st.session_state['user_id']` before visiting this page.")

st.divider()

# --- Goal check (NOT shuffled) ---
st.subheader("Goal Check")
goal_choice = st.radio(
    "Have you reached the goal? Did you find the restaurant and the required information?",
    options=["Yes", "No"],
    horizontal=True,
    key=f"{UI_TYPE}:goal_check_radio",
    index=None,  # no preselected option
)
goal_check = 1 if goal_choice == "Yes" else 0  # Binary 1/0

st.divider()
st.subheader("Rate your experience")

# One-time shuffle of BASE_QUESTIONS per session
order_key = f"q_order_{UI_TYPE}"
if order_key not in st.session_state:
    st.session_state[order_key] = list(range(len(BASE_QUESTIONS)))
    random.shuffle(st.session_state[order_key])

# Render radios for BASE_QUESTIONS with NO preselected option
answers: Dict[str, Optional[int]] = {}

for idx in st.session_state[order_key]:
    col_name, prompt = BASE_QUESTIONS[idx]
    widget_key = f"{UI_TYPE}:{col_name}"
    choice = st.radio(
        prompt,
        options=LIKERT_OPTIONS,
        index=None,           # no default selection
        horizontal=True,
        key=widget_key,
    )
    answers[col_name] = SCORE_MAP[choice] if choice else None

st.divider()
st.subheader("Final questions")

# Render NASA-TLX at the end (not shuffled), with custom scale and NO preselected option
for col_name, prompt in NASA_QUESTIONS:
    widget_key = f"{UI_TYPE}:{col_name}"
    choice = st.radio(
        prompt,
        options=NASA_OPTIONS,
        index=None,           # no default selection
        horizontal=True,
        key=widget_key,
    )
    answers[col_name] = NASA_SCORE_MAP[choice] if choice else None

comments = st.text_area(
    "Anything to add? (optional)",
    placeholder="Brief comments about this UI…",
    key=f"{UI_TYPE}:comments"
)

st.divider()

# Single primary action (no reset/shuffle buttons)
save_to_session = st.button("Save and continue the experiment", type="primary")

# ---------- Actions ----------
ensure_store()

if save_to_session:
    if not user_id:
        st.error("Cannot save: `user_id` missing from session.")
    else:
        row = {
            "user_id": user_id,
            "ui_type": UI_TYPE,
            "timestamp_iso": datetime.utcnow().isoformat(),
            "goal_check": goal_check,
            **{k: answers.get(k) for k, _ in BASE_QUESTIONS},
            **{k: answers.get(k) for k, _ in NASA_QUESTIONS},
            "comments": (comments or "").strip(),
            "task_id": st.session_state.get("task2_id"),
        }
        st.session_state["survey_responses"][UI_TYPE] = {k: row.get(k) for k in FIXED_COLS}
        st.success(f"Saved ratings for **{UI_TYPE}** to session.")
        st.balloons()
        st.switch_page(NEXT_PAGE)
