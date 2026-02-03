"""
This file only contains the save_to_file helper function.
Maybe more helper functions will get added that assist the API in some way.
This is not very likely though.
"""

# imports:
#//>>
from typing import Dict, Union, List
import random
import pandas as pd
from pandas import DataFrame
from statemachine import FSM
import os, csv, datetime, time, streamlit as st
import hashlib



INTERACTIONS_CSV = "data/interactions.csv"

def _now_iso():
    """Return current UTC time as ISO string."""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

def _ensure_csv(path=INTERACTIONS_CSV):
    """Make sure the interactions CSV exists with the correct header."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "session_id", "user_id", "task_id", "message_index", "role", "timestamp_iso",
                "content", "msg_len_chars",
                "latency_from_prev_s", "latency_from_other_role_s",
                "condition"
            ])

def _append_msg(role: str, content: str, condition: str):
    """Append a single user or assistant message to session buffer."""
    ts = time.time()
    st.session_state.message_index += 1
    lat_prev = None if st.session_state.prev_ts is None else round(ts - st.session_state.prev_ts, 3)

    if role == "assistant":
        lat_other = None if st.session_state.last_user_ts is None else round(ts - st.session_state.last_user_ts, 3)
        st.session_state.last_assistant_ts = ts
    else:
        lat_other = None if st.session_state.last_assistant_ts is None else round(ts - st.session_state.last_assistant_ts, 3)
        st.session_state.last_user_ts = ts

    st.session_state.prev_ts = ts
    user_id = st.session_state.get("user_id", "")
    task_id = st.session_state.get("current_task_id", "")

    st.session_state.interactions.append({
        "session_id": st.session_state.session_id,
        "user_id": user_id,
        "task_id": task_id,
        "message_index": st.session_state.message_index,
        "role": role,
        "timestamp_iso": _now_iso(),
        "content": content or "",
        "msg_len_chars": len(content or ""),
        "latency_from_prev_s": lat_prev,
        "latency_from_other_role_s": lat_other,
        "condition": condition
    })

def _flush_interactions_once(condition: str):
    """Write the buffered interactions for this page to disk (once only)."""
    if st.session_state.get("interactions_flushed"):
        return
    _ensure_csv()
    with open(INTERACTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in st.session_state.interactions:
            w.writerow([
                r["session_id"], r.get("user_id", ""), r.get("task_id", ""),
                r["message_index"], r["role"], r["timestamp_iso"],
                r["content"], r["msg_len_chars"], r["latency_from_prev_s"],
                r["latency_from_other_role_s"], r["condition"]
            ])
    st.session_state.interactions_flushed = True


TASKS = {
    "A": "Find an expensive restaurant in the north of the city. Any cuisine is fine. Also ask for it to be romantic. When found, fetch the address.",
    "B": "Find a moderate price restaurant in the north of town. Any cuisine is fine. Also ask that it has assigned seating. When found, ask for the phone number.",
}

def assign_task_order(user_id: str) -> list[str]:
    """Deterministic ~50/50 split based on user_id."""
    h = int(hashlib.sha256(user_id.encode()).hexdigest(), 16)
    return ["A", "B"] if (h % 2 == 0) else ["B", "A"]

#//<<

PATH: str = "user_data.csv"

def save_to_file(payload: Dict[str, Union[str, float]], path: str) -> None:
    #//>>
    """saves prior user info to dataset.

    This function saves all the user data that gets sent
    PRIOR to working with the dataset.
    Args:
        payload: [TODO:description]
        path: [TODO:description]
    """
    # 1. load the dataset:
    df: DataFrame = pd.read_csv(path)


    # 3. convert payload to dataframe:
    row: DataFrame = DataFrame([payload])

    # 4. concat the row to the original df:
    total: DataFrame = pd.concat([df, row], ignore_index=False)
    print(total)

    # 5. save the new dataframe
    total.to_csv(PATH)

    return None
    #//<<

def compute_answer(user_utterance: str, statemachine: FSM) -> str:
    #//>>
    """lets statemachine process user utterance and return output

    This function has the given statemachine process the user utterances in order to interpret what the user is saying.
    Then the statemachine also generates an output in the form of a string, which gets returned by this function.

    All the internal changes that happen should be maintained after the function ends,

    so if that requires a new statemachine object, feel free to return that too.
    Or just make it a global varianble or something. I don't care what you do, just don't butcher my code.

    Args:
        user_utterance: string variable depicting the user input
        statemachine: statemachine object that ought to process the user utterance

    Returns:
        string depicting the system utterance, in response to that of the user.
    """
    text = (user_utterance or "").strip()
    try:
        reply = statemachine.handle_input(text)
    except Exception:
        reply = "ERROR: Unable to compute answer"
    return reply
    #//<<

def say_hello(statemachine: FSM) -> str:
    try:
        hello = statemachine.get_prompt()
    except Exception:
        hello = "ERROR: Unable to retrieve hello message"
    return hello

def provide_task() -> str:
    #//>>
    """provides task for user for experiment

    This function randomly provides a task from a list of tasks within the function.
    The end-user is supposed to try to complete this task using the chatbot.
    All objectives have at least one associated restaurant.

    Returns:
        string containing objective/task for user
    """

    tasks: List[str] = ["Find an expensive restaurant in the north of the city. The restaurant can serve any food (you don't care about a specific cuisine). Also ask for the restaurant to be touristic. When you have found it, fetch the address.",
                        "Find a moderate price restaurant in the north of town. It can serve any food. Also ask for it to have with seats assigned. Once you have found it, ask for the phone number."
                        ]
    return random.choice(tasks)
    #//<<


def hide_sidebar():
    import streamlit as st
    st.markdown("""
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"], header {display: none !important;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


# testing:
#//>>
"""
if __name__ == "__main__":
    payload: Dict[str, Union[str, float]] = {"first_name": "alex",
                                             "last_name": "de Roode",
                                             "age": 22,
                                             "sex": "male"}

    save_to_file(payload, PATH)
"""
#//<<
