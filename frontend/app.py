import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import base64
import io


st.set_page_config(
    page_title="Finance Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-dark: #182c40;
        --primary-medium: #20374e;
        --primary-light: #28415b;
        --accent-red: #dc6868;
        --background-main: #f8f9fc;
        --background-card: #ffffff;
        --background-secondary: #f1f4f8;
        --text-primary: #182c40;
        --border-light: #e2e8f0;
        --shadow-card: 0 2px 12px rgba(24, 44, 64, 0.12);
        --hover-light: #fafafa;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8f9fc 0%, #f1f4f8 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: var(--primary-dark);
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, var(--background-card) 0%, var(--background-secondary) 100%);
        border-radius: 20px;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--border-light);
    }
    
    .response-card {
        background: var(--background-card);
        color: var(--text-primary);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-card);
        border: 2px solid var(--primary-light);
    }
    
    .response-card h3 {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .stButton > button {
        background: transparent !important;
        color: var(--primary-dark) !important;
        border: 2px solid var(--primary-medium) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.8rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: var(--hover-light) !important;
        color: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(24, 44, 64, 0.15) !important;
    }
    
    div[data-testid="column"]:nth-child(3) .stButton > button {
        background: transparent !important;
        color: var(--accent-red) !important;
        border: 2px solid var(--accent-red) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.8rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: #fef2f2 !important;
        color: var(--accent-red) !important;
        border-color: #c53030 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(220, 104, 104, 0.2) !important;
    }
    
    .stButton > button[kind="primary"] {
        background: transparent !important;
        color: var(--primary-dark) !important;
        border: 3px solid var(--primary-dark) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.8rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: var(--hover-light) !important;
        color: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(24, 44, 64, 0.2) !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--background-card);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-light);
        box-shadow: 0 0 0 3px rgba(24, 44, 64, 0.1);
    }
    
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] > div {
        background: #ffffff !important;
        color: #182c40 !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #182c40 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    p {
        color: var(--text-primary);
        line-height: 1.6;
    }
</style>


