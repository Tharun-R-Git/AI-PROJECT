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

import os
import json
import io
import wave
from dotenv import load_dotenv
import google.generativeai as genai
import sounddevice as sd
from openai import OpenAI

load_dotenv()
gemini_api_key = os.getenv('GOOGLE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client for Whisper transcription
openai_client = None
if openai_api_key:
    openai_client = OpenAI(api_key=openai_api_key)

st.title("🤖 AI-Powered Interview Preparation Guide")
st.caption("Practice interview questions and get instant feedback on your answers")

# Input section
st.subheader("📝 Input Job Description and Resume")
col1, col2 = st.columns(2)

with col1:
    jd_text = st.text_area(
        "Paste Job Description (JD)",
        height=200,
        placeholder="Paste the full job description here...",
        key="jd_input"
    )

with col2:
    resume_text = st.text_area(
        "Paste Resume/CV Text",
        height=200,
        placeholder="Paste your resume text here...",
        key="resume_input"
    )

generate_btn = st.button("🚀 Generate Interview Questions", type="primary", use_container_width=True)

if not gemini_api_key:
    st.error("⚠️ GOOGLE_API_KEY missing. Please add it to your .env file.")

genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

def safe_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except:
                return None
        return None

def generate_questions(jd: str):
    prompt = (
        "You are an expert interview coach. Based ONLY on the job description (JD) below, "
        "generate 3 interview questions each in the sections: technical, core_concepts, projects, hr, company_specific.\n"
        "Return EXACT JSON with keys and 3 questions as lists:\n"
        '{ "technical": [...], "core_concepts": [...], "projects": [...], "hr": [...], "company_specific": [...] }\n\n'
        f"JD:\n{jd}\n"
    )
    resp = gemini_model.generate_content(prompt)
    return safe_parse_json(resp.text or "")

def get_voice_input(duration=30, samplerate=16000):
    """Record audio and transcribe using OpenAI Whisper."""
    if not openai_client:
        return None, "OpenAI API key not configured. Please add OPENAI_API_KEY to .env file."
    
    try:
        # Record audio for specified duration
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()  # Wait for recording to complete
        
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio.tobytes())
        wav_io.seek(0)
        
        # Transcribe using Whisper
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=("voice.wav", wav_io)
        )
        
        return transcription.text.strip(), None
    except Exception as e:
        return None, f"Error recording/transcribing: {str(e)}"

def evaluate_text_answer(section, jd, question, answer):
    prompt = (
        f"You are an expert interviewer. Evaluate this answer:\n"
        f"Section: {section}\nJob Description:\n{jd}\nQuestion:\n{question}\nAnswer:\n{answer}\n"
        "Return JSON with score (1-10), feedback (text), and suggestions (list of strings)."
    )
    resp = gemini_model.generate_content(prompt)
    return safe_parse_json(resp.text or "") or {}

sections_order = [
    ("Technical", "technical"),
    ("Core Concepts", "core_concepts"),
    ("Projects", "projects"),
    ("HR", "hr"),
    ("Company Specific", "company_specific"),
]

# Generate questions and initialize session state
if generate_btn:
    if not gemini_api_key:
        st.error("GOOGLE_API_KEY missing.")
    elif not jd_text or not resume_text:
        st.warning("⚠️ Please provide both Job Description and Resume")
    else:
        with st.spinner("🔄 Generating interview questions..."):
            data = generate_questions(jd_text.strip())
        if not data:
            st.error("❌ Failed to generate questions. Try again.")
        else:
            st.success("✅ Questions generated! Starting interview practice...")
            # Limit to 3 questions per section
            for key in data:
                if isinstance(data[key], list) and len(data[key]) > 3:
                    data[key] = data[key][:3]
            
            st.session_state["questions"] = data
            st.session_state["section_idx"] = 0
            st.session_state["question_idx"] = 0
            st.session_state["feedback"] = None
            st.session_state["answer_text"] = ""
            st.session_state["submitted"] = False
            st.rerun()

