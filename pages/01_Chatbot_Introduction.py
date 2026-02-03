import streamlit as st, time
from helper import hide_sidebar

# ---- Page setup ----
st.set_page_config(page_title="Instructions", page_icon="ℹ️", layout="wide")

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
st.markdown("<h1>🧭 Instructions</h1>", unsafe_allow_html=True)
st.markdown("<h2>Your first chatbot interaction</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ---- Main content ----
st.markdown("""
<div class="content">

<p>
In the next page, you will interact with a <b>chatbot</b> designed to help you select the 
<strong>best restaurant</strong> in town for your needs.
</p>

<p>
You will be given a specific <b>task</b> to complete.  
For example:  
<em>“Find an expensive restaurant that serves Indian food in the north part of town.  
The restaurant also needs to be romantic.”</em>
</p>

<p>
Your goal is to find the restaurant described in the task.  
You have <b>5 minutes<b> to complete it — a timer will appear in the chat to help you keep track of time.  
The time is more than enough, so <b>don’t rush!</b>  
Take your time to interact with the chatbot naturally and try to enjoy the conversation.
</p>

<p>
You can either ask everything in one single message,  
or chat step by step as you would do with a human assistant — <b>it's up to you!</b>
</p>

<p>
Once you have completed your task (or if you decide to stop early),  
click the <b>“I want to end the interaction”</b> checkbox inside the chatbot interface.  
Then you will be able to move on to the next part of the experiment.
</p>
            
<p>
The chatbot might take a few seconds (up to one minute to load). Please, be patient and wait on the page till the chatbot appears.
</p>

<p style="text-align:center; margin-top: 30px;">
 <b>Enjoy your interaction, and good luck!</b> 
</p>

</div>
""", unsafe_allow_html=True)

# ---- Continue button ----
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
if st.button("I got it — Go to the chatbot"):
    st.switch_page("pages/02_fancy_gui_chat.py")
st.markdown('</div>', unsafe_allow_html=True)



