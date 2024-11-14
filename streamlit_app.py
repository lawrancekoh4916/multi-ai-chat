import streamlit as st

# Set up the Streamlit page (must be first Streamlit command)
st.set_page_config(layout="wide", page_title="Triple AI Chat")

import os
from dotenv import load_dotenv
import google.generativeai as genai
import openai
import groq

# Load environment variables
load_dotenv()

# Configure API clients
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')
groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))

# Function to get available Gemini models
def get_gemini_models():
    try:
        models = genai.list_models()
        return [m.name for m in models if 'gemini' in m.name]
    except Exception as e:
        st.error(f"Error fetching Gemini models: {str(e)}")
        return ['gemini-pro']  # Fallback

# Function to get available OpenAI models
def get_openai_models():
    try:
        models = openai.models.list()
        return [m.id for m in models if m.id.startswith(('gpt-3.5', 'gpt-4'))]
    except Exception as e:
        st.error(f"Error fetching OpenAI models: {str(e)}")
        return ['gpt-3.5-turbo']  # Fallback

# Function to get available Groq models
def get_groq_models():
    try:
        # List of currently available models from Groq documentation
        available_models = [
            'mixtral-8x7b-32768',
            'llama2-70b-32768',
            'gemma-7b-it',
            'llama2-13b-32768',
            'llama2-7b-32768'
        ]
        return available_models
    except Exception as e:
        st.error(f"Error fetching Groq models: {str(e)}")
        return ['mixtral-8x7b-32768']  # Fallback to most capable model

# Get available models
GEMINI_MODELS = get_gemini_models()
OPENAI_MODELS = get_openai_models()
GROQ_MODELS = get_groq_models()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {
        "gemini": [],
        "openai": [],
        "groq": []
    }
if "current_input" not in st.session_state:
    st.session_state.current_input = None

# Custom CSS for the chat containers
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        div[data-testid="column"] {
            height: 600px;
            overflow-y: auto !important;
            padding: 1rem;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .stTextInput > div > div > input {
            background-color: #f0f2f6;
            color: black;
        }
        .stMarkdown {
            overflow: visible;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Triple AI Chat Interface")

# Create three columns for the chat interfaces
col1, col2, col3 = st.columns(3)

# Left pane (Gemini)
with col1:
    st.subheader("Gemini")
    gemini_model = st.selectbox(
        "Select Gemini Model",
        GEMINI_MODELS,
        key="gemini_model"
    )
    
    # Display Gemini messages
    for msg in st.session_state.messages["gemini"]:
        if msg["role"] == "user":
            st.info(f"You: {msg['content']}")
        else:
            st.success(f"Gemini: {msg['content']}")

# Middle pane (OpenAI)
with col2:
    st.subheader("OpenAI")
    openai_model = st.selectbox(
        "Select OpenAI Model",
        OPENAI_MODELS,
        key="openai_model"
    )
    
    # Display OpenAI messages
    for msg in st.session_state.messages["openai"]:
        if msg["role"] == "user":
            st.info(f"You: {msg['content']}")
        else:
            st.success(f"OpenAI: {msg['content']}")

# Right pane (Groq)
with col3:
    st.subheader("Groq")
    groq_model = st.selectbox(
        "Select Groq Model",
        GROQ_MODELS,
        key="groq_model"
    )
    
    # Display Groq messages
    for msg in st.session_state.messages["groq"]:
        if msg["role"] == "user":
            st.info(f"You: {msg['content']}")
        else:
            st.success(f"Groq: {msg['content']}")

# Input area
col4, col5 = st.columns([6, 1])
with col4:
    if "input_value" not in st.session_state:
        st.session_state.input_value = ""
    
    def submit():
        if st.session_state.user_input:
            st.session_state.input_value = st.session_state.user_input
            st.session_state.user_input = ""
    
    user_input = st.text_input(
        "Message",
        key="user_input",
        label_visibility="collapsed",
        on_change=submit
    )

with col5:
    if st.button("Clear"):
        st.session_state.messages = {"gemini": [], "openai": [], "groq": []}
        st.session_state.current_input = None
        st.session_state.input_value = ""
        st.rerun()

# Handle user input
if st.session_state.input_value and st.session_state.input_value != st.session_state.current_input:
    current_input = st.session_state.input_value
    st.session_state.current_input = current_input
    st.session_state.input_value = ""
    
    # Add user message to all conversations
    for model in ["gemini", "openai", "groq"]:
        st.session_state.messages[model].append({
            "role": "user",
            "content": current_input
        })
    
    # Get Gemini response
    try:
        gemini = genai.GenerativeModel(gemini_model)
        gemini_response = gemini.generate_content(current_input)
        st.session_state.messages["gemini"].append({
            "role": "assistant",
            "content": gemini_response.text
        })
    except Exception as e:
        st.error(f"Gemini Error: {str(e)}")
        st.session_state.messages["gemini"].append({
            "role": "assistant",
            "content": f"Error: {str(e)}"
        })

    # Get OpenAI response
    try:
        openai_response = openai.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": current_input}]
        )
        st.session_state.messages["openai"].append({
            "role": "assistant",
            "content": openai_response.choices[0].message.content
        })
    except Exception as e:
        st.error(f"OpenAI Error: {str(e)}")
        st.session_state.messages["openai"].append({
            "role": "assistant",
            "content": f"Error: {str(e)}"
        })

    # Get Groq response
    try:
        groq_response = groq_client.chat.completions.create(
            model=groq_model,
            messages=[{"role": "user", "content": current_input}]
        )
        st.session_state.messages["groq"].append({
            "role": "assistant",
            "content": groq_response.choices[0].message.content
        })
    except Exception as e:
        st.error(f"Groq Error: {str(e)}")
        st.session_state.messages["groq"].append({
            "role": "assistant",
            "content": f"Error: {str(e)}"
        })
    
    st.rerun()

# Add JavaScript for auto-scrolling
st.markdown("""
    <script>
        // Function to scroll containers to bottom
        function scrollContainersToBottom() {
            const containers = document.querySelectorAll('.chat-container');
            containers.forEach(container => {
                container.scrollTop = container.scrollHeight;
            });
        }

        // Call on load
        window.addEventListener('load', scrollContainersToBottom);
        
        // Call on any DOM changes
        const observer = new MutationObserver(scrollContainersToBottom);
        
        // Observe chat containers
        document.querySelectorAll('.chat-container').forEach(container => {
            observer.observe(container, { 
                childList: true,
                subtree: true
            });
        });
    </script>
""", unsafe_allow_html=True)