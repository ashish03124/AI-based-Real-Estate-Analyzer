import streamlit as st
import google.generativeai as genai

# ======================
# SECRETS CONFIGURATION
# ======================
st.write("🔍 Secrets loaded:", st.secrets)

def get_api_key():
    """Secure API key retrieval with detailed error guidance"""
    try:
        # First check if secrets are available
        if not hasattr(st, 'secrets'):
            st.error("Streamlit secrets not available in this environment")
            st.stop()
        
        # Then check for the specific key
        if 'GEMINI_API_KEY' not in st.secrets:
            st.error("""
            🔐 Missing API Key Configuration
            
            REQUIRED STEPS:
            
            1. Go to your Streamlit app dashboard
            2. Click on 'Settings' → 'Secrets'
            3. Add exactly this configuration:
            
            ```toml
            [secrets]
            GEMINI_API_KEY = "your_actual_key_here"
            ```
            
            4. Click 'Save' 
            5. Wait 1 minute and refresh this page
            """)
            st.stop()
            
        return st.secrets["GEMINI_API_KEY"]
        
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()

# ======================
# APP INITIALIZATION
# ======================
def initialize_gemini():
    """Configure Gemini with robust error handling"""
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("models/gemini-1.5-pro-latest")
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {str(e)}")
        st.stop()

# ======================
# MAIN APP
# ======================
def main():
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst Pro",
        layout="centered",
        page_icon="🏡"
    )
    
    # Initialize services
    model = initialize_gemini()
    
    # Initialize chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    st.title("🏠 AI Real Estate Analyst Pro")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Initial greeting
    if not st.session_state.chat_history:
        welcome_msg = """
        🏡 **Professional Real Estate Assistant**  
        I specialize in:
        - Accurate property valuations
        - Local market analytics
        - Investment opportunity analysis
        - Comparative market reports
        
        Try asking:  
        *"What's the current price per sqft in Downtown Miami?"*  
        *"Show me investment opportunities in Austin under $500k"*
        """
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})
        with st.chat_message("assistant"):
            st.markdown(welcome_msg)
    
    # User input
    if prompt := st.chat_input("Ask about properties..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing market data..."):
                try:
                    response = model.generate_content(
                        f"""As a certified real estate analyst, provide detailed insights about:
                        {prompt}
                        
                        Include:
                        1. Location-specific context 🌍
                        2. Current market metrics 📊  
                        3. Professional recommendations 💼
                        4. Risk assessment ⚠️
                        """
                    )
                    reply = response.text
                except Exception as e:
                    reply = f"⚠️ Service Error: {str(e)}"
                
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
