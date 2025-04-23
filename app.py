import streamlit as st
import google.generativeai as genai

# ==================== SETUP & CONFIGURATION ====================
# Configure Gemini API (using Streamlit Secrets)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    st.error(f"🔐 Configuration Error: {str(e)}\n\n"
             "Please ensure you've set up your API key in Streamlit Secrets:\n"
             "1. Go to app settings → Secrets\n"
             "2. Add: [secrets]\n"
             "3. GEMINI_API_KEY = 'your_key_here'")
    st.stop()

# ==================== STREAMLIT UI CONFIG ====================
st.set_page_config(
    page_title="🏠 AI Real Estate Analyst Pro",
    page_icon="🏡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatInput textarea {
        color: #000000 !important;
        background-color: #f8f9fa !important;
    }
    [data-testid="stChatMessage"] [data-testid="user"] {
        background-color: #f0f2f6;
    }
    [data-testid="stChatMessage"] [data-testid="assistant"] {
        background-color: #e3f2fd;
    }
    .st-emotion-cache-6qob1r {
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
    }
</style>
""", unsafe_allow_html=True)

# ==================== CHATBOT FUNCTIONALITY ====================
REAL_ESTATE_CONTEXT = """You are a professional real estate analyst with 15+ years experience. 
Provide specific, actionable advice with these rules:
1. Always mention location context
2. Include current market data when possible
3. Give comparative analysis (e.g., "Compared to last year...")
4. Use bullet points for complex advice
5. Suggest next steps for buyers/sellers/investors"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "🏡 Welcome to AI Real Estate Analyst! I can help with:\n\n"
                   "- 🏠 Property valuations\n"
                   "- 📈 Market trend analysis\n"
                   "- 💰 Investment opportunities\n"
                   "- 📊 Comparative market analysis\n\n"
                   "What would you like to analyze today?"
    }]

# ==================== SIDEBAR TOOLS ====================
with st.sidebar:
    st.title("🛠️ Real Estate Toolkit")
    st.subheader("Quick Analysis Tools")
    
    tool = st.radio(
        "Select analysis type:",
        ["💬 General Query", 
         "💰 Valuation Estimate", 
         "📊 Market Trends",
         "🏗️ Investment Analysis"],
        index=0
    )
    
    if tool == "💰 Valuation Estimate":
        with st.form("valuation_form"):
            property_type = st.selectbox("Property Type", ["House", "Condo", "Apartment", "Commercial"])
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, value=3)
            location = st.text_input("Location (City/Neighborhood)")
            
            if st.form_submit_button("Get Estimate"):
                prompt = f"""Provide a detailed valuation estimate for a {bedrooms}-bedroom {property_type} 
                in {location}. Include:\n1. Price range\n2. Comparable sales\n3. Market conditions\n4. Suggested listing strategy"""
                st.session_state.messages.append({"role": "user", "content": prompt})
    
    elif tool == "📊 Market Trends":
        with st.form("trends_form"):
            location = st.text_input("Location")
            timeframe = st.selectbox("Timeframe", ["Last 3 months", "Last 6 months", "Last year", "Last 5 years"])
            
            if st.form_submit_button("Analyze Trends"):
                prompt = f"""Provide detailed market trends for {location} over {timeframe}. 
                Include:\n1. Price changes\n2. Inventory levels\n3. Days on market\n4. Buyer/seller balance"""
                st.session_state.messages.append({"role": "user", "content": prompt})
    
    elif tool == "🏗️ Investment Analysis":
        with st.form("investment_form"):
            property_type = st.selectbox("Property Type", ["Residential", "Commercial", "Rental", "Vacation"])
            budget = st.text_input("Budget Range")
            location = st.text_input("Target Location")
            
            if st.form_submit_button("Analyze Investment"):
                prompt = f"""Provide investment analysis for {property_type} properties in {location} 
                with {budget} budget. Include:\n1. ROI estimates\n2. Risk factors\n3. Recommended areas\n4. Management strategies"""
                st.session_state.messages.append({"role": "user", "content": prompt})

# ==================== CHAT INTERFACE ====================
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask about real estate...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing real estate data..."):
            try:
                response = model.generate_content(f"{REAL_ESTATE_CONTEXT}\n\nUser Query: {user_input}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