# Show interview questions
if "questions" in st.session_state:
    data = st.session_state["questions"]
    section_i = st.session_state.get("section_idx", 0)
    question_i = st.session_state.get("question_idx", 0)
    submitted = st.session_state.get("submitted", False)
    feedback = st.session_state.get("feedback")

    if section_i >= len(sections_order):
        st.success("🎉 Congratulations! You've completed all sections. Great job!")
        st.balloons()
        if st.button("🔄 Start Over"):
            for key in ["questions", "section_idx", "question_idx", "feedback", "answer_text", "submitted"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        section_name, section_key = sections_order[section_i]
        questions_list = data.get(section_key, [])
        
        # Limit to 3 questions
        if len(questions_list) > 3:
            questions_list = questions_list[:3]

        if question_i >= len(questions_list):
            # Move to next section
            st.info(f"✅ Completed {section_name} section! Moving to next section...")
            st.session_state["section_idx"] += 1
            st.session_state["question_idx"] = 0
            st.session_state["feedback"] = None
            st.session_state["answer_text"] = ""
            st.session_state["submitted"] = False
            st.rerun()
        else:
            current_question = questions_list[question_i]
            
            # Progress indicator
            total_questions = sum(len(data.get(key, [])) for key in ["technical", "core_concepts", "projects", "hr", "company_specific"])
            current_q_num = sum(len(data.get(sections_order[i][1], [])) for i in range(section_i)) + question_i + 1
            progress = current_q_num / total_questions
            
            st.progress(progress, text=f"Progress: {current_q_num}/{total_questions} questions")
            
            # Section and question display
            st.markdown("---")
            st.markdown(f"### 📂 Section: **{section_name}**")
            st.markdown(f"**Question {question_i + 1} of {len(questions_list)}**")
            st.markdown(f"#### {current_question}")
            st.markdown("---")
            
            # Show answer input only if not submitted
            if not submitted:
                # Input mode selection
                input_mode = st.radio(
                    "Choose input method:",
                    ["✍️ Type Answer", "🎤 Voice Answer"],
                    horizontal=True,
                    key=f"input_mode_{section_i}_{question_i}"
                )
                
                answer_text = st.session_state.get("answer_text", "")
                current_answer_key = f"current_answer_{section_i}_{question_i}"
                
                if input_mode == "✍️ Type Answer":
                    answer_text = st.text_area(
                        "✍️ Type your answer here:",
                        value=answer_text,
                        height=150,
                        key=current_answer_key,
                        placeholder="Enter your answer to the question above..."
                    )
                else:
                    # Voice input mode
                    st.markdown("**🎤 Voice Recording**")
                    st.info("💡 Click 'Record Answer' to start recording. You'll have time to speak your answer.")
                    
                    # Recording duration slider
                    record_duration = st.slider(
                        "Recording duration (seconds):",
                        min_value=10,
                        max_value=60,
                        value=30,
                        key=f"duration_{section_i}_{question_i}",
                        help="How long you want to record your answer"
                    )
                    
                    # Record button
                    record_btn = st.button(
                        "🎙️ Record Answer", 
                        key=f"record_{section_i}_{question_i}", 
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if record_btn:
                        with st.spinner(f"🎤 Recording for {record_duration} seconds... Speak now!"):
                            transcribed_text, error = get_voice_input(duration=record_duration)
                            
                            if error:
                                st.error(f"❌ {error}")
                            elif transcribed_text:
                                answer_text = transcribed_text
                                st.session_state["answer_text"] = transcribed_text
                                st.success("✅ Voice transcribed successfully!")
                                
                                # Show transcribed text
                                st.markdown("**📝 Transcribed Answer:**")
                                st.text_area(
                                    "Your transcribed answer:",
                                    value=transcribed_text,
                                    height=120,
                                    key=f"transcribed_{section_i}_{question_i}",
                                    help="Review and edit if needed before submitting"
                                )
                    
                    # Show current answer if available (editable)
                    if answer_text:
                        st.markdown("**📝 Your Answer (you can edit):**")
                        answer_text = st.text_area(
                            "Edit your answer if needed:",
                            value=answer_text,
                            height=120,
                            key=current_answer_key,
                            help="Review and edit your transcribed answer before submitting"
                        )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submit_btn = st.button("✅ Submit Answer", type="primary", use_container_width=True, key=f"submit_{section_i}_{question_i}")
                with col2:
                    skip_btn = st.button("⏭️ Skip Question", use_container_width=True, key=f"skip_{section_i}_{question_i}")
                
                if submit_btn:
                    # Get answer from the appropriate source
                    if current_answer_key in st.session_state:
                        final_answer = st.session_state[current_answer_key]
                    else:
                        final_answer = st.session_state.get("answer_text", "")
                    
                    if not final_answer or not final_answer.strip():
                        st.warning("⚠️ Please provide an answer (type or record) before submitting.")
                    else:
                        with st.spinner("🤔 Evaluating your answer..."):
                            feedback = evaluate_text_answer(section_name, jd_text, current_question, final_answer)
                            if feedback:
                                st.session_state["feedback"] = feedback
                                st.session_state["answer_text"] = final_answer
                                st.session_state["submitted"] = True
                                st.rerun()
                            else:
                                st.error("❌ Evaluation failed. Please try again.")
                
                if skip_btn:
                    st.session_state["question_idx"] += 1
                    st.session_state["submitted"] = False
                    st.session_state["feedback"] = None
                    st.session_state["answer_text"] = ""
                    st.rerun()
            
            # Show feedback after submission
            if submitted and feedback:
                st.markdown("---")
                st.markdown("### 📊 Feedback")
                
                # Score display
                score = feedback.get('score', 'N/A')
                if isinstance(score, (int, float)):
                    if score >= 8:
                        st.success(f"**Score: {score}/10** ⭐ Excellent!")
                    elif score >= 6:
                        st.info(f"**Score: {score}/10** 👍 Good!")
                    else:
                        st.warning(f"**Score: {score}/10** 💪 Keep practicing!")
                else:
                    st.info(f"**Score:** {score}/10")
                
                # Feedback text
                feedback_text = feedback.get('feedback', '')
                if feedback_text:
                    st.markdown("#### 💬 Detailed Feedback")
                    st.write(feedback_text)
                
                # Suggestions
                suggestions = feedback.get("suggestions", [])
                if suggestions:
                    st.markdown("#### 💡 Suggestions for Improvement")
                    for i, s in enumerate(suggestions, 1):
                        st.markdown(f"{i}. {s}")
                
                # Show submitted answer
                st.markdown("---")
                st.markdown("#### 📝 Your Answer")
                st.text_area(
                    "Your submitted answer:",
                    st.session_state.get("answer_text", ""),
                    height=100,
                    disabled=True,
                    key=f"submitted_answer_{section_i}_{question_i}"
                )
                
                # Next question button
                st.markdown("---")
                next_btn = st.button("➡️ Next Question", type="primary", use_container_width=True)
                
                if next_btn:
                    st.session_state["question_idx"] += 1
                    st.session_state["submitted"] = False
                    st.session_state["feedback"] = None
                    st.session_state["answer_text"] = ""
                    st.rerun()
else:
    st.info("👆 Please enter Job Description and Resume above, then click 'Generate Interview Questions' to begin.")
