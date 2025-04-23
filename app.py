import streamlit as st
import google.generativeai as genai

# ======================
# SECURE CONFIGURATION
# ======================
def get_api_key():
    """Retrieves API key exclusively from Streamlit Secrets"""
    if 'GEMINI_API_KEY' not in st.secrets:
        st.error("""
        🔐 API Key Missing!
        
        Please configure in Streamlit Secrets:
        1. Go to App Settings → Secrets
        2. Add:
        ```toml
        [secrets]
        GEMINI_API_KEY = "your_actual_key"
        ```
        """)
        st.stop()
    return st.secrets["GEMINI_API_KEY"]

# ======================
# APP INITIALIZATION
# ======================
def initialize_app():
    """Configures the application with production-ready settings"""
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    
    # Initialize Gemini (will fail fast if key missing)
    genai.configure(api_key=get_api_key())
    
    # Initialize session state
    if "model" not in st.session_state:
        st.session_state.model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# ======================
# CHAT INTERFACE
# ======================
def display_chat():
    """Renders conversation history"""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def handle_user_query(prompt: str):
    """Processes real estate queries"""
    with st.chat_message("assistant"):
        with st.spinner("Analyzing property..."):
            try:
                response = st.session_state.model.generate_content(
                    f"""As a real estate expert, respond to:
                    {prompt}
                    
                    Include:
                    1. Location context 🌎
                    2. Market data 📊
                    3. Investment advice 💰
                    """
                )
                reply = response.text
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"
            
            st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ======================
# MAIN APP
# ======================
def main():
    initialize_app()
    st.title("🏠 AI Real Estate Analyst")
    
    # Display chat history
    display_chat()
    
    # Initial greeting
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": """
            🏡 **AI Real Estate Assistant**  
            Ask me about:
            - Property valuations
            - Market trends
            - Investment opportunities
            """
        })
    
    # Process user input
    if prompt := st.chat_input("Ask about properties..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        handle_user_query(prompt)

if __name__ == "__main__":
    main()
