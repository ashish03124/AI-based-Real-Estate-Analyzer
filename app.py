import streamlit as st
import google.generativeai as genai

# ======================
# SECRETS CONFIGURATION
# ======================
def get_api_key():
    """Retrieve API key from Streamlit Secrets with clear error handling"""
    try:
        if 'GEMINI_API_KEY' not in st.secrets:
            st.error("""
            🔐 Missing API Key Configuration
            
            How to fix:
            
            1. Go to your Streamlit app dashboard
            2. Click on '⚙️ Settings' → 'Secrets'
            3. Add your Gemini API key:
            ```toml
            [secrets]
            GEMINI_API_KEY = "your_actual_key_here"
            ```
            4. Click 'Save' and restart your app
            """)
            st.stop()
        return st.secrets["GEMINI_API_KEY"]
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()

# ======================
# APP INITIALIZATION
# ======================
def initialize_app():
    """Configure the application"""
    # App metadata
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    
    # Initialize Gemini
    try:
        genai.configure(api_key=get_api_key())
        return genai.GenerativeModel("models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error(f"Failed to initialize AI service: {str(e)}")
        st.stop()

# ======================
# MAIN APP FUNCTIONALITY
# ======================
def main():
    # Initialize components
    model = initialize_app()
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    st.title("🏠 AI Real Estate Analyst")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Initial greeting
    if not st.session_state.chat_history:
        welcome_msg = """
        🏡 **AI Real Estate Assistant**  
        I can help with:
        - Property valuations
        - Market trends
        - Investment analysis
        
        Try asking:  
        *"What's my 3-bedroom in Austin worth?"*
        """
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})
        with st.chat_message("assistant"):
            st.markdown(welcome_msg)
    
    # Handle user input
    if prompt := st.chat_input("Ask about properties..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    response = model.generate_content(
                        f"""As a real estate expert, analyze:
                        {prompt}
                        
                        Provide:
                        1. Location context 🌎
                        2. Current market data 📊
                        3. Professional advice 💼
                        """
                    )
                    reply = response.text
                except Exception as e:
                    reply = f"⚠️ Error: {str(e)}"
                
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