""", unsafe_allow_html=True)






class Config:
    ORCHESTRATOR_URL = "http://localhost:8005"
    VOICE_AGENT_URL = "http://localhost:8004"  
    DEFAULT_TICKERS = ["AAPL", "TSMC", "NVDA"]
    QUERY_TEMPLATES = [
        "What are the prices that my stocks are trading at?",
        "Highlight any earnings surprises in my portfolio",
        "Show me the current market sentiment for my stocks", 
        "What are the key risk factors I should be aware of today?",
    ]


def init_session_state():
    defaults = {
        'selected_tickers': Config.DEFAULT_TICKERS.copy(),
        'voice_enabled': True,  
        'current_analysis': None,
        'last_health_check': None,
        'voice_capabilities': None,
        'current_audio': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def check_voice_capabilities() -> Optional[Dict]:
    """Check voice agent capabilities"""
    try:
        response = requests.get(f"{Config.VOICE_AGENT_URL}/capabilities", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None

def generate_voice_response(text: str) -> Optional[bytes]:
    """Generate voice response from text"""
    try:
        payload = {"text": text, "voice_speed": 150}
        response = requests.post(
            f"{Config.VOICE_AGENT_URL}/tts",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type:
                return response.content
            else:
                
                return None
    except requests.RequestException as e:
        st.error(f"Voice generation error: {str(e)}")
    return None

def test_voice_service() -> bool:
    """Test voice service with sample TTS"""
    try:
        response = requests.get(f"{Config.VOICE_AGENT_URL}/test-tts", timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_orchestrator_health() -> Optional[Dict]:
    """Check orchestrator and all agent services health"""
    try:
        response = requests.get(f"{Config.ORCHESTRATOR_URL}/health", timeout=10)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None

def send_query(query: str, tickers: List[str], use_voice: bool = False) -> Optional[Dict]:
    """Send query to orchestrator"""
    try:
        payload = {
            "query": query,
            "tickers": tickers,
            "use_voice": use_voice
        }
        
        response = requests.post(
            f"{Config.ORCHESTRATOR_URL}/query",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    
    except requests.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
    
    return None

def test_system() -> Optional[Dict]:
    """Test the complete system pipeline"""
    try:
        response = requests.get(f"{Config.ORCHESTRATOR_URL}/test", timeout=30)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-title">Your Financial Assistant</h1>', unsafe_allow_html=True)

def render_voice_status():
    """Render voice service status in sidebar"""
    st.sidebar.markdown("### Voice Services")
    
    if st.sidebar.button("Check Voice Service", use_container_width=True):
        with st.spinner("Checking voice capabilities..."):
            st.session_state.voice_capabilities = check_voice_capabilities()
    
    voice_caps = st.session_state.voice_capabilities
    
    if voice_caps:
        tts_status = "healthy" if voice_caps.get('tts_available') else "offline"
        stt_status = "healthy" if voice_caps.get('stt_available') else "offline"
        
        status_class_tts = "status-healthy" if tts_status == "healthy" else "status-offline"
        status_class_stt = "status-healthy" if stt_status == "healthy" else "status-offline"
        
        st.sidebar.markdown(f"""
        <div style="margin: 0.8rem 0;">
            <strong style="color: var(--text-primary);">Text-to-Speech</strong><br>
            <span class="{status_class_tts}">{tts_status.upper()}</span>
        </div>
        <div style="margin: 0.8rem 0;">
            <strong style="color: var(--text-primary);">Speech-to-Text</strong><br>
            <span class="{status_class_stt}">{stt_status.upper()}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("Test Voice Output", use_container_width=True):
            with st.spinner("Testing voice output..."):
                if test_voice_service():
                    st.sidebar.success("Voice test successful!")
                else:
                    st.sidebar.error("Voice test failed")
    else:
        st.sidebar.error("Cannot connect to voice service")

