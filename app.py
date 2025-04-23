import os
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ======================
# CONFIGURATION SETUP
# ======================
def configure_gemini():
    """Handles API key configuration for both local and production"""
    # Try Streamlit secrets first (for production), fallback to .env (for local)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("""
        🔑 API Key Missing!
        For local use: Create `.env` with GEMINI_API_KEY=your_key
        For deployment: Set in Streamlit Secrets
        """)
        st.stop()  # Prevent app from running without key
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-pro-latest")

# ======================
# SESSION MANAGEMENT
# ======================
def init_session():
    """Initialize session state variables"""
    defaults = {
        "chat_history": [],
        "property_details": {},
        "first_interaction": True,
        "model": configure_gemini()  # Initialize model once
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ======================
# CORE FUNCTIONALITY
# ======================
def generate_response(prompt: str) -> str:
    """Generate AI response with error handling"""
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def extract_property_details(text: str) -> dict:
    """Extract property features from user input"""
    patterns = {
        "location": r'in\s(.+?)(?:\s|$)',
        "size": r'(\d+)\s*(sqft|square\s*feet)',
        "beds": r'(\d+)\s*bed',
        "price": r'\$?(\d{1,3}(?:,\d{3})*)'
    }
    return {k: re.search(v, text, re.I) for k, v in patterns.items()}

# ======================
# UI COMPONENTS
# ======================
def display_chat():
    """Render chat history"""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_welcome():
    """Initial assistant message"""
    welcome = """
    🏡 **AI Real Estate Analyst**  
    I can help with:
    - 📈 Property valuations
    - 🌆 Market trends
    - 💰 Investment analysis  
    Try: *"What's my 3-bedroom in Austin worth?"*
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

def render_sidebar_tools():
    """Property analysis tools"""
    with st.sidebar:
        st.subheader("🔧 Property Toolkit")
        
        # Current property summary
        if any(st.session_state.property_details.values()):
            st.write("**📋 Current Property**")
            for key, match in st.session_state.property_details.items():
                if match: st.write(f"- {key.title()}: {match.group(1)}")
        
        st.divider()
        
        # Quick analysis buttons
        if st.button("📊 Market Snapshot"):
            if loc := st.session_state.property_details.get("location"):
                with st.chat_message("assistant"):
                    response = generate_response(
                        f"Give a 3-point market snapshot for {loc.group(1)}"
                    )
                    st.markdown(response)

# ======================
# MAIN APP
# ======================
def main():
    # App configuration
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    st.title("🏠 AI Real Estate Analyst")
    
    # Initialize app
    load_dotenv()  # Only loads .env locally
    init_session()
    
    # Display chat interface
    display_chat()
    if st.session_state.first_interaction:
        show_welcome()
        st.session_state.first_interaction = False
    
    # Handle user input
    if user_input := st.chat_input("Ask about properties..."):
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # Create enhanced prompt
                prompt = f"""
                As a top real estate analyst, respond to:
                "{user_input}"
                
                Include:
                1. 📍 Location context
                2. 📊 Data references
                3. 💡 Actionable advice
                4. ⚠️ Potential risks
                """
                
                reply = generate_response(prompt)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                
                # Update property details
                if any(kw in user_input.lower() for kw in ["worth", "value", "price", "buy"]):
                    st.session_state.property_details = extract_property_details(user_input)
    
    # Render sidebar tools
    render_sidebar_tools()

if __name__ == "__main__":
    main()
