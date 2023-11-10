"""
This is a Python script that serves as a frontend for a conversational AI model built with the `langchain` and `llms` libraries.
The code creates a web application using Streamlit, a Python library for building interactive web apps.
# Author: Avratanu Biswas
# Date: March 11, 2023
"""

# Import necessary libraries
import streamlit as st
#import streamlit_nested_layout
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
#from langchain.llms import OpenAI
from langchain.llms import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Set Streamlit page configuration
st.set_page_config(page_title='🧠MemoryBot🤖', layout='wide')
# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder="Your AI assistant here! Ask me anything ...", 
                            label_visibility='hidden')
    return input_text

# Define function to start a new chat
def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.entity_store = {}
    st.session_state.entity_memory.buffer.clear()

# Set up sidebar with various options
with st.sidebar:
# with st.sidebar.expander("🛠️ ", expanded=False):   # this caused a nested expander error
    # Option to preview memory store
    if st.checkbox("Preview memory store"):
        with st.expander("Memory-Store", expanded=False):
            st.session_state.entity_memory.store
    # Option to preview memory buffer
    if st.checkbox("Preview memory buffer"):
        with st.expander("Buffer-Store", expanded=False):
            st.session_state.entity_memory.buffer
    #MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo','text-davinci-003','text-davinci-002','code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider',min_value=3,max_value=1000)

# Set up the Streamlit app layout
st.title("🗣️ Chat Bot for ⚖️")
st.subheader(" Powered by 🦜 LangChain + OpenAI")

# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input("API-KEY", type="password")  # removed this because we are getting this value from .env file
#API_O = os.environ.get("OPEN_API_KEY")
AZURE_OPEN_API_KEY = os.environ.get("AZURE_OPEN_API_KEY")
print(AZURE_OPEN_API_KEY)
print("docker registry url: ", os.environ.get("DOCKER_REGISTRY_SERVER_URL"))

# Session state storage would be ideal
#if API_O:
if AZURE_OPEN_API_KEY:
    # Create an OpenAI instance
    #os.environ["OPENAI_API_TYPE"] = "azure"
    #os.environ["OPENAI_API_VERSION"] = "2023-05-15"   # os.getenv("AZURE_OPENAI_ENDPOINT")
    #os.environ["OPENAI_API_BASE"] = "https://use-openai.openai.azure.com/"
    #os.environ["OPENAI_API_KEY"] = AZURE_OPEN_API_KEY # "c7be4f73105a41dc843e9a8efc723569"
    
    
    #llm = OpenAI(temperature=0,
    #           openai_api_key=API_O, 
    #           model_name=MODEL, 
    #           verbose=False) 
    llm = AzureOpenAI(
                      openai_api_type="azure",
                      openai_api_key=os.getenv("AZURE_OPEN_API_KEY"),
                      openai_api_base=os.getenv("AZURE_OPENAI_BASE"),
                      deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"),
                      model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                      temperature=0.7,
                      openai_api_version=os.getenv("OPENAI_VERSION"))                      
                      #model_kwargs={"api_type": "azure", "api_version": "2023-05-15"})

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
            st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K )
        
        # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
            llm=llm, 
            prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
            memory=st.session_state.entity_memory
        )  
else:
    st.sidebar.warning('API key required to try this app')
    # st.stop()


# Add a button to start a new chat
st.sidebar.button("New Chat", on_click = new_chat, type='primary')

# Get the user input
user_input = get_text()

# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input:
    output = Conversation.run(input=user_input)  
    st.session_state.past.append(user_input)  
    st.session_state.generated.append(output)  

# Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        st.info(st.session_state["past"][i],icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])
    
    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download',download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
        with st.sidebar.expander(label= f"Conversation-Session:{i}"):
            st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:   
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
