"""
This file contains the code responsible for the landing page that the users
using a GUI will be faced with. The landing page contains a form for
getting the users their information, which gets extracted through a form.

ONLY when the form has been completely filled out, and submitted,
do we allow the user to move on to the next page.
There they will actually interact with the recommender
system by getting recommendations.

After that, the user will be led to a third and final page,
which also contains a form. Here we ask for all the metrics
regarding user satisfaction.

!! IMPORTANT: !!
The data that gets gathered here gets sent to a web-API that saves the data to a local file.
To see more about how that side works, visit the data_receiver.py file
"""

# standard imports:
from typing import Dict, Union

# 3rd-party imports:
import streamlit as st
import requests
from requests import Response
from helper import hide_sidebar


st.session_state.setdefault("user_id", __import__("uuid").uuid4().hex[:8])


if "submitted" not in st.session_state:
    st.session_state.submitted = False

API_LINK: str = "http://94.208.248.212:5000/log"

# 1. welcome test subject:
#//>>
st.set_page_config(page_title="welcome to the experiment", page_icon="🔬")
st.title("Welcome to the experiment!")
st.markdown(
    """
    Dear participant, welcome to our experiment on chatbot interaction!!
    In this short study, you’ll interact with two versions of our restaurant recommendation chatbot.  
    You will be given instructions as soon as the experiment flows, please follow them and enjoy your experience with our restaurant recommender chatbot. 
    The entire session takes **about 10–15 minutes**.  
    Please complete each section carefully and in order — once you finish one part, a button will appear to move to the next.  
    """
)

hide_sidebar()
#//<<

# 2. form:
#//>>
with st.form("participant_form"):
    st.markdown("## Participant Information")
    age: int = st.slider("Age", 10, 120)
    sex: str = st.radio("Sex", ["Male", "Female", "Other"], horizontal=True)
    occupation: str = st.text_input("Occupation (e.g., student, researcher, engineer)")
    nationality: str = st.text_input("Nationality (e.g., Italian, Dutch, German)")

    st.info(    """
Before we begin, it's important to know that all data that we collect will be
anonymous and confidential, and you will not be identifiable in any report,
thesis or publication which arises from this study. If the dataset will be
published as part of scientific communications this will be done in an
anonymized fashion.\n
We will kindly ask your permission to use your data for research purposes.
You are free to decline this request, of course, but you can't finish the
experiment.\n
By checking this checkbox, I confirm that:\n
- I have read and understood the information provided to me for this
study,\n
- I understand that my participation is voluntary and that I am free to
withdraw at any time, without giving a reason, without my medical
care or legal rights being affected,\n
- I understand that the research data will be archived in a completely
anonymous way in an online database and/or data repository and/or
published as supplementary material to a scientific article and may
be accessed by other researchers as well as the general public
- I understand that the anonymized research data can be used in,\n
future projects on similar or different topics to this study and
potential results can be published in other scientific publications. At
all times, my personal data will be kept anonymized in accordance
with data protection guidelines


    """)
    informed_consent: bool = st.checkbox("I have read the consent form and agree with it")
    submit: bool = st.form_submit_button("Submit participant info")
#//<<

# check whether form is full:
#//>>
full: bool
submitted: bool = False
if  age and sex and informed_consent:
    full = True
else:
    full = False
#//<<\

# handle the submit part:
#//>>
if submit:
    if full:
        st.session_state.submitted = True
        st.session_state["participant_info"] = {
            "user_id": st.session_state["user_id"],
            "age": age,
            "sex": sex,
            "occupation": occupation,
            "nationality": nationality,
            "informed_consent": informed_consent,
        }
        st.success("✅ Participant information successfully saved.")
    else:
        st.warning('fill in the bloody form!', icon="⚠️")
#//<<

# handle user going to next page
#//>>
next_page: bool = st.button("I am ready to start the experiment...")
if next_page:
    if st.session_state.submitted:
        #from streamlit import get_pages
        st.switch_page("pages/01_Chatbot_Introduction.py")
    else:
        st.warning('Fill in the form before starting the experiment!', icon="⚠️")
#//<<
