import streamlit as st

# --- Authentication Check ---
# Stop the page from loading if the user is not logged in
if not st.session_state.get("logged_in"):
    st.error("Please log in from the 🏠 Home page to use this feature.")
    st.stop()

# Block admin access to student features
if st.session_state.get("role") == "admin":
    st.error("Access Denied: This feature is for students only. Admins cannot access student features.")
    st.stop()

# --- YOUR ORIGINAL CODE STARTS BELOW ---
# app.py
import streamlit as st
import sounddevice as sd
import sqlite3
import pandas as pd
import io
import os
import wave
from dotenv import load_dotenv
from openai import OpenAI
# speech_recognition imported but not used - removed

# ---------------------------
# Load environment and init
# ---------------------------
load_dotenv()
db_path = "data.db"

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------
# Helper: Load local DB
# ---------------------------
@st.cache_data(show_spinner=False)
def load_db_to_context(db_path=db_path):
    if not os.path.exists(db_path):
        st.error("Database file not found! Please ensure 'data.db' exists in the project folder.")
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM companies", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading database: {e}")
        return pd.DataFrame()

# ---------------------------
# Helper: Voice Input
# ---------------------------

def get_voice_input(duration=10, samplerate=16000):
    """Record short audio and transcribe it quickly using OpenAI Whisper."""
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
    wav_io.seek(0)

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=("voice.wav", wav_io)
    )

    return transcription.text.strip()
# ---------------------------
# Helper: Query LLM
# ---------------------------
def query_llm(user_query, df):
    if df.empty:
        return "⚠️ Database is empty or not loaded correctly."

    table_text = df.to_csv(index=False)

    system_prompt = f"""
You are CDC Assistant, an intelligent placement query engine for VIT students.
You are given the placement database below (in CSV format).
Use it to answer user queries accurately and concisely.
Always show the final answer in a clean, readable format (Markdown tables or bullet points).
Do not hallucinate — only use information from the database.

--- Placement Database (CSV) ---
{table_text}
--------------------------------

--- Database Schema ---
Company: Name of the recruiting company.
Month: The month during which the company visited the campus.
Average_CTC_LPA: The average salary package (in LPA) offered by the company.
BBS: No. of CSE (Business Systems) students placed.
BCE: No. of CSE (Core) students placed.
BCI: No. of CSE (Information Security) students placed.
BCT: No. of CSE (IoT) students placed.
BDS: No. of CSE (Data Science) students placed.
BEC: No. of Electronics Engineering students placed.
BEE: No. of Electrical Engineering students placed.
BIT: No. of Information Technology students placed.
BKT: No. of CSE (Blockchain Technology) students placed.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying model: {e}"



# Custom CSS for a clean UI
st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            font-family: "Poppins", sans-serif;
        }
        h1 {
            color: #1a73e8;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #555;
        }
        .query-box {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
        }
        .footer {
            text-align: center;
            font-size: 0.85rem;
            color: #999;
            margin-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Title and instructions
st.markdown("<h1> CDC Assistant — Placement Query Engine</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Ask natural language queries about placement data (voice or text)</p>", unsafe_allow_html=True)

with st.container():
    st.markdown("#### Example Queries")
    st.markdown("""
    - “Which companies came in **July**?”
    - “Show companies offering more than **10 LPA**.”
    - “How many **CSE (Core)** students got placed in **Infosys**?”
    """)

# Input Section
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    user_query = st.text_input("Type your query below:", placeholder="e.g., Show companies offering above 8 LPA")
with col2:
    if st.button("Speak"):
        user_query = get_voice_input()

# Load database
df = load_db_to_context()

# Show preview of data
if not df.empty:
    with st.expander("View Placement Data (click to expand)"):
        st.dataframe(df)

# Query handling
if user_query:
    with st.spinner(" Thinking..."):
        llm_response = query_llm(user_query, df)
    st.markdown("### LLM Response")
    st.markdown(llm_response)

# Footer
st.markdown("<p class='footer'>⚙️ Powered by Streamlit · OpenAI · SQLite</p>", unsafe_allow_html=True)
