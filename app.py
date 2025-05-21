# -*- coding: utf-8 -*-
"""
Sonar Analysis Hub v1.3 📡🌊 (Perplexity AI Integration)
A web-app for visualizing and analyzing and uploaded sonar data.
Features: Sonar Scan Exploration, New Scan , Sonar Data Upload, AI Analysis of Uploads, Technology Information, Perplexity AI Assistant.
"""

# --- Imports ---
import streamlit as st
import json         # For pretty printing JSON output and data export
import time         # For  delays
from datetime import datetime, timezone, timedelta # For timestamps
import pandas as pd # For data manipulation and CSV reading
import plotly.express as px # For interactive charts
from openai import OpenAI # For Perplexity AI
import re           # For cleaning markdown
import numpy as np  # For generating sample sonar data (e.g., spectrograms)
from PIL import Image # For handling image uploads
import io # For handling file streams

# --- Early Configuration: MUST BE FIRST STREAMLIT COMMAND ---
st.set_page_config(
    page_title="Sonar Analysis Hub📡 (Perplexity AI)",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📡" # New Sonar Icon
)

# --- Configuration ---
# --- User MUST Configure These Using Streamlit Secrets ---
# Example structure in secrets.toml:
# [perplexity_api]
# api_key = "YOUR_PERPLEXITY_API_KEY" 
# # Note: The Perplexity API key might start with "pplx-"
# [sonar_data_api] # Placeholder for potential future API
# base_url = "YOUR_SONAR_DATA_API_ENDPOINT"
# api_key = "YOUR_SONAR_DATA_API_KEY"

try:
    PERPLEXITY_API_KEY = st.secrets["perplexity_api"]["api_key"]
except (AttributeError, KeyError, TypeError): # Added TypeError for st.secrets being None
    st.error("🚨 **Config Error:** Perplexity API Key (`perplexity_api.api_key`) missing. Perplexity AI Assistant disabled.", icon="⚙️")
    PERPLEXITY_API_KEY = None

# Placeholder for future Sonar Data API config
SONAR_API_BASE_URL = st.secrets.get("sonar_data_api", {}).get("base_url")
SONAR_API_KEY = st.secrets.get("sonar_data_api", {}).get("api_key")


# --- System Instruction for Perplexity AI (Sonar Focus) ---
APP_LOAD_TIME_STR = datetime.now().strftime('%A, %B %d, %Y')
SONAR_SYSTEM_INSTRUCTION = f"""You are the Sonar Perplexity AI Analysis Assistant, integrated into the Sonar Analysis Hub.
Your purpose is to provide helpful and informative responses regarding sonar principles, data interpretation, target classification concepts, and the functionalities of this hub.
This hub allows users to explore sonar scans (Sea, Land, Air), simulate new scans, upload their own sonar-related images/data for basic viewing and AI analysis, and learn about different sonar technologies.

The dashboard functionalities you can refer to include:
- Exploring existing sonar scans using a Scan ID (e.g., SEA001, LAND001, AIR001). This includes viewing metadata, spectrograms/radargrams, and detected targets. Users can also download scan data as JSON.
- Simulating a new sonar scan by providing basic parameters. Results can be downloaded as JSON.
- Uploading sonar images (PNG, JPG) or basic data files (CSV, TXT) for display.
- **AI Analysis of Uploaded Content:**
  - If the user mentions an 'uploaded image', 'the visual', 'the picture', 'the photo', they are referring to an image they have uploaded to the dashboard. You will NOT receive the image data directly. You should attempt to discuss it based on its filename (if mentioned by the user) and the user's description or query about it.
  - For an 'uploaded data file' (CSV, TXT) or its filename, a text snippet of its content *will* be provided appended to the user's query. Please base your analysis on this provided text content. Describe visual elements in sonar images if appropriate (e.g., shapes, textures, potential anomalies based on user's description) or interpret patterns in data snippets.
- Viewing detailed information about sonar technologies (e.g., Side-Scan Sonar, GPR, Ultrasonic).
- Finding contact information.

Be concise, accurate, and maintain a helpful, professional tone.
Do NOT invent specific real-time scan data unless it's explicitly provided in the user's query for a hypothetical scenario.
If asked about specific live data *visible only* on the dashboard (like a specific scan result the user just performed or an uploaded image they haven't specifically asked you to analyze with the content provided), explain that you don't have direct real-time access to the dashboard's *current state* but can explain *how* the user can find that information using the dashboard's tabs or provide general information about how sonar data exploration or file uploading works. If they want you to analyze an uploaded file, they need to explicitly ask you to analyze 'the uploaded image/file' or refer to its name.

You can answer general questions about:
- Sonar Principles: How sonar works (acoustic waves, echoes, etc.), different frequencies and their uses.
- Sonar Technologies: Side-Scan Sonar (SSS), Multi-Beam Echosounders (MBES), Ground Penetrating Radar (GPR), Ultrasonic Sensors. Explain what these entail and their common applications.
- Data Interpretation: General tips on interpreting spectrograms/radargrams (e.g., what strong reflections, shadows, or specific patterns might indicate).
- Target Classification: High-level concepts (e.g., how patterns and signal characteristics can help differentiate objects; mention that advanced systems might use AI/machine learning like Convolutional Neural Networks (CNNs) for tasks such as acoustic classification, as explored in research like the Nature article s41598-019-40765-6).
- Factors affecting sonar performance (e.g., water conditions, soil type, frequency).

Keep responses well-formatted using markdown.
Today's date is {APP_LOAD_TIME_STR}. Use this date for context if needed.
Encourage users to use the "Explore Scan Data", "Simulate New Scan", or "Upload & Analyze Sonar Data" features for practical examples.
"""

