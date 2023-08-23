#
# app.py
# Author : Sushil K Sharma
#

import streamlit as st

st.set_page_config(
    page_title="CSTU GPT - Team 2",
    page_icon="💬",
)

st.title("Welcome to Team 2 - CSTU GPT 💬")

st.sidebar.success("Select a site above.")

credits_text = """
## CSE590/MB590 CSTUGPT Special Topics, Summer 2023

- Project: CSTUGPT [Github](https://github.com/krishnatray/cstuchatgpt_team2)

---------------------
## Project Team:
- Sushil K Sharma [Linkedin](https://linkedin.com/in/krishnatray)
- Fang Wang [Linkedin](https://www.linkedin.com/in/fangwang12/) 
- Lam Ngoc Dao [Linkedin](https://www.linkedin.com/in/lam-dao-871508246/)
- Alok Gupta [Linkedin](https://linkedin.com/in/alok-gupta-innovator) 
- Joyce Cheng [Linkedin](https://www.linkedin.com/in/joyce-cheng-2872a688/) 
- Phil Pyo [Linkedin](https://www.linkedin.com/in/phillippyo/)
---------------------
## Professor:
#### Michael Hu(mhu95131@gmail.com)

California Science and Technology University
https://www.cstu.edu/
              
"""
st.markdown(credits_text) 