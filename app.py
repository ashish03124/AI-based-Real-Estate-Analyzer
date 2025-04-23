import os
import re
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ======================
# Configuration Setup
# ======================
def configure_app():
    """Handle secrets and API configuration"""
    # Unified secret/environment handling
    # Unified configuration (works both locally and in production)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("""
        ❌ Gemini API key missing. Please:
        1. For local use: Create `.env` with GEMINI_API_KEY=your_key
        2. For deployment: Set in Streamlit Secrets
        """)
        st.stop()  # Prevents app from running without key
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-pro-latest")

# ======================
# Session Management
# ======================
def init_session():
    """Initialize session state"""
    if "chat_history" not in st.session_state:
        st.session_state.update({
            "chat_history": [],
            "property_details": {},
            "first_interaction": True
        })

# ======================
# UI Components
# ======================
def display_chat():
    """Render chat history"""
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def show_welcome():
    """Initial assistant greeting"""
    welcome = """
    Hello! I'm your AI Real Estate Analyst. 🏘️ I can help with:
    
    **Property Valuation**:
    - "What's my 3-bedroom house in Seattle worth?"
    - "Estimate value for 1500 sqft condo in Miami"
    
    **Market Analysis**:
    - "Show trends for Austin TX housing market"
    - "Compare prices in Brooklyn vs Manhattan"
    
    **Investment Advice**:
    - "Good ROI areas in Phoenix?"
    - "Should I buy this rental property?"
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# ======================
# Core Functionality
# ======================
def generate_response(user_input: str, model):
    """Generate AI response for real estate queries"""
    prompt = f"""
    As an expert real estate analyst, respond to:
    "{user_input}"
    
    Guidelines:
    1. For valuations: Request missing details → Provide price ranges with comps
    2. For markets: Show trends with YoY comparisons
    3. For investments: Calculate ROI and tax implications
    4. Always include:
       - 📊 Data-driven insights
       - 📍 Location context
       - ⚠️ Relevant caveats
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def extract_property_details(text: str):
    """Parse property details from user input"""
    return {
        "location": re.search(r'in\s(.+?)(?:\s|$)', text, re.I),
        "size": re.search(r'(\d+)\s*(sqft|square feet)', text, re.I),
        "beds": re.search(r'(\d+)\s*bed', text, re.I)
    }

# ======================
# Sidebar Tools
# ======================
def render_sidebar_tools(model):
    """Property analysis tools"""
    with st.sidebar:
        st.subheader("Property Toolkit")
        
        if st.session_state.property_details:
            st.write("**Current Property**")
            for k, v in st.session_state.property_details.items():
                if v: st.write(f"- {k.capitalize()}: {v.group(1)}")
        
        st.divider()
        
        if st.button("📊 Market Snapshot"):
            if location := st.session_state.property_details.get("location"):
                with st.chat_message("assistant"):
                    response = model.generate_content(
                        f"Provide 3 bullet points on {location.group(1)} market trends"
                    )
                    st.markdown(response.text)

# ======================
# Main App Flow
# ======================
def main():
    # App config
    st.set_page_config(
        page_title="🏠 AI Real Estate Analyst",
        layout="centered",
        page_icon="🏡"
    )
    st.title("🏠 AI Real Estate Analyst")
    
    # Initialize
    model = configure_app()
    init_session()
    load_dotenv()  # Only needed locally
    
    # Display chat
    display_chat()
    if st.session_state.first_interaction:
        show_welcome()
        st.session_state.first_interaction = False
    
    # User input
    if user_input := st.chat_input("Ask about properties..."):
        # Update chat
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                reply = generate_response(user_input, model)
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                
                # Update property details
                if any(keyword in user_input.lower() for keyword in ["worth", "value", "price"]):
                    st.session_state.property_details = extract_property_details(user_input)
    
    # Sidebar tools
    render_sidebar_tools(model)

if __name__ == "__main__":
    main()
