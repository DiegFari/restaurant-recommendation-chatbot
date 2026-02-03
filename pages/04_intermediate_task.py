# pages/03_intermediate_task.py
import random, time
import streamlit as st
from helper import hide_sidebar

st.set_page_config(page_title="Intermediate Task", page_icon="🧩", layout="wide")

# ----------------------------
# CONFIG
# ----------------------------
TRIALS_PER_SECTION = 5
GRID_R, GRID_C = 2, 3                    # 6 blocks total
TOTAL_CELLS = GRID_R * GRID_C            # = 6

NEXT_PAGE = "04_questions.py"

# ----------------------------
# SESSION STATE INIT
# ----------------------------
if "inter_seed" not in st.session_state:
    st.session_state.inter_seed = int(time.time())

# Blue task state
st.session_state.setdefault("blue_round", 0)       # 0..TRIALS_PER_SECTION
st.session_state.setdefault("blue_misclicks", 0)

# Odd-one-out state
st.session_state.setdefault("odd_round", 0)
st.session_state.setdefault("odd_misclicks", 0)

# ----------------------------
# HELPERS
# ----------------------------
def stable_rng(seed):
    """Return a random.Random seeded object (stable across reruns)."""
    r = random.Random()
    r.seed(seed)
    return r

def grid_buttons(symbols, prefix, disabled=False):
    """Render a 2x3 grid of buttons with given symbols, return index clicked or None."""
    idx_clicked = None
    i = 0
    for r in range(GRID_R):
        cols = st.columns(GRID_C, gap="small")
        for c in range(GRID_C):
            clicked = cols[c].button(symbols[i], key=f"{prefix}_{i}", disabled=disabled)
            if clicked and idx_clicked is None:
                idx_clicked = i
            i += 1
    return idx_clicked

st.title("Intermediate Task")
st.markdown("In this brief section, you just have to complete two simple games.\n As you see there are two tabs. Follow the instructions on the tabs and have fun with the game, then, you can go on with the experiment.")
hide_sidebar()

tabs = st.tabs(["🔵 Find the Blue Box", "🧩 Odd One Out"])

# =========================================================
# 1) Find the Blue Box (6 buttons, exactly one 🟦)
# =========================================================
with tabs[0]:
    st.subheader(f"Round {min(st.session_state.blue_round + 1, TRIALS_PER_SECTION)} of {TRIALS_PER_SECTION}")
    st.caption("Click the blue square (🟦).")

    if st.session_state.blue_round >= TRIALS_PER_SECTION:
        st.success(f"Completed {TRIALS_PER_SECTION} rounds ✅  | Misclicks: {st.session_state.blue_misclicks}")
    else:
        # stable layout for this round
        r = stable_rng(st.session_state.inter_seed + 1000 + st.session_state.blue_round)
        blue_idx = r.randrange(TOTAL_CELLS)
        symbols = ["🟦" if i == blue_idx else "⬛" for i in range(TOTAL_CELLS)]

        fb = st.empty()
        clicked = grid_buttons(symbols, prefix=f"blue_r{st.session_state.blue_round}")

        if clicked is not None:
            if clicked == blue_idx:
                fb.success("Correct! Moving to the next round…")
                st.session_state.blue_round += 1
                st.rerun()

            else:
                st.session_state.blue_misclicks += 1
                fb.error("Nope — try again!")

# =========================================================
# 2) Odd One Out (6 buttons, one breaks the pattern)
# =========================================================
with tabs[1]:
    st.subheader(f"Round {min(st.session_state.odd_round + 1, TRIALS_PER_SECTION)} of {TRIALS_PER_SECTION}")
    st.caption("Click the item that does not fit the pattern.")

    if st.session_state.odd_round >= TRIALS_PER_SECTION:
        st.success(f"Completed {TRIALS_PER_SECTION} rounds ✅  | Misclicks: {st.session_state.odd_misclicks}")
    else:
        # Choose a pattern for this round deterministically
        patterns = [
            ("🟩", "🟥"),
            ("⚪️", "⚫️"),
            ("🔺", "🔷"),
            ("🟨", "🟦"),
            ("🟪", "⬜️"),
        ]
        r = stable_rng(st.session_state.inter_seed + 2000 + st.session_state.odd_round)
        common_sym, odd_sym = r.choice(patterns)
        odd_idx = r.randrange(TOTAL_CELLS)
        symbols = [odd_sym if i == odd_idx else common_sym for i in range(TOTAL_CELLS)]

        fb2 = st.empty()
        clicked2 = grid_buttons(symbols, prefix=f"odd_r{st.session_state.odd_round}")

        if clicked2 is not None:
            if clicked2 == odd_idx:
                fb2.success("Correct! Moving to the next round…")
                st.session_state.odd_round += 1
                st.rerun()

            else:
                st.session_state.odd_misclicks += 1
                fb2.error("That matches the pattern — look for the misfit!")

# =========================================================
# Footer / Continue
# =========================================================
st.divider()
ready = (
    st.session_state.blue_round >= TRIALS_PER_SECTION
    and st.session_state.odd_round  >= TRIALS_PER_SECTION
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if ready:
        st.success("Great job! Both sections completed.")
        if st.button("Continue with the rest of the experiment", type="primary", key="go_next"):
            st.switch_page("pages/05_Chatbotinstructions2.py") 
    else:
        st.info("Finish all 5 rounds in both sections to continue.")

