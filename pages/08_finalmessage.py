import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from helper import hide_sidebar

st.set_page_config(page_title="Final page", page_icon="🎯", layout="wide")

# ---- Styling (centered + dark mode aesthetic) ----
st.markdown("""
    <style>
      
        .centered {
            text-align: center;
        }
        .content {
            max-width: 900px;
            margin: 0 auto;
            font-size: 15px;
            line-height: 1.6;
        }
        h1 {
            text-align: center;
            color: #f5f5f5;
            margin-bottom: 0.3em;
        }
        h2 {
            text-align: center;
            color: #cccccc;
            margin-top: 0;
        }
        .important {
            color: #ffcc00;
            font-weight: bold;
        }
        .button-container {
            display: flex;
            justify-content: center;
            margin-top: 40px;
        }
        div.button-container > div[data-testid="stVerticalBlock"] {
            display: flex;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

hide_sidebar()

# ---- Title section ----
st.markdown("<h1>🎯 Experiment finished</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ---- Main content ----
st.markdown("""
<div class="content">

<p>
Thank you very much for participating in our experiment! The session is now finished, so you can close this page whenever you want.
</p>

<p>
If you are interested, we will now briefly explain the purpose of this study.
</p>

<p>
The purpose of this study was to investigate the role of the graphical interface of a chatbot on the experience of the user. 
In fact, you interacted with only one chatbot, just with two different interfaces. 
We will compare the scores assigned to the first chatbot and to the second to assess if having an aesthetically pleasing graphical interface affects the experience of the user. 
</p>

<p>
Thank you again for your participation, we hope you enjoyed our chatbot!
</p>

""", unsafe_allow_html=True)


# ==========================================================
# 🔽 DATA COLLECTION AND SAVING SECTION
# ==========================================================

st.divider()
st.subheader("📁 Saving your data...")

CSV_FILE = Path("user_data.csv")

def collect_all_data():
    """Combine participant info and all survey responses into a single DataFrame."""
    participant = st.session_state.get("participant_info", {})
    surveys = st.session_state.get("survey_responses", {})

    if not participant:
        st.error("⚠️ No participant info found in session — nothing to save.")
        return pd.DataFrame()

    if not surveys:
        st.error("⚠️ No survey data found in session — nothing to save.")
        return pd.DataFrame()

    rows = []
    for ui_key, survey_data in surveys.items():
        combined = {**participant, **survey_data}
        combined["save_timestamp"] = datetime.utcnow().isoformat()
        rows.append(combined)
    return pd.DataFrame(rows)


# 🔹 Automatically save data when page loads
df = collect_all_data()
if not df.empty:
    if CSV_FILE.exists():
        old = pd.read_csv(CSV_FILE)
        df = pd.concat([old, df], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success(f"✅ All your data has been saved.")
else:
    st.warning("⚠️ Could not save data — missing session information.")
