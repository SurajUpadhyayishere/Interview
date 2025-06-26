from openai import OpenAI
import streamlit as st
from streamlit_js_eval import  streamlit_js_eval
import time


st.set_page_config(page_title="Interview Page",page_icon="🧔🏻‍♂️")
st.title("ChatBot")

if "setup_complete" not in  st.session_state:
    st.session_state.setup_complete = False
if "user_messages_count" not in  st.session_state:
    st.session_state.user_messages_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown  = False
if  "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages =  []

def  complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown  = True

#=============================================================================================================================#
#==========================Take Personal  And Professionl Information=========================================================#

if not st.session_state.setup_complete:

    st.subheader("Personal Information",divider="rainbow")

    if "name" not in st.session_state:
        st.session_state["name"]   = ''
    if "experience" not in st.session_state:
        st.session_state["experience"] = ''
    if  "skills" not in  st.session_state:
        st.session_state["skills"] = ''

    st.session_state["name"] = st.text_input(label="Name",max_chars=50 , value=st.session_state["name"] ,placeholder="What's your name")
    st.session_state["experience"] = st.text_area(label="Experience",max_chars=150,value=st.session_state["experience"],placeholder="What's your experience")
    st.session_state["skills"] = st.text_area(label="Skills",max_chars=150,value=st.session_state["skills"],placeholder="What's your skills")

    st.write(f"***Name*** :",st.session_state["name"])
    st.write(f"***Experience*** :",st.session_state["experience"])
    st.write(f"***Skills*** :",st.session_state["skills"])

    st.subheader("Level,Role,Company",divider="rainbow")

    if  "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if  "position" not in st.session_state:
        st.session_state["position"] = "Data Engineer"
    if  "company" not in st.session_state:
        st.session_state["company"] =  "Google"


    cl1,cl2 = st.columns(2)

    with cl1:
        st.session_state["level"] = st.radio(
            "Select Your Level",
            options=["Junior","Mid-Level","Senior"]
        )

    with cl2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Engineer","AI Engineer","Web Developer","App Developer","Data Analyst","Businesss  Analyst"))

    st.session_state["company"] = st.selectbox(
        "Select Your Company",
        ["Google","Amazon","Netflix","Facebook","Tesla","Twitter","Apple"]
    )

    st.write(f"***Your Information***: {st.session_state['level']}  {st.session_state['position']} at {st.session_state['company']}." )

    if st.button("Start Interview",on_click=complete_setup):
        st.write("Setup Completed  Start Interview")

#===========================================================================================================================================================#
#====================================================Interview  Page========================================================================================#


#If  setup complete and feedback_shown and chat_complete  both not complete run  this
if st.session_state.setup_complete  and not st.session_state.feedback_shown and not  st.session_state.chat_complete: 
    if st.session_state.setup_complete:
        st.info("Hi,Could Introduce Yourself",icon="😀")

        Client = OpenAI(api_key=st.secrets['CHAT_API_KEYS'],base_url="https://api.groq.com/openai/v1")

        #Check the llm have model or not
        if "openai_model" not in st.session_state: 
            st.session_state["openai_model"] = "llama3-8b-8192"

        #Appending messages in sessionS_state
        if  not  st.session_state.messages:
            st.session_state.messages = [{"role":"system",
                    "content":(f"You are an HR executive that interviews an interviewwe called {st.session_state['name']}"
                            f"with experience{st.session_state['experience']} and skills {st.session_state['skills']}."
                            f"You should interview him for the position {st.session_state["level"]} {st.session_state['position']}"
                            f"at the company {st.session_state['company']}")}]

        #making chain of messages
        for messages in st.session_state.messages:
            if messages["role"] != "system":
                with  st.chat_message(messages["role"]):
                    st.markdown(messages["content"])

        #Taking input from user
        if  st.session_state.user_messages_count < 5:
            if prompt:= st.chat_input("Your Answer", max_chars=1000):
                st.session_state.messages.append({"role":"user","content":prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                

                #Respond The User
                if st.session_state.user_messages_count  < 4:
                    with  st.chat_message("assistant"):
                        stream = Client.chat.completions.create(
                            model = st.session_state["openai_model"],
                            temperature=0.5,
                            messages=[
                                {"role":  m["role"],"content":m["content"]}
                                for m in st.session_state.messages
                            ],
                            stream=True,
                        )
                    response = st.write_stream(stream)
                    st.session_state.messages.append({"role":"assistant","content":response})
                st.session_state.user_messages_count += 1

            if  st.session_state.user_messages_count >= 5:
                st.session_state.chat_complete = True
        
        if  st.session_state.chat_complete and not  st.session_state.feedback_shown:
            st.button("Get Feedback",on_click=show_feedback)
            st.write("Fetching Feedback")

if st.session_state.feedback_shown:
    st.subheader("Feedback,Overall Conclusion")

    conversation_history =  "\n".join([f"{msg['role']} {msg['content']}" for msg in st.session_state.messages])

    feedback_client  = OpenAI(api_key=st.secrets['CHAT_API_KEYS'],base_url="https://api.groq.com/openai/v1")

    feedback_completions  = feedback_client.chat.completions.create(
         model= st.session_state["openai_model"],
         stream=False,
         temperature=0.5,
         messages=[{
                "role":"system","content":"You are a helpful tool that provides feedback on interview performance.\n"
                        "First output an overall score from 1-10.\n"
                        "Then give concise feedback.\n\n"
                        "Format strictly:\n"
                        "Overall Score: <score>\n"
                        "Feedback: <your feedback>"
           },{"role":"user","content":f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you should  not engage in conversation:  {conversation_history}"}],
        
        )
        
     #display the feedback
    st.write(feedback_completions.choices[0].message.content)

     #Restart interview
    if st.button("Restart Interview", type="primary"):
        st.success("Restarting Interview....")
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