def render_service_status():
    """Render service status in sidebar"""
    st.sidebar.markdown("### System Status")
    
    if st.sidebar.button("Check Services", use_container_width=True):
        with st.spinner("Checking services..."):
            st.session_state.last_health_check = check_orchestrator_health()
    
    health_data = st.session_state.last_health_check
    
    if health_data:
        services = health_data.get('services', {})
        
        for service_name, status in services.items():
            status_class = "status-healthy" if status == "healthy" else "status-offline"
            display_name = service_name.replace('_', ' ').title()
            
            st.sidebar.markdown(f"""
            <div style="margin: 0.8rem 0;">
                <strong style="color: var(--text-primary);">{display_name}</strong><br>
                <span class="{status_class}">{status.upper()}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.error("Cannot connect to orchestrator")

def render_portfolio_config():
    """Render portfolio configuration in sidebar"""
    st.sidebar.markdown("### Stocks in Your Portfolio")
    
    # Ticker input
    tickers_input = st.sidebar.text_input(
        "Stock Tickers (comma separated)",
        value=",".join(st.session_state.selected_tickers),
        help="Enter stock symbols separated by commas"
    )
    
    # Update tickers
    new_tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]
    if new_tickers != st.session_state.selected_tickers:
        st.session_state.selected_tickers = new_tickers
    
    # Display current portfolio
    if st.session_state.selected_tickers:
        st.sidebar.success(f"Tracking {len(st.session_state.selected_tickers)} stocks")
        for ticker in st.session_state.selected_tickers:
            st.sidebar.markdown(f"• **{ticker}**")

def render_system_test():
   
    st.sidebar.markdown("### System Test")
    
    if st.sidebar.button("Test Pipeline", use_container_width=True):
        with st.spinner("Testing complete pipeline..."):
            test_result = test_system()
            
            if test_result and test_result.get('status') == 'success':
                st.sidebar.success("System test passed!")
                
            else:
                st.sidebar.error("System test failed")
                

def render_query_interface():
    """Render the main query interface"""
    st.markdown("### Quick Query Templates")
    
    cols = st.columns(2)
    
    for i, template in enumerate(Config.QUERY_TEMPLATES):
        col = cols[i % 2]
        if col.button(f"{template[:50]}...", key=f"template_{i}", use_container_width=True):
            st.session_state.current_query = template
    
    # Query input
    query = st.text_area(
        "Or enter your custom query:",
        value=getattr(st.session_state, 'current_query', ''),
        height=120,
        placeholder="Ask about portfolio risk, market analysis, earnings updates, or any financial insights..."
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        analyze_button = st.button(
            "Fetch Results",
            type="primary",
            use_container_width=True,
            disabled=not query or not st.session_state.selected_tickers
        )
    
    with col2:
        voice_button = st.button(
            "Voice Query",
            use_container_width=True,
            disabled=True,
            help="Voice input yet to be added. Please input via text."
        )
    
    with col3:
        clear_button = st.button(
            "Clear",
            use_container_width=True
        )
    
    if clear_button:
        st.session_state.current_analysis = None
        st.session_state.current_audio = None
        if hasattr(st.session_state, 'current_query'):
            del st.session_state.current_query
        st.rerun()
    
    return analyze_button, query

def render_audio_player(audio_data: bytes, response_text: str):
    """Render audio player for voice response"""
    
    

    audio_base64 = base64.b64encode(audio_data).decode()
    

    audio_html = f"""
    <div class="audio-player">
        <p><strong>Text:</strong> {response_text[:200]}{'...' if len(response_text) > 200 else ''}</p>
        <audio controls style="width: 100%; margin-top: 1rem;">
            <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <div style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted);">
             Click play to hear the response
        </div>
    </div>
    """
    
    st.markdown(audio_html, unsafe_allow_html=True)

def render_analysis_results(analysis_data: Dict):
    """Render full text response ABOVE voice output"""
    response = analysis_data.get('response', 'No response available')
    
    
    with st.container():
        st.markdown(f"""
        <div class="response-card">
            <h3>Analysis Response</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; white-space: pre-wrap;">{response}</p>
        </div>
        """, unsafe_allow_html=True)
    

    st.markdown("---")
    
    
    st.markdown("### Voice Response")
 
    if st.session_state.current_audio is None:
        with st.spinner("Generating voice response..."):
            audio_data = generate_voice_response(response)
            if audio_data:
                st.session_state.current_audio = audio_data
                st.success("Voice response generated!")
            else:
                st.warning("Voice generation not available or failed")
    
   
    if st.session_state.current_audio:
        render_audio_player(st.session_state.current_audio, response)
    else:
        st.info("Voice output not available - text response shown above")

def process_query(query: str):
    """Process the user query"""
    with st.spinner("Processing your query..."):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Sending query to orchestrator...")
        progress_bar.progress(20)
        
        result = send_query(query, st.session_state.selected_tickers, st.session_state.voice_enabled)
        
        if result:
            status_text.text("Analysis complete!")
            progress_bar.progress(100)
          
            st.session_state.current_analysis = result
            st.session_state.current_audio = None  
            
    
            progress_bar.empty()
            status_text.empty()
            
            return True
        else:
            status_text.text("Query failed")
            progress_bar.empty()
            return False


def main():
    init_session_state()
    

    render_header()
    

    with st.sidebar:
        
        render_portfolio_config()
        st.divider()
        render_system_test()
    

    analyze_button, query = render_query_interface()
    

    if analyze_button and query:
        if process_query(query):
            st.success("Query processed successfully!")
        else:
            st.error("Failed to process query. Please check your services.")
    

    if st.session_state.current_analysis:
        st.divider()
        render_analysis_results(st.session_state.current_analysis)
    

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: var(--text-muted); padding: 1rem;'>"
        
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
