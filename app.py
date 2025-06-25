from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Virtual_Interview",page_icon="📜")
st.title("ChatBot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_messages_count" not in st.session_state:
    st.session_state.user_messages_count = 0
if "feedback_shown" not in  st.session_state:
    st.session_state.feedback_shown  = False
if "messages" not in st.session_state:
    st.session_state.messages  = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False


def complete_setup():
    st.session_state.setup_complete = True

def feedback_shown():
    st.session_state.feedback_shown  = True

if not st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    #Collecting  the Personal Inforamtion like Name,Experience and Skills
    st.subheader("Personal Information",divider="rainbow")

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

    st.session_state["name"] = st.text_input(label="Name", max_chars=50, value=st.session_state["name"] , placeholder="What's your name?")
    st.session_state["experience"] = st.text_area(label="Experience", max_chars=200 , value=st.session_state["experience"] , height=None ,placeholder="What's is your work experience ?")
    st.session_state["skills"] = st.text_area(label="Skills", max_chars=200, value=st.session_state["skills"] ,height=None, placeholder="What is your skills")

    st.subheader("Company and Position",divider="rainbow")

    if "level" not in st.session_state:
        st.session_state.level = "junior"
    if "position" not in st.session_state:
        st.session_state.position = "Data Engineer"
    if "company" not in st.session_state:
        st.session_state.company = "Google"


    #Collecting information like Level,Position and Company
    col1,col2 = st.columns(2)

    with col1:
       st.radio(
            "Choose Level",
            options=["Junior","Mid-Level","Senior"],
            key="level"
        )

    with col2:
        st.selectbox(
            "Choose Role Position",
            ("Data Engineer","Data Scientist","AI Engineer","ML Engineer","Data Analyst","App Developer","Web Developer"),
            key="position"
        )

    st.selectbox(
            "Choose The Company",
            ("Google","Facebook","Udemy","Amazon","Netflix","Apple"),
            key="company"
        )
    
  
    st.write(f"**Your Information**: {st.session_state.level} {st.session_state.position} at {st.session_state.company}")

    if st.button("Start Interview",on_click=complete_setup):
        st.write("Setup Complete... Start Interview")

if st.session_state.setup_complete:

    st.info(
        """
        Would you like to introduce yourself
        """,
        icon="😀"
    )

# Connecting with Grok api
client =OpenAI(api_key=st.secrets["CHAT_API_KEYS"], base_url="https://api.groq.com/openai/v1" )

# Give Model if not exist
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "llama3-8b-8192"

#Stating the behaviour of model
if not st.session_state.messages:
    st.session_state.messages = [{"role":"system","content":f"You are an HR executive that interviews an interviewer called {st.session_state["name"]} with experience {st.session_state["experience"]} and skills {st.session_state["skills"]}. You should interview them for position {st.session_state.level} {st.session_state.position} at the company {st.session_state.company}"}]

#making chain of messages
for messages in st.session_state.messages:
    if messages["role"] != "system":
      with st.chat_message(messages["role"]):
        st.markdown(messages["role"])

if st.session_state.user_messages_count <  5:
    if prompt:= st.chat_input("Your Answer",max_chars=1000):
        #collecting messages
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.user_messages_count < 4:
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model = st.session_state["openai_model"],
                    temperature=0.5,
                    messages = [
                        {"role":m["role"],"content":m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True
                )
            response = st.write_stream(stream) #string
            st.session_state.messages.append({"role":"assistant","content":response})

        st.session_state.user_messages_count  += 1
    
    if  st.session_state.user_messages_count >= 5:
        st.session_state.chat_complete = True        

    if st.session_state.chat_complete and not st.session_state.feedback_shown:
        st.button("Get Feedback",on_click=feedback_shown)
        st.write("Feedback Writing......")

if  st.session_state.feedback_shown:
    st.subheader("Feeback")

    conversation_history = "\n".join([f"{msg["role"]}:  {msg["content"]}"  for msg in st.session_state.messages])

    feedback_client  = OpenAI(api_key=st.secrets["CHAT_API_KEYS"], base_url="https://api.groq.com/openai/v1")

    feedback_completions  = feedback_client.chat.completions.create(
        model= st.session_state["openai_model"],
        messages=[{
            "role":"system","content":(   "You are a helpful tool that provides feedback on an  interviewer performance."
            "Before the Feedback give a score of 1  to 10." 
            "Follow this format:"
            "Overal Score: //Your Score"
            "Feedback:  //Here you put your feedback"
            "Give only the feeback  do  not ask any additional questions.")
        },{"role":"user","content":f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you should  not engage in conversation:  {conversation_history}"}],
        stream=True,
    )

    st.write(feedback_completions.choices[0].message.content)


    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expression="parent.winodow.location.reload()")