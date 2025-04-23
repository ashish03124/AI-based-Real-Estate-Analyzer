import os
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ======================
# ENVIRONMENT SETUP
# ======================
def setup_environment():
    """Configure environment with fail-safe key loading"""
    # Load .env file only in local development
    if not st.secrets:  # Only runs locally
        load_dotenv()
    
    # Check both possible key sources
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("""
        🔐 Authentication Required
        
        Please provide your Gemini API key:
        
        **For Local Development**:
        1. Create a `.env` file in your project root
        2. Add: `GEMINI_API_KEY=your_key_here`
        
        **For Production Deployment**:
        1. Go to Streamlit app settings
        2. Add to Secrets:
        ```toml
        [secrets]
        GEMINI_API_KEY = "your_key_here"
        ```
        """)
        st.stop()  # Halt execution if no key found
    
    return api_key

# ======================
# APP INITIALIZATION
# ======================
def initialize_app():
    """Configure app-wide settings"""
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    
    # Initialize Gemini
    api_key = setup_environment()
    genai.configure(api_key=api_key)
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.update({
            "model": genai.GenerativeModel("models/gemini-1.5-pro-latest"),
            "chat_history": [],
            "property_details": {},
            "first_interaction": True
        })

# ======================
# CORE FUNCTIONS
# ======================
def generate_response(prompt: str) -> str:
    """Generate AI response with error handling"""
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

def extract_property_details(text: str) -> dict:
    """Parse property details from user input"""
    return {
        "location": re.search(r'in\s(.+?)(?:\s|$)', text, re.I),
        "size": re.search(r'(\d+)\s*(sqft|square\s*feet)', text, re.I),
        "beds": re.search(r'(\d+)\s*bed', text, re.I),
        "price": re.search(r'\$?(\d{1,3}(?:,\d{3})*)', text)
    }

# ======================
# UI COMPONENTS
# ======================
def display_chat():
    """Render conversation history"""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_welcome():
    """Initial assistant message"""
    welcome_msg = """
    🏡 **AI Real Estate Analyst**  
    I can help with:
    - 📈 Property valuations
    - 🌆 Market trends
    - 💰 Investment analysis
    
    Try asking:  
    *"What's my 3-bedroom in Austin worth?"*  
    *"Show market trends for Miami condos"*
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})
    with st.chat_message("assistant"):
        st.markdown(welcome_msg)

# ======================
# MAIN APP FLOW
# ======================
def main():
    initialize_app()
    st.title("🏠 AI Real Estate Analyst")
    
    # Display chat history
    display_chat()
    
    # Show welcome message on first load
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
                prompt = f"""
                As a real estate expert, respond to:
                "{user_input}"
                
                Include:
                1. 📍 Location context
                2. 📊 Data references
                3. 💡 Actionable advice
                """
                
                reply = generate_response(prompt)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                
                # Update property details if relevant
                if any(kw in user_input.lower() for kw in ["worth", "value", "price"]):
                    st.session_state.property_details = extract_property_details(user_input)

if __name__ == "__main__":
    main()