# --- Apply Custom CSS ---
st.markdown(
    """
<style>
    /* --- Global Font Imports --- */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

   /* --- Base Body & App Styling --- */
    body {
        font-family: 'Open Sans', sans-serif;
        color: #E0E0E0; /* Lighter gray for text */
    }

    .stApp {
        background-image: url('https://i.imgur.com/bBitsSE.png');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-color: #121212; /* Dark fallback */
    }

    /* --- Content Containers Backgrounds for Readability over background image --- */
    .stSidebar,
    .stTabs > div[role="tabpanel"] > div, /* Tab content wrapper */
    .stChatMessage > div, /* Inner div of chat message for background */
    div[data-testid="stExpander"] > div:nth-child(2), /* Expander content */
    div[data-testid="stAlert"] > div[role="alert"],
    .stDataFrame {
        background-color: rgba(30, 30, 33, 0.94); /* Dark, highly opaque background */
        border-radius: 8px;
        padding: 1rem; /* Default padding for these blocks */
        margin-bottom: 1rem; /* Default spacing */
    }
    /* Override default padding for specific elements if needed */
     .stChatMessage > div { padding: 10px 15px; margin-bottom: 0;}
     .stDataFrame { padding: 0; } /* Dataframe handles its own padding */


    .stSidebar {
        background-color: rgba(37, 37, 40, 0.96) !important;
        border-right: 1px solid #383838;
        padding: 20px 15px !important;
        margin-bottom: 0; /* Sidebar doesn't need bottom margin */
    }

    /* Tab headers container */
    .stTabs > div[role="tablist"] {
       background-color: rgba(42, 42, 46, 0.90) !important;
       padding: 8px 8px 0px 8px; /* Padding around tab buttons */
       border-radius: 8px 8px 0 0;
       margin-bottom: 0;
    }
    /* Active Tab Button */
    .stTabs button[aria-selected="true"] {
        background-color: rgba(0, 174, 239, 0.2); /* Light blue highlight for active tab */
        color: #00AEEF;
        border-bottom: 3px solid #00AEEF;
    }
     /* Tab panels (content area) */
    .stTabs > div[role="tabpanel"] > div {
        background-color: rgba(30, 30, 33, 0.94);
        padding: 0; /* Scrollable content will have padding */
        border-radius: 0 0 8px 8px;
        margin-bottom: 1rem;
    }

    .scrollable-tab-content {
        background-color: rgba(34, 34, 37, 0.96) !important;
        max-height: 75vh; /* Adjusted for potentially more content */
        overflow-y: auto;
        overflow-x: hidden;
        padding: 20px;
        border: 1px solid #383838;
        border-radius: 5px;
        margin-top: 0px; /* Was 10px, remove if tab panel handles spacing */
    }
    .scrollable-tab-content::-webkit-scrollbar { width: 10px; }
    .scrollable-tab-content::-webkit-scrollbar-track { background: #2a2a2e; border-radius: 5px; }
    .scrollable-tab-content::-webkit-scrollbar-thumb { background-color: #007bff; border-radius: 5px; }
    .scrollable-tab-content::-webkit-scrollbar-thumb:hover { background-color: #0056b3; }

    .tech-card, .scan-result-container {
        background-color: rgba(42, 42, 46, 0.95) !important;
        border: 1px solid #383838;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    /* Ensure card/container specific padding overrides the generic one if needed */
    .tech-card { padding: 20px; }
    .scan-result-container { padding: 25px; margin-top:20px;}


    /* --- Title Styles --- */
    .main-title, .sub-title, h1, h2, h3, h4, h5, h6 {
        background-color: transparent !important; /* Titles should not have their own background box */
        padding: 0 !important; /* Reset padding if it was inherited */
    }
    .main-title {
        font-size: 42px; font-family: 'Roboto', sans-serif; font-weight: 700; color: #00AEEF;
        text-align: center; margin-bottom: 10px; padding-top: 20px;
    }
    .sub-title {
        font-size: 18px; font-family: 'Open Sans', sans-serif; color: #B0B0B0;
        text-align: center; margin-bottom: 30px; opacity: 0.9;
    }
    .sidebar-title {
        font-family: 'Roboto', sans-serif; font-weight: 600; font-size: 24px; color: #00AEEF; margin-bottom: 15px;
    }
    .ai-assistant-title {
        font-family: 'Roboto', sans-serif; font-weight: 600; font-size: 1.3em; color: #00AEEF;
        margin-top: 20px; margin-bottom: 10px;
    }

    /* General Text */
    p, div, textarea, input, select, span, li, a, label, .stMarkdown p, .stMarkdown li {
        color: #D0D0D0;
        font-family: 'Open Sans', sans-serif;
        font-size: 1em;
    }
     .tab-description {
       font-size: 1.0em; color: #A0A0A0; margin-bottom: 20px; font-style: italic; opacity: 0.9;
    }

    /* --- General Element Styling (Buttons, Inputs etc.) --- */
    .stButton>button {
        font-family: 'Roboto', sans-serif; font-weight: 500; color: #FFFFFF; background-color: #007bff;
        border: 1px solid #0069d9; transition: all 0.2s ease-out; padding: 10px 20px; border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #0069d9; border-color: #005cbf; transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,174,239,0.2);
    }
    .stButton>button:active { transform: translateY(0px); box-shadow: 0 1px 2px rgba(0,174,239,0.1); }
    .stButton>button:disabled { background-color: #555555; color: #999999; border-color: #444444; }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto', sans-serif; color: #00AEEF; font-weight: 600;
    }
    h1 { font-size: 2.2em; margin-bottom: 0.7em; }
    h2 { font-size: 1.8em; margin-bottom: 0.6em; }
    h3 { font-size: 1.4em; margin-bottom: 0.5em; }


    /* Input Fields */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stNumberInput>div>div>input,
    .stDateInput>div>div>input,
    .stSelectbox>div>div>div,
    .stFileUploader > div > div > div > button { /* File uploader button */
        color: #E0E0E0 !important;
        background-color: rgba(42, 42, 46, 0.98) !important; /* Opaque input background */
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
        padding: 10px;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stNumberInput>div>div>input:focus,
    .stDateInput>div>div>input:focus {
        border-color: #00AEEF !important;
        box-shadow: 0 0 0 0.2rem rgba(0,174,239,.25) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div { /* Dropdown arrow and text */
        background-color: rgba(42, 42, 46, 0.98) !important;
        color: #E0E0E0 !important;
    }
     /* File uploader text */
    .stFileUploader p {
        color: #B0B0B0 !important;
    }


    /* Dataframes */
    .stDataFrame {
        border: 1px solid #444444; border-radius: 5px; background-color: rgba(42, 42, 46, 0.98) !important;
    }
    .stDataFrame thead th {
        background-color: rgba(51, 51, 51, 0.99) !important; color: #00AEEF;
        font-family: 'Roboto', sans-serif; font-weight: 500;
    }
    .stDataFrame tbody tr td {
        color: #D0D0D0; font-family: 'Open Sans', sans-serif; border-color: #444444;
    }
    .stDataFrame tbody tr:hover { background-color: #383838 !important; }


    /* --- SIDEBAR STYLES specific overrides --- */
    .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 { color: #00AEEF; }
    .stSidebar p, .stSidebar li, .stSidebar a, .stSidebar .stRadio > label {
        color: #C0C0C0; font-family: 'Open Sans', sans-serif; font-size: 0.95em;
    }
    .stSidebar .stExpander {
         border: 1px solid #444444; border-radius: 4px;
         background-color: rgba(42, 42, 46, 0.9) !important; /* Expander specific background */
         margin-bottom: 10px;
    }
     .stSidebar .stExpander header {
         color: #00AEEF; font-family: 'Roboto', sans-serif; font-weight: 500;
         background-color: rgba(42, 42, 46, 0.9) !important; /* Ensure header matches */
     }
     .stSidebar .stExpander > div:nth-child(2) { /* Expander content area */
        background-color: rgba(30, 30, 33, 0.92) !important; /* Slightly different for content */
        padding: 10px;
     }
     .stSidebar .stExpander a { color: #00BFFF !important; }
     .stSidebar .stExpander a:hover { color: #60DFFF !important; }
    .stSidebar .stMetric label { color: #00AEEF; }
    .stSidebar .stMetric .stMetricValue { color: #E0E0E0; }


     /* --- Chat Specific Styles --- */
    [data-testid="chatAvatarIcon-user"] svg { fill: #00AEEF; }
    [data-testid="chatAvatarIcon-assistant"] svg { fill: #33CC33; }

    .stChatMessage { /* The outer container Streamlit creates */
        background-color: transparent !important; /* Make outer transparent */
        border: none;
        border-radius: 8px;
        margin-bottom: 15px;
        padding: 0;
    }
    .stChatMessage > div { /* The inner div we targetted for background */
        background-color: rgba(42, 42, 46, 0.96) !important; /* Chat bubble background */
        border: 1px solid #444444;
        /* padding and margin-bottom already defined under general content containers */
    }
     .stChatMessage p, .stChatMessage li { color: #D0D0D0; font-family: 'Open Sans', sans-serif; }
     .stChatMessage code { background-color: #333333; color: #FFD700; border: 1px solid #555555; }
     .stChatMessage pre > code { background-color: #1C1C1C !important; color: #E0E0E0 !important; }
     .stChatMessage a { color: #00BFFF !important; }
     .stChatMessage a:hover { color: #60DFFF !important; }

    .stChatInput textarea {
        background-color: rgba(51, 51, 51, 0.98) !important; color: #E0E0E0 !important;
        border: 1px solid #555555 !important;
    }
     .stChatInput textarea:focus {
        border-color: #00AEEF !important; box-shadow: 0 0 0 0.2rem rgba(0,174,239,.25) !important;
     }
     div[data-testid="stChatInput"] { /* Chat input container */
        background-color: rgba(37, 37, 40, 0.92) !important; /* Match sidebar elements */
        padding: 10px 0px;
     }

    /* --- Alerts (Info/Success/Error/Warning) --- */
    div[data-testid="stAlert"] > div[role="alert"] {
        border-radius: 5px; border-width: 1px; opacity: 0.98; padding: 0.8rem 1rem;
    }
    /* Ensure alert backgrounds are opaque enough */
    div[data-testid="stAlert"] > div[role="alert"][class*="st-ae"] { /* Success */
        background-color: rgba(30, 70, 32, 0.95) !important; border-color: #2A8F2E; color: #A6D7A7;
    }
    div[data-testid="stAlert"] > div[role="alert"][class*="st-b7"] { /* Info */
        background-color: rgba(16, 53, 82, 0.95) !important; border-color: #1976D2; color: #90CAF9;
    }
    div[data-testid="stAlert"] > div[role="alert"][class*="st-b6"] { /* Error */
        background-color: rgba(82, 16, 16, 0.95) !important; border-color: #D32F2F; color: #F99090;
    }
    div[data-testid="stAlert"] > div[role="alert"][class*="st-b5"] { /* Warning */
        background-color: rgba(82, 53, 16, 0.95) !important; border-color: #F57C00; color: #F9C990;
    }

    /* Plotly charts specific background if needed */
    .stPlotlyChart .plotly, .plotly-graph-div {
        background-color: #2a2a2e !important; /* Solid dark background for chart itself */
        border-radius: 6px;
    }
    /* Ensure Plotly chart container doesn't get unwanted semi-transparent background */
     div[data-testid="stPlotlyChart"] {
        background-color: transparent !important;
        padding: 0 !important;
        margin-bottom: 1rem; /* Spacing for the chart block */
     }

</style>
    """,
    unsafe_allow_html=True,
)

# --- Global Variables &  Data ---

