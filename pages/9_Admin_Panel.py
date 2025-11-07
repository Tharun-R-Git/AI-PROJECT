# pages/9_🔑_Admin_Panel.py
import streamlit as st
import importlib
from modules import database, gemini_parser
import json
import os
from datetime import datetime

# Force reload modules to avoid caching issues
importlib.reload(database)

# --- Authentication Check ---
if st.session_state.get("role") != "admin":
    st.error("Access Denied: You must be logged in as an Admin to view this page.")
    st.stop()

st.title("🔑 Admin Panel: Post New Job")
st.caption(f"Logged in as: {st.session_state.get('email')}")

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "job_pdfs"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

company_name = st.text_input("Company Name")
jd_text = st.text_area("Paste the full Job Description here", height=300)

# Optional PDF upload
st.markdown("### Optional: Upload Job Description PDF")
pdf_file = st.file_uploader("Upload JD PDF (Optional - for student reference only)", type=['pdf'], key="jd_pdf")
pdf_path = None

if pdf_file is not None:
    # Save PDF to uploads directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"{company_name.replace(' ', '_')}_{timestamp}.pdf" if company_name else f"jd_{timestamp}.pdf"
    pdf_path = os.path.join(UPLOADS_DIR, pdf_filename)
    
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    st.success(f"PDF uploaded: {pdf_filename}")

if st.button("Extract Criteria & Find Eligible Students"):
    if not company_name or not jd_text:
        st.warning("Please enter a company name and a job description.")
    else:
        with st.spinner("Calling Gemini API to extract criteria and job details..."):
            criteria, message = gemini_parser.get_gemini_json_response(jd_text)
            
            if criteria is None:
                st.error(f"Failed to parse criteria: {message}")
                st.stop()
            
            st.success(f"Information extracted successfully: {message}")
            
            # Display extracted information
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Eligibility Criteria")
                st.json({
                    'cgpa': criteria.get('cgpa'),
                    'branches': criteria.get('branches'),
                    'backlogs': criteria.get('backlogs'),
                    'year_gap': criteria.get('year_gap')
                })
            
            with col2:
                st.markdown("#### Job Details")
                details = {}
                if criteria.get('ctc'):
                    details['CTC'] = criteria.get('ctc')
                if criteria.get('stipend'):
                    details['Stipend'] = criteria.get('stipend')
                if criteria.get('last_date'):
                    details['Last Date'] = criteria.get('last_date')
                if criteria.get('company_description'):
                    details['Company Description'] = criteria.get('company_description')
                
                if details:
                    st.json(details)
                else:
                    st.info("No additional details found in JD")

        with st.spinner("Querying student database..."):
            eligible_students_df = database.get_students_matching_criteria(criteria)
            
            if eligible_students_df.empty:
                st.warning("No students match the extracted criteria.")
            else:
                st.subheader("Eligible Students")
                st.dataframe(eligible_students_df)
                st.info(f"Found {len(eligible_students_df)} eligible students.")
                
                # Store results in session state to be saved
                st.session_state['current_job_data'] = {
                    'company': company_name,
                    'jd': jd_text,
                    'criteria_json': json.dumps(criteria),
                    'eligible_emails': eligible_students_df['email'].tolist(),
                    'ctc': criteria.get('ctc'),
                    'stipend': criteria.get('stipend'),
                    'last_date': criteria.get('last_date'),
                    'company_description': criteria.get('company_description'),
                    'pdf_path': pdf_path
                }

# Add a button to "confirm" and save the job
if 'current_job_data' in st.session_state:
    st.markdown("---")
    if st.button(f"✅ Confirm and Post Job for {len(st.session_state['current_job_data']['eligible_emails'])} students"):
        data = st.session_state['current_job_data']
        
        success, message = database.save_job_and_eligibility(
            data['company'],
            data['jd'],
            data['criteria_json'],
            data['eligible_emails'],
            st.session_state['email'], # The admin's email
            ctc=data.get('ctc'),
            stipend=data.get('stipend'),
            last_date=data.get('last_date'),
            company_description=data.get('company_description'),
            pdf_path=data.get('pdf_path')
        )
        
        if success:
            st.success(f"Job posted successfully! Job ID: {message}")
            # Clear cache
            del st.session_state['current_job_data']
            st.rerun()
        else:
            st.error(f"Failed to save job: {message}")
