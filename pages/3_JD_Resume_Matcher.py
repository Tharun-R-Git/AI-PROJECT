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


import streamlit as st

import PyPDF2

import google.generativeai as genai

from dotenv import load_dotenv

import os

load_dotenv()

API_KEYS = [os.getenv("GEMINI_API_KEY_1"), os.getenv("GEMINI_API_KEY_2")]



DEFAULT_MODEL = "models/gemini-2.5-flash"

AVAILABLE_MODELS = [

    "models/gemini-pro-latest",

    "models/gemini-2.5-pro-preview-06-05",

    "models/gemini-2.5-pro",

    "models/gemini-2.5-flash"

]



st.title("🧑‍💼 CDC Assistant - Resume Analyzer")

st.write("Upload your resume (PDF) and provide your job description. Get tailored AI-powered feedback!")



model_choice = st.selectbox("Select Gemini Model", AVAILABLE_MODELS, index=0)



uploaded_file = st.file_uploader("Upload your Resume PDF", type=["pdf"])

resume_text = None



if uploaded_file:

    try:

        with st.spinner("Extracting text from your PDF..."):

            reader = PyPDF2.PdfReader(uploaded_file)

            resume_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

        st.success("Resume processed successfully.")

    except Exception as e:

        st.error(f"Error reading PDF: {e}")



job_description = st.text_area("Paste the Job Description here", height=200)



def ask_gemini(prompt, api_key):

    try:

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(model_choice)

        response = model.generate_content([prompt])

        return response.text.strip()

    except Exception as e:

        return f"[Error]: {e}"



if st.button("Analyze Resume") and resume_text and job_description:

    # Use keys alternately for each major section

    key_iter = iter(API_KEYS * 2)  # Just in case, double so we don't run out



    with st.status("Extracting skills & experience from resume...", expanded=True):

        skills_prompt = f"""

You are a professional resume analyzer AI.

Extract all skills, experience, projects, certifications, education details, and main keywords from the candidate's resume below. Structure your output as:



Skills:

Experience:

Certifications:

Projects:

Education:

Tailored Keywords:



Resume:

{resume_text}

"""

        skills_report = ask_gemini(skills_prompt, next(key_iter))

        st.write(skills_report)



    with st.status("Analyzing resume vs. job description...", expanded=True):

        match_prompt = f"""

You are an expert at resume-job matching.

Given these:

Job Description:

{job_description}



Resume Summary:

{skills_report}



1. Analyze the overlap and differences between required and provided skills/evidence.

2. List clear matches and clear gaps (missing/weak areas).

3. Assign a detailed suitability score out of 10, with reasoning.



Use this structure:

Matched Requirements:

Missing/Weak Areas:

Suitability Score (1-10) with reason:

"""

        match_report = ask_gemini(match_prompt, next(key_iter))

        st.write(match_report)



    with st.status("Generating actionable recommendations for the candidate...", expanded=True):

        recommendation_prompt = f"""

Imagine you are a career coach for job applicants.

Given the following analysis, suggest actionable recommendations the candidate should follow to improve their chances of getting this job.

Your recommendations should be practical, focused, and tailored to this job description and resume.



Analysis:

{match_report}



Structure:

1. Immediate Resume/Skill Improvement Actions: (If match is <8.5, then give 1 solid project idea and professional certifications or courses available in the internet, along with any improvement tips that can be made in the resume). If score > 8.5, you can give general tips/resume based tips.

2. Longer-Term Career/Skill Tips:

"""

        recommendations = ask_gemini(recommendation_prompt, next(key_iter))

        st.write(recommendations)



    with st.status("Summarizing for recruiter...", expanded=True):

        summary_prompt = f"""

Summarize the candidate's suitability for this job in 2-3 recruiter-friendly sentences, using this info:



Job Description:

                    {job_description}



Candidate Resume Analysis:

{match_report}



Candidate Recommendations:

{recommendations}



Output only the summary for a recruiter.

"""

        summary = ask_gemini(summary_prompt, next(key_iter))

        st.success(summary)



if not (uploaded_file and job_description):

    st.info("Please upload a PDF and enter a job description to begin analysis.")



st.markdown("""

---

**Powered by Google Gemini & Streamlit**  

Created by your AI coding assistant 🤖

""")
