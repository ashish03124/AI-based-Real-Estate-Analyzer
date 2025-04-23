import streamlit as st
import google.generativeai as genai

# ======================
# SECURE API CONFIGURATION
# ======================
def validate_environment():
    """Ensures proper configuration before startup"""
    if 'GEMINI_API_KEY' not in st.secrets:
        st.error("""
        🔐 Configuration Required

        Steps to fix:
        1. Go to your Streamlit app dashboard
        2. Click ⚙️ → Settings → Secrets
        3. Add exactly:
        ```toml
        [secrets]
        GEMINI_API_KEY = "your_actual_key_here"
        ```
        4. Click Save and restart your app
        """)
        st.stop()  # Prevent further execution
    return st.secrets["GEMINI_API_KEY"]

# ======================
# APP INITIALIZATION
# ======================
def initialize_app():
    """Configures core application services"""
    # Validate environment first
    api_key = validate_environment()
    
    # App metadata
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡",
        menu_items={
            'Get Help': 'https://docs.streamlit.io',
            'Report a bug': None,
            'About': "Powered by Gemini AI"
        }
    )
    
    # Initialize AI services
    genai.configure(api_key=api_key)
    
    # Initialize session state
    session_defaults = {
        'model': genai.GenerativeModel("models/gemini-1.5-pro-latest"),
        'chat_history': [],
        'property_cache': {}
    }
    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ======================
# CORE FUNCTIONALITY
# ======================
def generate_insight(prompt: str) -> str:
    """Generates AI response with robust error handling"""
    try:
        response = st.session_state.model.generate_content(
            f"""As a real estate expert analyzing:
            {prompt}

            Provide:
            1. Location-specific context 🌍
            2. Current market data 📈
            3. Professional recommendation 💼
            4. Potential risks ⚠️
            
            Use bullet points for readability.
            """
        )
        return response.text
    except Exception as e:
        return f"🔴 Service Error: {str(e)}"

# ======================
# USER INTERFACE
# ======================
def render_chat_interface():
    """Handles all chat display and interactions"""
    st.title("🏠 AI Real Estate Analyst")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Initial greeting
    if not st.session_state.chat_history:
        greeting = """
        🏡 **AI Real Estate Assistant**  
        How I can help:
        • Instant property valuations
        • Local market trends
        • Investment analysis
        
        Try:  
        _"Value my 3-bedroom in Austin"_  
        _"Show Denver market trends"_
        """
        st.session_state.chat_history.append({"role": "assistant", "content": greeting})
        with st.chat_message("assistant"):
            st.markdown(greeting)
    
    # Process user input
    if query := st.chat_input("Ask about properties..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        
        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = generate_insight(query)
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# ======================
# MAIN EXECUTION
# ======================
def main():
    initialize_app()
    render_chat_interface()

if __name__ == "__main__":
    main()
