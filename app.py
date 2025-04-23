import os
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ======================
# ENVIRONMENT SETUP
# ======================
def get_api_key():
    """Safely retrieves API key with clear error guidance"""
    # Try Streamlit secrets (production) first
    if 'secrets' in st.__dict__ and st.secrets.get("GEMINI_API_KEY"):
        return st.secrets["GEMINI_API_KEY"]
    
    # Fallback to .env (local development)
    load_dotenv()
    local_key = os.getenv("GEMINI_API_KEY")
    
    if not local_key:
        st.error("""
        🔐 API Key Required
        
        How to configure:
        
        LOCAL DEVELOPMENT (.env file):
        ```bash
        echo "GEMINI_API_KEY=your_actual_key" > .env
        ```
        
        STREAMLIT DEPLOYMENT (Secrets):
        1. Go to App Settings → Secrets
        2. Add:
        ```toml
        [secrets]
        GEMINI_API_KEY = "your_actual_key"
        ```
        """)
        st.stop()
    return local_key

# ======================
# CORE APP SETUP
# ======================
def initialize_app():
    """Configures the application"""
    # App metadata
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    
    # Initialize Gemini
    genai.configure(api_key=get_api_key())
    
    # Session state setup
    if "model" not in st.session_state:
        st.session_state.model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "property_details" not in st.session_state:
        st.session_state.property_details = {}

# ======================
# MAIN APP FUNCTIONALITY
# ======================
def main():
    initialize_app()
    st.title("🏠 AI Real Estate Analyst")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # First-run welcome message
    if not st.session_state.chat_history:
        welcome = """
        🏡 **AI Real Estate Assistant**  
        I can help with:
        - 📈 Property valuations
        - 🌆 Market trends
        - 💰 Investment analysis
        
        Try: *"What's my 3-bedroom in Austin worth?"*
        """
        st.session_state.chat_history.append({"role": "assistant", "content": welcome})
        with st.chat_message("assistant"):
            st.markdown(welcome)
    
    # User input handling
    if prompt := st.chat_input("Ask about properties..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    response = st.session_state.model.generate_content(
                        f"""As a real estate expert, answer concisely:
                        {prompt}
                        
                        Include:
                        1. Location context 🌎
                        2. Data references 📊
                        3. Actionable advice 💡
                        """
                    )
                    reply = response.text
                except Exception as e:
                    reply = f"⚠️ Error: {str(e)}"
                
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