def generate__spectrogram(target_type="clear", height=128, width=256):
    """Generates a simple noisy spectrogram with a potential target signature."""
    data = np.random.rand(height, width) * 0.3 # Background noise
    if target_type == "object_strong": # Large, clear object
        y_center, x_center = height // 2, width // 2
        y_range, x_range = height // 7, width // 5 # Made slightly larger
        data[y_center - y_range : y_center + y_range, x_center - x_range : x_center + x_range] += np.random.rand(2*y_range, 2*x_range) * 0.75 # Stronger signal
        # Add some seabed reflection if applicable (e.g., sea context)
        if height > 50 and "Sea" in st.session_state.get("current_sim_type",""): # check context if available
             data[int(height*0.8):int(height*0.95), :] += 0.25 + np.random.rand(int(height*0.15), width)*0.1
    elif target_type == "object_faint": # Smaller, less distinct object
        y_center, x_center = height // rnd_choice([2,3,4]), width // rnd_choice([2,3,4]) # Randomized position
        y_range, x_range = height // rnd_choice([10,12,15]), width // rnd_choice([6,8,10]) # Smaller size
        data[y_center - y_range : y_center + y_range, x_center - x_range : x_center + x_range] += np.random.rand(2*y_range, 2*x_range) * 0.35 # Fainter signal
    elif target_type == "layered_gpr": # GPR layers
        for i in range(np.random.randint(2,5)): # 2 to 4 layers
            layer_depth = int(height * (0.2 + i*0.2 + np.random.uniform(-0.05, 0.05)))
            thickness = int(height * (0.04 + np.random.rand()*0.06))
            if layer_depth + thickness < height and layer_depth >=0:
                 data[layer_depth:layer_depth+thickness, :] += 0.25 + np.random.rand(thickness, width)*0.2
    elif target_type == "utility_gpr": # GPR hyperbolic signatures for utilities
        num_utilities = np.random.randint(1, 4)
        for _ in range(num_utilities):
            center_x = np.random.randint(width // 4, 3 * width // 4)
            apex_y = np.random.randint(height // 4, height // 2)
            # Simple hyperbolic shape
            for x_offset in range(-width // 8, width // 8):
                y_val = apex_y + int(0.05 * (x_offset**2) / (width/32)) # Exaggerate hyperbola for visibility
                if 0 <= center_x + x_offset < width and 0 <= y_val < height:
                    data[y_val, center_x + x_offset] = min(1, data[y_val, center_x + x_offset] + 0.6)
                    if y_val+1 < height: data[y_val+1, center_x + x_offset] = min(1, data[y_val+1, center_x + x_offset] + 0.4) # Thicken
    elif target_type == "small_objects_sea": # Multiple small, faint objects
        num_objects = np.random.randint(3,7)
        for _ in range(num_objects):
            y_center, x_center = np.random.randint(0, height), np.random.randint(0,width)
            y_r, x_r = height // np.random.randint(18,30), width // np.random.randint(12,20) # very small
            y_start, y_end = max(0, y_center-y_r), min(height, y_center+y_r)
            x_start, x_end = max(0, x_center-x_r), min(width, x_center+x_r)
            if y_start < y_end and x_start < x_end:
                 data[y_start:y_end, x_start:x_end] += np.random.rand(y_end-y_start, x_end-x_start) * np.random.uniform(0.25, 0.45)
    elif target_type == "cluttered_air": # Multiple faint reflections for air sonar
        num_echoes = np.random.randint(5,15)
        for _ in range(num_echoes):
            y_c, x_c = np.random.randint(height//4, height), np.random.randint(width//4, width) # Avoid edge
            y_r, x_r = height // np.random.randint(15,25), width // np.random.randint(10,18)
            y_s,y_e = max(0,y_c-y_r), min(height,y_c+y_r)
            x_s,x_e = max(0,x_c-x_r), min(width,x_c+x_r)
            if y_s < y_e and x_s < x_e:
                data[y_s:y_e, x_s:x_e] += np.random.rand(y_e-y_s, x_e-x_s) * np.random.uniform(0.2, 0.4)
    return np.clip(data, 0, 1)

def rnd_choice(options): # Helper for variety in spectrograms
    return np.random.choice(options)

_SONAR_DATA = {
    "SEA001": {
        "scan_id": "SEA001",
        "sonar_type": "Sea (Side-Scan Sonar)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Coastal Region A1 - Seabed Survey",
        "parameters": {"frequency_khz": 400, "range_m": 150, "depth_m": 45, "operator": "Dr. Sonar"},
        "spectrogram_data": generate__spectrogram("object_strong", height=150, width=300),
        "color_scale": "Viridis",
        "detected_targets": [
            {"id": "TGT001", "type": "Man-Made Object (Possible Wreck)", "confidence": 0.78, "range_m": 75, "size_m_approx": "5x2", "details": "Strong acoustic signature, rectangular shape."},
            {"id": "TGT002", "type": "Natural Rock Formation", "confidence": 0.95, "range_m": 110, "size_m_approx": "8x5", "details": "Irregular shape, matches seabed geology."}
        ],
        "summary": "Scan SEA001 shows a significant man-made object and a large natural rock formation. Seabed appears to be sandy with some undulation."
    },
    "LAND001": {
        "scan_id": "LAND001",
        "sonar_type": "Land (Ground Penetrating Radar - GPR)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Site B - Archeological Dig Area 3",
        "parameters": {"frequency_mhz": 250, "depth_m_max": 5, "survey_line": "L004"},
        "spectrogram_data": generate__spectrogram("layered_gpr", height=200, width=400), # Radargram
        "color_scale": "Plasma",
        "detected_targets": [
            {"id": "TGT003", "type": "Buried Structure (Foundation Wall)", "confidence": 0.82, "depth_m_approx": 1.5, "material_guess": "Stone/Brick", "details": "Linear feature with strong reflection."},
            {"id": "TGT004", "type": "Utility Pipe", "confidence": 0.70, "depth_m_approx": 0.8, "material_guess": "PVC/Metal", "details": "Hyperbolic reflection signature, small diameter."}
        ],
        "summary": "GPR Scan LAND001 reveals a potential buried foundation wall at ~1.5m and a utility pipe closer to the surface."
    },
    "AIR001": {
        "scan_id": "AIR001",
        "sonar_type": "Air (Ultrasonic Array Sensor)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Indoor Test Environment - Chamber 2",
        "parameters": {"frequency_khz": 40, "scan_angle_deg": 90, "max_range_m": 10},
        "spectrogram_data": generate__spectrogram("object_faint", height=100, width=200),
        "color_scale": "Cividis",
        "detected_targets": [
            {"id": "TGT005", "type": "Flat Surface (Wall)", "confidence": 0.98, "distance_m": 5.2, "orientation_deg": 0, "details": "Consistent echo across multiple sensors."},
            {"id": "TGT006", "type": "Small Obstacle", "confidence": 0.65, "distance_m": 2.1, "size_m_approx": "0.3x0.3", "details": "Localized echo, possibly cylindrical."}
        ],
        "summary": "Airborne ultrasonic scan AIR001 mapped a wall at 5.2m and detected a small obstacle at 2.1m."
    },
    "SEA002": {
        "scan_id": "SEA002",
        "sonar_type": "Sea (Side-Scan Sonar - High Frequency)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=5, hours=10)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Shallow Reef Zone - Small Target Search",
        "parameters": {"frequency_khz": 600, "range_m": 75, "depth_m": 20, "operator": "Ops Team Bravo"},
        "spectrogram_data": generate__spectrogram("small_objects_sea", height=120, width=280),
        "color_scale": "Inferno",
        "detected_targets": [
            {"id": "TGT007", "type": "Small Debris Field", "confidence": 0.65, "range_m": 40, "size_m_approx": " Scattered <1m pieces", "details": "Multiple small, weak acoustic signatures."},
            {"id": "TGT008", "type": "Seabed Scour", "confidence": 0.80, "range_m": 55, "size_m_approx": "3m length", "details": "Linear depression on seabed."}
        ],
        "summary": "High-frequency scan SEA002 identified a scattered debris field and seabed scour marks in the shallow reef zone. Several minor anomalies present."
    },
    "LAND002": {
        "scan_id": "LAND002",
        "sonar_type": "Land (Ground Penetrating Radar - GPR)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=3, hours=7)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Urban Area - Utility Mapping Project",
        "parameters": {"frequency_mhz": 400, "depth_m_max": 3, "survey_line": "U007B"},
        "spectrogram_data": generate__spectrogram("utility_gpr", height=180, width=350),
        "color_scale": "Magma", 
        "detected_targets": [
            {"id": "TGT009", "type": "Suspected Gas Line", "confidence": 0.85, "depth_m_approx": 1.2, "material_guess": "Metal/PE", "details": "Clear hyperbolic reflection, medium diameter."},
            {"id": "TGT010", "type": "Possible Conduit/Cable", "confidence": 0.70, "depth_m_approx": 0.6, "material_guess": "Unknown", "details": "Fainter, smaller hyperbolic signature."}
        ],
        "summary": "GPR Scan LAND002 for utility mapping detected a probable gas line at 1.2m and another shallower linear anomaly, possibly a conduit."
    },
    "AIR002": {
        "scan_id": "AIR002",
        "sonar_type": "Air (Ultrasonic Sensor - Multi-Echo Mode)",
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M UTC"),
        "location_": "Cluttered Warehouse Aisle 3",
        "parameters": {"frequency_khz": 50, "scan_angle_deg": 120, "max_range_m": 5},
        "spectrogram_data": generate__spectrogram("cluttered_air", height=110, width=220),
        "color_scale": "Turbo",
        "detected_targets": [
            {"id": "TGT011", "type": "Pallet Rack Shelf", "confidence": 0.90, "distance_m": 2.5, "orientation_deg": -15, "details": "Strong planar reflection."},
            {"id": "TGT012", "type": "Stacked Boxes", "confidence": 0.75, "distance_m": 1.5, "size_m_approx": "1.0x0.8", "details": "Multiple intermittent echoes, irregular shape."},
            {"id": "TGT013", "type": "Overhead Pipe", "confidence": 0.60, "distance_m": 3.8, "size_m_approx": "0.1 diameter", "details": "Weak, localized echo from above scan center."}
        ],
        "summary": "Ultrasonic scan AIR002 in a cluttered warehouse identified a pallet rack, stacked boxes, and a potential overhead pipe."
    }
}


SONAR_TECHNOLOGIES_INFO = [
    {
        "name": "Side-Scan Sonar (SSS)",
        "description": "Generates high-resolution images of the seabed or lakebed by emitting fan-shaped acoustic pulses perpendicular to the direction of motion. Excellent for locating objects, mapping seabed texture, and detailed surveys.",
        "icon": "🌊",
        "details": ["Operates by emitting acoustic pulses and recording the strength and travel time of the returning echoes.", "Creates a 'sonograph' or acoustic image.", "Commonly used for wreck detection, pipeline surveys, geological mapping, and search and recovery operations."]
    },
    {
        "name": "Multi-Beam Echosounder (MBES)",
        "description": "Emits sound waves in a wide swath, allowing for precise bathymetric mapping (depth measurement) and simultaneous backscatter data collection over a large area.",
        "icon": " M", # Placeholder for MultiBeam icon
        "details": ["Collects data from multiple beams simultaneously, creating detailed 3D maps of the seafloor.", "Provides both depth (bathymetry) and acoustic reflectivity (backscatter) data.", "Used for hydrographic surveys, nautical charting, habitat mapping, and offshore construction."]
    },
    {
        "name": "Ground Penetrating Radar (GPR)",
        "description": "A geophysical method that uses radar pulses to image the subsurface. It detects reflected signals from subsurface structures, changes in material, or buried objects.",
        "icon": "🌍",
        "details": ["Transmits high-frequency radio waves into the ground and records the reflected signals.", "Effective for detecting utilities, voids, rebar, archaeological features, and geological strata.", "Non-destructive and can be used on various materials like soil, rock, concrete, and ice."]
    },
    {
        "name": "Ultrasonic Sensors (Air/Short-Range Water)",
        "description": "Utilize high-frequency sound waves (ultrasound) to measure distances, detect objects, or map environments, typically in air or for short-range underwater applications.",
        "icon": "🔊",
        "details": ["Emit ultrasonic pulses and measure the time taken for echoes to return.", "Common in robotics for navigation and obstacle avoidance, parking sensors, level measurement, and non-destructive testing.", "Range and resolution depend on frequency and medium."]
    },
    {
        "name": "AI in Sonar Classification (e.g., with Perplexity AI concepts)", #Updated title
        "description": "Modern sonar systems increasingly leverage Artificial Intelligence (AI) and Machine Learning (ML) for automated target recognition (ATR) and classification from sonar imagery (e.g., spectrograms, side-scan images). Large language models can assist in interpreting reports and data.",
        "icon": "🤖",
        "details": [
            "Deep Learning models, particularly Convolutional Neural Networks (CNNs), have shown significant promise in classifying objects based on their acoustic signatures from images.",
            "Large Language Models (LLMs) like those accessible via Perplexity AI can be used to summarize sonar data reports, answer questions about sonar principles, and assist in drafting analyses of sonar findings when provided with textual data or descriptions.",
            "Techniques are often inspired by computer vision, adapted for the unique characteristics of sonar data (e.g., noise, artifacts, specific textures).",
            "Research, such as 'Deep convolutional neural networks for sonar image classification' (Nature s41598-019-40765-6), demonstrates the application of CNNs for tasks like distinguishing between different types of seabed features or man-made objects from imagery.",
            "Challenges include dataset availability for training visual models, variability in sonar data due to environmental conditions, and the need for robust models. LLMs rely on the quality and detail of the input text or data provided to them."
            ]
    }
]


# --- Helper Functions ---

def clean_markdown(text):
    """Removes specific markdown code block specifiers if they cause issues."""
    text = re.sub(r"```json\n", "```\n", text)
    text = re.sub(r"```python\n", "```\n", text)
    text = re.sub(r"```text\n", "```\n", text)
    text = re.sub(r"```markdown\n", "```\n", text)
    return text

@st.cache_resource
def configure_perplexity_client(api_key):
    """Configures and returns the Perplexity AI client."""
    if not api_key:
        return None
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        # Optionally, you could try a lightweight API call here to verify connectivity,
        # e.g., listing models if supported and doesn't incur costs, but often not necessary.
        print("✅ Perplexity AI client configured for Sonar Analysis Hub.")
        return client
    except Exception as e:
        st.error(f"🚨 **Perplexity AI Error:** Client configuration failed: {e}", icon="🔥")
        print(f"Error configuring Perplexity client: {e}")
        return None

perplexity_client = None # Initialize
if PERPLEXITY_API_KEY:
    perplexity_client = configure_perplexity_client(PERPLEXITY_API_KEY)


@st.cache_data(ttl=600) # Cache for 10 minutes
def get__scan_details(scan_id):
    """Simulates fetching sonar scan information."""
    print(f"Simulating fetching data for Scan ID: {scan_id}")
    time.sleep(0.5) # Simulate network delay
    return _SONAR_DATA.get(scan_id.upper())

@st.cache_data(ttl=300) # Cache for 5 minutes
def run_new_scan_(sonar_type, area_name, primary_frequency, scan_depth_range, custom_notes):
    """Simulates running a new sonar scan and generating basic results, ensuring targets are created."""
    print(f"Simulating new scan for: Type: {sonar_type}, Area: {area_name}")
    time.sleep(0.7) # Simulate processing delay

    scan_id = f"SIM{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    st.session_state.current_sim_type = sonar_type # For spectrogram generator context
    targets = [] # Initialize targets list

    if "Sea" in sonar_type or "SSS" in sonar_type:
        base_type = "Sea (Side-Scan Sonar)"
        spectrogram_data = generate__spectrogram(np.random.choice(["object_strong", "object_faint", "clear", "small_objects_sea"]))
        color_scale = "Viridis"
        params = {"frequency_khz": primary_frequency or 300, "range_m": scan_depth_range or 100, "sim_operator": "AutoSim"}
        # --- Generate 1 to 3 targets for Sea scans ---
        num_targets = np.random.randint(1, 4)
        for i in range(num_targets):
            target_types_sea = ["Potential Wreckage Fragment", "Unknown Anomaly", "Seabed Feature", "Submerged Object"]
            target_type = np.random.choice(target_types_sea)
            range_val = round(np.random.uniform(20, (scan_depth_range or 100) * 0.9), 1)
            size_approx = f"{round(np.random.uniform(0.5, 5),1)}x{round(np.random.uniform(0.5, 3),1)}"
            targets.append({
                "id": f"SIM_TGT_S{i+1:02d}",
                "type": target_type,
                "confidence": round(np.random.uniform(0.55, 0.92), 2),
                "range_m": range_val,
                "size_m_approx": size_approx,
                "details": f"Auto-generated target. Acoustic signature suggests {target_type.lower()} at approx. {range_val}m."
            })

    elif "Land" in sonar_type or "GPR" in sonar_type:
        base_type = "Land (Ground Penetrating Radar - GPR)"
        spectrogram_data = generate__spectrogram(np.random.choice(["layered_gpr", "object_faint", "utility_gpr"]))
        color_scale = "Plasma"
        params = {"frequency_mhz": primary_frequency or 200, "depth_m_max": scan_depth_range or 5, "survey_line": "SIM_L001"}
        # --- Generate 1 to 3 targets for Land scans ---
        num_targets = np.random.randint(1, 4)
        for i in range(num_targets):
            target_types_land = ["Buried Utility Line", "Subsurface Void", "Foundation Remnant", "Geological Layer Change"]
            target_type = np.random.choice(target_types_land)
            depth_val = round(np.random.uniform(0.3, (scan_depth_range or 5) * 0.85), 1)
            targets.append({
                "id": f"SIM_TGT_L{i+1:02d}",
                "type": target_type,
                "confidence": round(np.random.uniform(0.65, 0.88), 2),
                "depth_m_approx": depth_val,
                "material_guess": np.random.choice(["Concrete/Metal", "Soil Disturbance", "Clay/Rock", "Unknown"]),
                "details": f"Auto-generated GPR target. Reflection indicates {target_type.lower()} at ~{depth_val}m depth."
            })

    elif "Air" in sonar_type or "Ultrasonic" in sonar_type:
        base_type = "Air (Ultrasonic Array Sensor)"
        spectrogram_data = generate__spectrogram(np.random.choice(["object_faint", "cluttered_air"]))
        color_scale = "Cividis"
        params = {"frequency_khz": primary_frequency or 40, "max_range_m": scan_depth_range or 8, "scan_angle_deg": 90}
        # --- Generate 1 to 2 targets for Air scans ---
        num_targets = np.random.randint(1, 3)
        for i in range(num_targets):
            target_types_air = ["Nearby Obstacle", "Reflective Surface", "Moving Object Signature"]
            target_type = np.random.choice(target_types_air)
            distance_val = round(np.random.uniform(0.5, (scan_depth_range or 8) * 0.9), 1)
            targets.append({
                "id": f"SIM_TGT_A{i+1:02d}",
                "type": target_type,
                "confidence": round(np.random.uniform(0.75, 0.99), 2),
                "distance_m": distance_val,
                "details": f"Auto-generated airborne target. Echo suggests {target_type.lower()} at {distance_val}m."
            })
    else:
        base_type = "Generic Sonar"
        spectrogram_data = generate__spectrogram("clear")
        color_scale = "Gray"
        params = {"frequency_generic": primary_frequency or 100, "range_generic": scan_depth_range or 50}
        # --- Default target for Generic if others fail ---
        targets.append({
            "id": "SIM_TGT_GEN01",
            "type": "Generic Anomaly",
            "confidence": round(np.random.uniform(0.5, 0.8), 2),
            "range_generic": round(np.random.uniform(10, (scan_depth_range or 50) * 0.8), 1),
            "details": "Auto-generated generic target."
        })

    if "current_sim_type" in st.session_state:
        del st.session_state.current_sim_type # Clean up

    return {
        "scan_id": scan_id,
        "sonar_type": base_type,
        "timestamp": timestamp,
        "location_": area_name or "Simulated Area", 
        "parameters": params,
        "spectrogram_data": spectrogram_data,
        "color_scale": color_scale,
        "detected_targets": targets, 
        "summary": f"Simulated scan {scan_id} completed for {area_name}. Found {len(targets)} potential target(s). Notes: {custom_notes}" if custom_notes else f"Simulated scan {scan_id} completed for {area_name}. Found {len(targets)} potential target(s).",
        "notes_user": custom_notes
    }
    
def prepare_data_for_json_export(scan_data_dict):
    """Prepares scan data for JSON export, removing or converting large arrays."""
    serializable_data = scan_data_dict.copy()
    if 'spectrogram_data' in serializable_data and isinstance(serializable_data['spectrogram_data'], np.ndarray):
        serializable_data['spectrogram_data_shape'] = str(serializable_data['spectrogram_data'].shape) 
        del serializable_data['spectrogram_data']
    for key, value in serializable_data.items():
        if isinstance(value, (np.int64, np.int32, np.float64, np.float32)):
            serializable_data[key] = value.item() 
        elif isinstance(value, list): 
            serializable_data[key] = [v.item() if isinstance(v, (np.int64, np.int32, np.float64, np.float32)) else v for v in value]
    return serializable_data


def display__result_block(scan_result_data, context_key_suffix=""):
    """Displays the details, spectrogram, and targets for a given scan result."""
    st.markdown(f"<div class='scan-result-container'>", unsafe_allow_html=True)
    if not isinstance(scan_result_data, dict):
        st.error(f"Error: Expected a dictionary for scan_result_data, but got {type(scan_result_data)}.", icon="❌")
        st.markdown(f"</div>", unsafe_allow_html=True)
        return

    scan_id = scan_result_data.get('scan_id', 'N/A')
    sonar_type = scan_result_data.get('sonar_type', 'N/A')
    st.subheader(f"Results for Scan: {scan_id} ({sonar_type})")

    sim_meta_col1, sim_meta_col2 = st.columns(2)
    with sim_meta_col1:
        timestamp = scan_result_data.get('timestamp', 'N/A')
        st.markdown(f"**Timestamp:** {timestamp}")
        location = scan_result_data.get('location_', 'N/A - Key Missing!')
        st.markdown(f"**Location (Simulated):** {location}")
        if location == 'N/A - Key Missing!':
            st.warning("Debug: The key 'location_' was missing from the scan data.", icon="⚠️")

    with sim_meta_col2:
        st.markdown(f"**Parameters:**")
        parameters = scan_result_data.get('parameters', {})
        if parameters:
            st.json(parameters, expanded=False)
        else:
            st.markdown("N/A")
            if 'parameters' not in scan_result_data:
                 st.warning("Debug: The key 'parameters' was missing from the scan data.", icon="⚠️")

    summary = scan_result_data.get('summary', 'N/A')
    st.markdown(f"**Scan Summary:** {summary}")
    if 'summary' not in scan_result_data and summary == 'N/A':
         st.warning("Debug: The key 'summary' was missing from the scan data.", icon="⚠️")

    notes_user = scan_result_data.get('notes_user')
    if notes_user: 
        st.markdown(f"**User Notes:** {notes_user}")

    try:
        if all(k in scan_result_data for k in ['scan_id', 'timestamp']): 
            sim_data_for_json = prepare_data_for_json_export(scan_result_data.copy()) 
            json_export_sim_data = json.dumps(sim_data_for_json, indent=4)
            st.download_button(
                label="📥 Download Scan Data (JSON)",
                data=json_export_sim_data,
                file_name=f"{scan_id}_export.json", 
                mime="application/json",
                key=f"download_sim_{scan_id}_{context_key_suffix}"
            )
        else:
            st.error("Cannot generate download link: Essential data missing from scan result.", icon="⚠️")
    except Exception as e_json_sim:
        st.error(f"Error preparing  data for download: {e_json_sim}")

    st.markdown("---")

    st.subheader("Simulated Sonar Image / Spectrogram")
    spectrogram_data = scan_result_data.get("spectrogram_data")
    if spectrogram_data is not None and isinstance(spectrogram_data, np.ndarray):
        try:
            fig_sim_spec = px.imshow(spectrogram_data,
                                     color_continuous_scale=scan_result_data.get("color_scale", "Viridis"),
                                     aspect="auto",
                                     labels=dict(x="Range/Time Bins", y="Beam/Depth Bins", color="Intensity"))
            fig_sim_spec.update_layout(
                title_text=f"Visualisation for {scan_id}",
                plot_bgcolor='#2a2a2e', paper_bgcolor='#2a2a2e',
                font_color='#E0E0E0',
                coloraxis_colorbar_title_font_color='#E0E0E0',
                coloraxis_colorbar_tickfont_color='#E0E0E0'
            )
            st.plotly_chart(fig_sim_spec, use_container_width=True)
        except Exception as e_plot_sim:
            st.error(f"Could not plot spectrogram for : {e_plot_sim}")
    else:
        st.info("No spectrogram data generated or data not in expected format for this .")
        if 'spectrogram_data' not in scan_result_data:
            st.warning("Debug: The key 'spectrogram_data' was missing from the scan data.", icon="⚠️")

    st.markdown("---")
    st.subheader("Simulated Detected Targets")
    detected_targets = scan_result_data.get("detected_targets")
    if detected_targets: 
        sim_targets_df = pd.DataFrame(detected_targets)
        st.dataframe(sim_targets_df, use_container_width=True)
    else:
        st.info("No specific targets generated for this .")
        if 'detected_targets' not in scan_result_data and not detected_targets == []: 
             st.warning("Debug: The key 'detected_targets' was missing from the scan data.", icon="⚠️")

    st.markdown(f"</div>", unsafe_allow_html=True)
# --- END OF Helper Functions ---

# --- Streamlit App Layout ---
st.markdown("<h1 class='main-title'>Sonar Analysis Hub 📡</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Explore sonar data, upload your own for AI analysis, and get Perplexity AI insights.</p>", unsafe_allow_html=True)

if "last_uploaded_image" not in st.session_state:
    st.session_state.last_uploaded_image = None
if "last_uploaded_data_file" not in st.session_state:
    st.session_state.last_uploaded_data_file = None

# --- Sidebar ---
with st.sidebar:
    st.image("https://i.imgur.com/sQju3dP.jpeg", width=150, caption="SonarTech s Inc.")
    st.markdown("<h2 class='sidebar-title'>Navigation</h2>", unsafe_allow_html=True)

    st.markdown("### Analysis Tools")
    if 'active_tab_key' not in st.session_state:
        st.session_state.active_tab_key = "🏠 Dashboard"

    if st.button("🛰️ Explore Scan Data", key="sidebar_explore", use_container_width=True):
        st.session_state.active_tab_key = "🛰️ Explore Scan Data"
    if st.button("💡 Simulate New Scan", key="sidebar_simulate", use_container_width=True):
        st.session_state.active_tab_key = "💡 Simulate New Scan"
    if st.button("⬆️ Upload & Analyze Sonar Data", key="sidebar_upload", use_container_width=True):
        st.session_state.active_tab_key = "⬆️ Upload & Analyze Sonar Data"

    st.markdown("---")
    with st.expander("📚 Resources & Links", expanded=False):
        st.markdown("- [Nature: Acoustic Classification (s41598-019-40765-6)](https://www.nature.com/articles/s41598-019-40765-6)")
        st.markdown("- [Ocean Exploration Trust: Sonar](https://nautiluslive.org/tech/sonar)")
        st.markdown("- [USGS: GPR Info](https://www.usgs.gov/node/277760)")
        st.markdown("- [Perplexity AI (Docs)](https://docs.perplexity.ai/home)")

    st.markdown("---")
    st.markdown("<h3 class='ai-assistant-title'>🤖 AI Sonar Assistant</h3>", unsafe_allow_html=True)

    if not perplexity_client: 
        st.warning("AI Assistant offline. Configure Perplexity API Key in secrets.", icon="🔌")
    else:
        if "sonar_messages" not in st.session_state:
            st.session_state.sonar_messages = [
                {"role": "assistant", "content": "Hello! I'm the Sonar AI Assistant. Explore the hub or ask me about sonar. If you upload a file in the 'Upload' tab, you can ask me about it here (e.g., 'analyze the uploaded image' or 'what about the CSV file I uploaded?')."}
            ]

        MAX_CHAT_HISTORY_DISPLAY = 30
        chat_display_container = st.container()
        chat_display_container.markdown('<div style="max-height: 300px; overflow-y: auto; padding-right: 10px; margin-bottom: 10px; border: 1px solid #444; border-radius: 5px; background-color: rgba(30,30,33,0.9);">', unsafe_allow_html=True)
        with chat_display_container:
            for msg_idx, msg in enumerate(st.session_state.sonar_messages[-MAX_CHAT_HISTORY_DISPLAY:]):
                with st.chat_message(msg["role"], avatar= "🧑‍💻" if msg["role"]=="user" else "📡"):
                    st.markdown(clean_markdown(str(msg.get("content",""))), unsafe_allow_html=False) # Ensure content is string
        chat_display_container.markdown('</div>', unsafe_allow_html=True)
        
        chat_input_disabled = not perplexity_client
        if chat_input_disabled and PERPLEXITY_API_KEY: # Only show if key was provided but client failed
             st.caption("AI chat initialization failed. Please check console logs or API key.")

        if prompt := st.chat_input("Ask about sonar...", key="sonar_perplexity_prompt", disabled=chat_input_disabled):
            st.session_state.sonar_messages.append({"role": "user", "content": prompt})
            
            user_prompt_content_for_api = prompt 
            uploaded_context_sent_to_api = False # Flag to track if context was added

            # Handle uploaded data file context (CSV/TXT)
            if st.session_state.last_uploaded_data_file and \
               any(keyword in prompt.lower() for keyword in ["data", "csv", "text", "file", st.session_state.last_uploaded_data_file["name"].lower()]):
                data_context_str = f"\n\n--- Context from uploaded file: {st.session_state.last_uploaded_data_file['name']} ---\n{st.session_state.last_uploaded_data_file['content_preview']}\n--- End of context ---"
                user_prompt_content_for_api += data_context_str
                st.toast(f"💡 Sending content from '{st.session_state.last_uploaded_data_file['name']}' to AI.", icon="📄")
                st.session_state.last_uploaded_data_file = None # Clear after use
                uploaded_context_sent_to_api = True
            
            # Handle image context (by name/reference, not sending image data)
            elif st.session_state.last_uploaded_image and \
                 any(keyword in prompt.lower() for keyword in ["image", "picture", "photo", "visual", st.session_state.last_uploaded_image["name"].lower()]):
                # No image data is sent. System prompt guides AI to expect user references.
                st.toast(f"🗣️ AI will consider your query in context of the uploaded image: '{st.session_state.last_uploaded_image['name']}'.", icon="🖼️")
                # user_prompt_content_for_api += f" (User is referring to an uploaded image: {st.session_state.last_uploaded_image['name']})" # Optional clarification
                st.session_state.last_uploaded_image = None # Clear after this query attempts to use it.
                uploaded_context_sent_to_api = True # Still flag that context was relevant


            if perplexity_client:
                try:
                    with st.spinner("AI is thinking..."):
                        # Construct messages for Perplexity API
                        api_messages = [{"role": "system", "content": SONAR_SYSTEM_INSTRUCTION}]
                        for msg_data in st.session_state.sonar_messages: # Add history
                            if msg_data["role"] in ["user", "assistant"]: # Ensure roles are correct
                                api_messages.append({"role": msg_data["role"], "content": str(msg_data.get("content", ""))})
                        # The last user message (current prompt with context) is already in sonar_messages,
                        # so no need to append user_prompt_content_for_api separately if sonar_messages is used directly.
                        # However, to ensure the *very latest* prompt (with potential context modifications not yet in sonar_messages)
                        # is the one being sent as the current user turn, we can build it carefully:
                        
                        # Create a temporary list for the API call, including the last user message with context
                        current_call_messages = [{"role": "system", "content": SONAR_SYSTEM_INSTRUCTION}]
                        # Add all but the last message from session_state (which is the raw prompt)
                        for msg_data in st.session_state.sonar_messages[:-1]:
                             if msg_data["role"] in ["user", "assistant"]:
                                current_call_messages.append({"role": msg_data["role"], "content": str(msg_data.get("content", ""))})
                        # Add the current user prompt with any appended context
                        current_call_messages.append({"role": "user", "content": user_prompt_content_for_api})


                        response = perplexity_client.chat.completions.create(
                            model="sonar-pro", # Or "sonar-medium-online", "sonar-small-online"
                            messages=current_call_messages,
                            temperature=0.7, # Perplexity default, or adjust (e.g. 0.5)
                            # top_p=0.9 # Optional
                        )
                        
                        ai_response_content = "⚠️ Response generation issue."
                        if response.choices and response.choices[0].message and response.choices[0].message.content:
                            raw_txt = response.choices[0].message.content
                            cleaned_txt = clean_markdown(raw_txt)
                            finish_reason = response.choices[0].finish_reason
                            if finish_reason and finish_reason != "stop":
                                 cleaned_txt += f"\n\n*(Note: Response may have been truncated. Finish reason: {finish_reason})*"
                        else:
                            cleaned_txt = "⚠️ No valid response content received from AI."
                            print(f"Perplexity AI response issue: {response}")
                    
                    st.session_state.sonar_messages.append({"role": "assistant", "content": cleaned_txt})
                    if uploaded_context_sent_to_api: # If context was sent or referred to
                        st.session_state.sonar_messages.append({"role": "assistant", "content": "(Context from the uploaded file/image reference has now been cleared for the next query. To re-analyze, please upload or refer to it again if needed.)"})

                except Exception as e_ai:
                    error_msg_ai = str(e_ai)
                    st.error(f"Sorry, an AI Assistant Error occurred: {error_msg_ai[:150]}...", icon="🔥")
                    print(f"Error during Perplexity AI interaction: {e_ai}")
                    st.session_state.sonar_messages.append({"role": "assistant", "content": f"Sorry, an error occurred with the AI: {error_msg_ai}. Please try again."})
                st.rerun()
            else:
                st.warning("AI Assistant client not available. Cannot send message.", icon="⚙️")
                st.rerun()

        if st.button("Clear Chat History", key="clear_sonar_chat", use_container_width=True, type="secondary"):
            initial_assistant_message = "Chat history cleared. How can I help you?"
            st.session_state.sonar_messages = [{"role": "assistant", "content": initial_assistant_message}]
            st.session_state.last_uploaded_image = None
            st.session_state.last_uploaded_data_file = None
            print("Chat history and uploaded file context cleared.")
            st.rerun()

    st.markdown("---")
    st.caption(f"© {datetime.now().year} SonarTech s Inc.")

# --- Main Content Tabs ---
tab_names = ["🏠 Dashboard", "🛰️ Explore Scan Data", "💡 Simulate New Scan", "⬆️ Upload & Analyze Sonar Data", "🛠️ Sonar Technologies", "📞 Contact"]

try:
    default_tab_index = tab_names.index(st.session_state.get('active_tab_key', tab_names[0]))
except ValueError:
    default_tab_index = 0 

tabs = st.tabs(tab_names) 

# --- Tab: Dashboard ---
with tabs[0]: 
    st.header("Welcome to the Sonar Analysis Hub!")
    st.markdown("<p class='tab-description'>Your interface for exploring sonar data, uploading your own for AI analysis, understanding detection principles, and learning about various sonar technologies.</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    st.subheader("Explore Sonar Capabilities")
    st.markdown("""
    This hub provides tools and information for understanding sonar applications:
    - **Sea Sonar:** Simulate Side-Scan Sonar data for seabed imaging and wreck detection.
    - **Land Sonar (GPR):** Explore Ground Penetrating Radar data for subsurface investigation.
    - **Air Sonar (Ultrasonic):** Analyze ultrasonic sensor data for obstacle avoidance and mapping.
    - **Upload Your Data:** Upload your own sonar images or basic data files. The AI Assistant can then discuss them based on your prompts.

    **Navigate using the tabs above or sidebar buttons to:**
    - **Explore Scan Data:** Load and visualize pre-defined sonar scans.
    - **Simulate New Scan:** Generate new sonar data based on your input parameters.
    - **Upload & Analyze Sonar Data:** Upload your sonar images/data and use the sidebar AI to discuss them.
    - **Sonar Technologies:** Learn about different sonar systems and AI applications.
    - **Perplexity AI Sonar Assistant:** Use the AI in the sidebar for questions and analysis of uploaded content!
    """)

    st.markdown("---")
    st.subheader(" Data Overview")
    col1, col2, col3 = st.columns(3)
    current_sea_scans = len([s for s_id, s in _SONAR_DATA.items() if "Sea" in s["sonar_type"]])
    current_land_scans = len([s for s_id, s in _SONAR_DATA.items() if "Land" in s["sonar_type"]])
    current_air_scans = len([s for s_id, s in _SONAR_DATA.items() if "Air" in s["sonar_type"]])
    
    col1.metric(" Sea Scans", f"{current_sea_scans}", "Side-Scan & MBES Concepts")
    col2.metric(" Land Scans (GPR)", f"{current_land_scans}", "Subsurface Imaging")
    col3.metric(" Air Scans (Ultrasonic)", f"{current_air_scans}", "Ranging & Detection")
    
    if st.checkbox("Show Sonar Types Distribution Chart", True, key="dash_chart_toggle"):
        sonar_types_counts = {
            "Sea": current_sea_scans,
            "Land (GPR)": current_land_scans,
            "Air (Ultrasonic)": current_air_scans
        }
        df_types = pd.DataFrame(list(sonar_types_counts.items()), columns=['Sonar Type', 'Number of Scans'])
        
        fig = px.bar(df_types, x="Sonar Type", y="Number of Scans", 
                     title="Distribution of Scan Types",
                     color="Sonar Type", color_discrete_map={
                         "Sea": "#00AEEF", "Land (GPR)": "#FFA500", "Air (Ultrasonic)": "#33CC33"
                     },
                     template="plotly_dark")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            title_font_color='#E0E0E0', font_color='#C0C0C0'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab: Explore Scan Data ---
with tabs[1]: 
    st.header("Explore Existing Sonar Scan Data")
    st.markdown("<p class='tab-description'>Select a Scan ID to view its details, spectrogram/radargram, and detected targets. You can also download the scan data.</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    available_scan_ids = list(_SONAR_DATA.keys()) 
    scan_id_input = st.selectbox("Select Scan ID:", options=available_scan_ids, index=0, key="scan_id_explore",
                                 help="Choose from pre-loaded or newly simulated scans available in this session.")

    if st.button("Load Scan Data", key="load_scan_btn", use_container_width=True):
        if scan_id_input:
            with st.spinner(f"Loading data for scan: {scan_id_input}..."):
                scan_data = get__scan_details(scan_id_input) 

            if scan_data:
                st.session_state.current_loaded_scan_id = scan_id_input 
                st.markdown(f"<div class='scan-result-container'>", unsafe_allow_html=True)
                st.subheader(f"Scan Details: {scan_data['scan_id']} ({scan_data['sonar_type']})")
                
                meta_col1, meta_col2 = st.columns(2)
                with meta_col1:
                    st.markdown(f"**Timestamp:** {scan_data['timestamp']}")
                    st.markdown(f"**Location:** {scan_data['location_']}")
                with meta_col2:
                    st.markdown(f"**Parameters:**")
                    st.json(scan_data['parameters'], expanded=False)
                
                st.markdown(f"**Scan Summary:** {scan_data.get('summary', 'N/A')}")

                try:
                    scan_data_for_json = prepare_data_for_json_export(scan_data)
                    json_export_data = json.dumps(scan_data_for_json, indent=4)
                    st.download_button(
                        label="📥 Download Scan Data (JSON)",
                        data=json_export_data,
                        file_name=f"{scan_data['scan_id']}_export.json",
                        mime="application/json",
                        key=f"download_{scan_data['scan_id']}"
                    )
                except Exception as e_json:
                    st.error(f"Error preparing data for download: {e_json}")

                st.markdown("---")

                st.subheader("Sonar Image / Spectrogram / Radargram")
                if scan_data.get("spectrogram_data") is not None and isinstance(scan_data["spectrogram_data"], np.ndarray):
                    try:
                        fig_spec = px.imshow(scan_data["spectrogram_data"],
                                             color_continuous_scale=scan_data.get("color_scale", "Viridis"),
                                             aspect="auto",
                                             labels=dict(x="Range/Time Bins", y="Beam/Depth Bins", color="Intensity"))
                        fig_spec.update_layout(
                            title_text=f"Visualisation for {scan_data['scan_id']}",
                            plot_bgcolor='#2a2a2e', paper_bgcolor='#2a2a2e', 
                            font_color='#E0E0E0',
                            coloraxis_colorbar_title_font_color='#E0E0E0',
                            coloraxis_colorbar_tickfont_color='#E0E0E0'
                        )
                        st.plotly_chart(fig_spec, use_container_width=True)
                    except Exception as e_plot:
                        st.error(f"Could not plot spectrogram: {e_plot}")
                else:
                    st.info("No spectrogram data available or data is not in expected format for this scan.")

                st.markdown("---")
                st.subheader("Detected Targets (Classification)")
                if scan_data.get("detected_targets"):
                    targets_df = pd.DataFrame(scan_data["detected_targets"])
                    st.dataframe(targets_df, use_container_width=True)
                else:
                    st.info("No specific targets detected or listed for this scan.")
                st.markdown(f"</div>", unsafe_allow_html=True) 
            else:
                st.error(f"Scan ID '{scan_id_input}' not found. Please select a valid ID.", icon="❌")
        else:
            st.warning("Please select a Scan ID.", icon="⚠️")
    
    elif 'current_loaded_scan_id' in st.session_state and st.session_state.current_loaded_scan_id == scan_id_input:
        scan_data = get__scan_details(st.session_state.current_loaded_scan_id)
        if scan_data: 
            st.markdown(f"<div class='scan-result-container'>", unsafe_allow_html=True)
            st.subheader(f"Scan Details: {scan_data['scan_id']} ({scan_data['sonar_type']})")
            meta_col1, meta_col2 = st.columns(2)
            with meta_col1:
                st.markdown(f"**Timestamp:** {scan_data['timestamp']}")
                st.markdown(f"**Location:** {scan_data['location_']}")
            with meta_col2:
                st.markdown(f"**Parameters:**"); st.json(scan_data['parameters'], expanded=False)
            st.markdown(f"**Scan Summary:** {scan_data.get('summary', 'N/A')}")
            try:
                scan_data_for_json = prepare_data_for_json_export(scan_data)
                json_export_data = json.dumps(scan_data_for_json, indent=4)
                st.download_button(label="📥 Download Scan Data (JSON)",data=json_export_data,file_name=f"{scan_data['scan_id']}_export.json",mime="application/json",key=f"download_{scan_data['scan_id']}_rerun")
            except Exception as e_json: st.error(f"Error preparing data for download: {e_json}")
            st.markdown("---")
            st.subheader("Sonar Image / Spectrogram / Radargram")
            if scan_data.get("spectrogram_data") is not None and isinstance(scan_data["spectrogram_data"], np.ndarray):
                try:
                    fig_spec = px.imshow(scan_data["spectrogram_data"],color_continuous_scale=scan_data.get("color_scale", "Viridis"),aspect="auto",labels=dict(x="Range/Time Bins", y="Beam/Depth Bins", color="Intensity"))
                    fig_spec.update_layout(title_text=f"Visualisation for {scan_data['scan_id']}",plot_bgcolor='#2a2a2e', paper_bgcolor='#2a2a2e',font_color='#E0E0E0',coloraxis_colorbar_title_font_color='#E0E0E0',coloraxis_colorbar_tickfont_color='#E0E0E0')
                    st.plotly_chart(fig_spec, use_container_width=True)
                except Exception as e_plot: st.error(f"Could not plot spectrogram: {e_plot}")
            else: st.info("No spectrogram data.")
            st.markdown("---")
            st.subheader("Detected Targets ( Classification)")
            if scan_data.get("detected_targets"): st.dataframe(pd.DataFrame(scan_data["detected_targets"]), use_container_width=True)
            else: st.info("No specific targets.")
            st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Example Scan IDs available:")
    st.code("\n".join(available_scan_ids))

    st.markdown('</div>', unsafe_allow_html=True) 

# --- Tab: Simulate New Scan ---
with tabs[2]:
    st.header("Simulate a New Sonar Scan")
    st.markdown("<p class='tab-description'>Configure parameters to generate a new sonar scan. Results can be added to the 'Explore Scan Data' list for this session and downloaded.</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    with st.form("new_scan_form"):
        st.subheader("Scan Configuration")
        sim_sonar_type = st.selectbox("Sonar Type for Simulation*",
                                      options=["Sea (Side-Scan Sonar type)", "Land (GPR type)", "Air (Ultrasonic type)", "Generic Sonar "],
                                      help="Select the type of sonar environment to simulate.")
        sim_area_name = st.text_input("Simulated Area Name/Identifier *", placeholder="e.g., Test Site Alpha, Seabed Sector X")

        col_param1, col_param2 = st.columns(2)
        with col_param1:
            sim_frequency = st.number_input("Primary Frequency (kHz/MHz)", min_value=10, value=100, step=10,
                                            help="E.g., 40 (Air), 250 (GPR), 400 (SSS). Unit depends on type.")
        with col_param2:
            sim_range_depth = st.number_input("Max Scan Range/Depth (meters)", min_value=1, value=50, step=5,
                                              help="Effective range or depth for the simulation.")

        sim_custom_notes = st.text_area("Custom Notes for Simulation", placeholder="e.g., Testing for small object detection, high clutter environment.")

        submitted_ = st.form_submit_button("Run New Simulation", use_container_width=True)

    if submitted_:
        if not all([sim_sonar_type, sim_area_name]):
            st.error("Please fill in all required fields marked with *.", icon="❗")
        else:
            with st.spinner("Simulating new scan..."):
                _scan_result = run_new_scan_( 
                    sim_sonar_type,
                    sim_area_name,
                    sim_frequency,
                    sim_range_depth,
                    sim_custom_notes
                )
            st.success(f"New scan simulation {_scan_result['scan_id']} completed!", icon="✅")
            st.session_state.last__scan_result = _scan_result 

            display__result_block(_scan_result, context_key_suffix="new")

            add_to_explore_key = f"add_sim_{_scan_result['scan_id']}_on_creation"
            if st.checkbox("Add this simulation to 'Explore Scan Data' list for this session?", True, key=add_to_explore_key):
                if _scan_result['scan_id'] not in _SONAR_DATA:
                    _SONAR_DATA[_scan_result['scan_id']] = _scan_result
                    st.info(f"Scan {_scan_result['scan_id']} is now available in the 'Explore Scan Data' tab.", icon="ℹ️")
            elif _scan_result['scan_id'] in _SONAR_DATA:
                 del _SONAR_DATA[_scan_result['scan_id']]
                 st.info(f"Scan {_scan_result['scan_id']} was not added to 'Explore Scan Data'.", icon="ℹ️")

    elif 'last__scan_result' in st.session_state and st.session_state.last__scan_result:
        _scan_result = st.session_state.last__scan_result 
        st.info(f"Displaying previously simulated scan: {_scan_result['scan_id']}", icon="🔄")

        display__result_block(_scan_result, context_key_suffix="old")

        manage_explore_key = f"manage_sim_{_scan_result['scan_id']}_in_explore"
        is_currently_in_explore_list = _scan_result['scan_id'] in _SONAR_DATA

        should_be_in_explore_list = st.checkbox(
            "Keep this simulation in 'Explore Scan Data' list?",
            value=is_currently_in_explore_list,
            key=manage_explore_key
        )

        if should_be_in_explore_list and not is_currently_in_explore_list:
            _SONAR_DATA[_scan_result['scan_id']] = _scan_result
            st.info(f"Scan {_scan_result['scan_id']} has been re-added to the 'Explore Scan Data' tab.", icon="ℹ️")
        elif not should_be_in_explore_list and is_currently_in_explore_list:
            del _SONAR_DATA[_scan_result['scan_id']]
            st.info(f"Scan {_scan_result['scan_id']} has been removed from the 'Explore Scan Data' tab.", icon="ℹ️")

    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab: Upload & Analyze Sonar Data ---
with tabs[3]:
    st.header("⬆️ Upload & Analyze Sonar Data")
    st.markdown("<p class='tab-description'>Upload your sonar images (PNG, JPG) or data files (CSV, TXT). Then, use the sidebar AI Assistant to ask questions about the uploaded content (e.g., 'Analyze the uploaded image' or 'Tell me about the data file I uploaded called X.csv').</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    st.subheader("Upload Sonar Image")
    uploaded_image_file = st.file_uploader("Choose an image file (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="sonar_image_upload")

    if uploaded_image_file is not None:
        try:
            image = Image.open(uploaded_image_file)
            st.image(image, caption=f"Uploaded Image: {uploaded_image_file.name}", use_column_width=True)
            st.session_state.last_uploaded_image = {"name": uploaded_image_file.name, "image_obj": image} # image_obj stored for display, not sent to AI
            st.session_state.last_uploaded_data_file = None 
            st.success(f"Image '{uploaded_image_file.name}' loaded. You can now ask the AI Assistant in the sidebar to discuss it.", icon="🖼️")
            st.info(f"Example prompt for AI: \"What might typical features in a sonar image like '{uploaded_image_file.name}' represent?\" or \"Discuss the uploaded image named {uploaded_image_file.name}\".", icon="💡")
        except Exception as e_img:
            st.error(f"Error processing image: {e_img}")
            st.session_state.last_uploaded_image = None

    st.markdown("---")
    st.subheader("Upload Sonar Data File")
    uploaded_data_file = st.file_uploader("Choose a data file (CSV, TXT)", type=["csv", "txt"], key="sonar_data_upload")

    if uploaded_data_file is not None:
        st.markdown(f"<div class='scan-result-container'>", unsafe_allow_html=True) 
        st.subheader(f"Preview of: {uploaded_data_file.name}")
        content_preview_for_ai = None
        try:
            if uploaded_data_file.type == "text/csv":
                df = pd.read_csv(uploaded_data_file)
                st.dataframe(df.head(10)) 
                if len(df) > 10: st.caption(f"Showing first 10 rows of {len(df)} total rows.")
                content_preview_for_ai = df.head(20).to_string() 
            elif uploaded_data_file.type == "text/plain":
                stringio = io.StringIO(uploaded_data_file.getvalue().decode("utf-8"))
                text_content = stringio.read()
                st.text_area("File Content (first 1000 chars):", text_content[:1000], height=200)
                content_preview_for_ai = text_content[:2000] 
            
            st.session_state.last_uploaded_data_file = {"name": uploaded_data_file.name, "content_preview": content_preview_for_ai}
            st.session_state.last_uploaded_image = None 
            st.success(f"File '{uploaded_data_file.name}' loaded. You can now ask the AI Assistant in the sidebar to analyze its content.", icon="📄")
            st.info(f"Example prompt for AI: \"Summarize the uploaded data file.\" or \"What patterns do you see in {uploaded_data_file.name}?\"", icon="💡")

        except Exception as e_data:
            st.error(f"Error processing data file: {e_data}")
            st.session_state.last_uploaded_data_file = None
        st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.last_uploaded_image:
        st.write(f"🗣️ **Ready for AI:** Image '{st.session_state.last_uploaded_image['name']}' is active for discussion via sidebar chat.")
    if st.session_state.last_uploaded_data_file:
        st.write(f"🗣️ **Ready for AI:** Data file '{st.session_state.last_uploaded_data_file['name']}' (text preview) is active for AI analysis via sidebar chat.")
    
    st.info("Note: Uploaded files are processed in memory for this session. For images, the AI will discuss based on your textual prompts and its name. For data files, a text preview is sent to the AI when you ask about it. Context is cleared after one analysis query.", icon="ℹ️")
    st.markdown('</div>', unsafe_allow_html=True) 

# --- Tab: Sonar Technologies ---
with tabs[4]:
    st.header("Understanding Sonar Technologies")
    st.markdown("<p class='tab-description'>Learn about different types of sonar, their principles, applications, and the role of AI in modern sonar analysis.</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    if not SONAR_TECHNOLOGIES_INFO:
        st.info("Sonar technology information is currently unavailable. Please check back later.")
    else:
        for tech in SONAR_TECHNOLOGIES_INFO:
            st.markdown(f"<div class='tech-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3>{tech['icon']} {tech['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{tech['description']}</p>", unsafe_allow_html=True)
            if tech.get("details"):
                st.markdown("<strong>Key characteristics & applications:</strong>", unsafe_allow_html=True)
                for detail in tech['details']:
                    st.markdown(f"- {detail}")
            st.markdown(f"</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) 

# --- Tab: Contact Us (Placeholder) ---
with tabs[5]:
    st.header("Contact Us")
    st.markdown("<p class='tab-description'>This section is a placeholder for contact information.</p>", unsafe_allow_html=True)
    st.markdown('<div class="scrollable-tab-content">', unsafe_allow_html=True)

    st.info("This is a demonstration application. For real sonar inquiries, please consult with relevant industry experts or organizations.")
    
    st.subheader(" Contact Form")
    with st.form("contact_form_sonar"):
        contact_name = st.text_input("Your Name")
        contact_email = st.text_input("Your Email")
        contact_subject = st.text_input("Subject")
        contact_message = st.text_area("Your Message", height=100)
        contact_submitted = st.form_submit_button("Send Message ()")

        if contact_submitted:
            if contact_name and contact_email and contact_message:
                st.success(f"Thank you, {contact_name}! Your message '{contact_subject}' has been 'received' ().")
            else:
                st.error("Please fill in all fields.")
    
    st.markdown('</div>', unsafe_allow_html=True) 

# --- Footer ---
st.markdown("---") 
st.markdown(f"<p style='text-align:center; font-size: 0.9em; color: #A0A0A0; padding: 10px 0;'>© {datetime.now().year} SonarTech s Inc. - For Educational & Demonstrative Purposes.</p>", unsafe_allow_html=True)

print(f"Sonar Analysis Hub Streamlit app script (Perplexity AI version) finished loading at {datetime.now()}. Active tab hint: {st.session_state.get('active_tab_key')}")
