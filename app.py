import os
import re
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load secrets (for Streamlit Cloud)
if st.secrets:
    for key, value in st.secrets.items():
        os.environ[key] = value
else:
    # Fallback for local development
    load_dotenv(".env")
# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in your .env file.")
    st.stop()

# Configure Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# App configuration
st.set_page_config(
    page_title="🏠 AI Real Estate Analyst", 
    layout="centered",
    page_icon="🏡"
)
st.title("🏠 AI Real Estate Analyst")
st.caption("Get instant property valuations, market insights, and investment advice!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.property_details = {}
    st.session_state.first_interaction = True

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initial assistant greeting
if st.session_state.first_interaction:
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
    
    **General Questions**:
    - "Explain cap rates"
    - "What's a 1031 exchange?"
    """
    st.session_state.chat_history.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)
    st.session_state.first_interaction = False

# Chat input
user_input = st.chat_input("Ask about properties, markets, or investments...")

if user_input:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process real estate query
    prompt = f"""
    You're an expert real estate analyst with 20 years experience. The user asked:
    "{user_input}"
    
    Respond following these guidelines:
    
    1. **Valuation Requests**:
       - Ask for missing details (sqft, beds/baths, location, condition)
       - Provide price range based on recent comps
       - Example: "3-bed in Chicago ≈ $450K-$520K based on West Loop comps"
    
    2. **Market Analysis**:
       - Compare year-over-year trends
       - Highlight inventory levels
       - Example: "Austin prices up 8% YoY with 3 months inventory"
    
    3. **Investment Questions**:
       - Calculate potential ROI
       - Mention tax implications
       - Example: "Phoenix rentals show 6.5% cap rate, consider 1031 exchange"
    
    4. **General Knowledge**:
       - Explain concepts simply
       - Provide examples
    
    Format responses with:
    - 📊 Data points
    - 📍 Location context
    - 💡 Actionable advice
    - ⚠️ Risks/caveats
    
    If information is incomplete, ask ONE clarifying question.
    """
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing real estate data..."):
            try:
                response = model.generate_content(prompt)
                reply = response.text
                
                # Extract and store property details if mentioned
                if any(word in user_input.lower() for word in ["worth", "value", "price", "valuation"]):
                    details = {
                        "location": re.search(r'in\s(.+?)$', user_input, re.I),
                        "size": re.search(r'(\d+)\s*(sqft|square feet)', user_input, re.I),
                        "beds": re.search(r'(\d+)\s*bed', user_input, re.I)
                    }
                    st.session_state.property_details.update(
                        {k: v.group(1) for k, v in details.items() if v}
                    )
                
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                error_msg = f"⚠️ Error analyzing property: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Sidebar with property details and tools
with st.sidebar:
    st.subheader("Property Toolkit")
    
    if st.session_state.property_details:
        st.write("**Current Property**")
        for k, v in st.session_state.property_details.items():
            st.write(f"- {k.capitalize()}: {v}")
    else:
        st.write("No property details saved")
    
    st.divider()
    
    # Quick analysis tools
    st.write("**Quick Analysis**")
    if st.button("Calculate Mortgage"):
        with st.chat_message("assistant"):
            if "location" in st.session_state.property_details:
                prompt = f"Estimate monthly mortgage for {st.session_state.property_details.get('size', '')} property in {st.session_state.property_details['location']} at current rates"
                response = model.generate_content(prompt)
                st.markdown(response.text)
            else:
                st.warning("Please provide location and price first")
    
    if st.button("Rental Estimate"):
        with st.chat_message("assistant"):
            if "location" in st.session_state.property_details:
                prompt = f"Estimate rental income for {st.session_state.property_details.get('beds', '')} bedroom in {st.session_state.property_details['location']}"
                response = model.generate_content(prompt)
                st.markdown(response.text)
            else:
                st.warning("Please provide location and bedroom count")
    
    st.button("Clear Session", on_click=lambda: st.session_state.clear())
