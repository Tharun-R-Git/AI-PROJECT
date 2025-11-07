# pages/2_🎓_Student_Dashboard.py
import streamlit as st
from modules import database
import json
import os
import pandas as pd

# --- Authentication Check ---
if st.session_state.get("role") != "student":
    st.error("Access Denied: You must be logged in as a Student to view this page.")
    st.stop()

st.title("🎓 Student Dashboard")
st.subheader(f"Welcome, {st.session_state.get('email')}!")

st.header("My Eligible Jobs")
st.write("This list shows all jobs that match your profile.")

# Refresh button
if st.button("🔄 Refresh Jobs"):
    st.rerun()

with st.spinner("Fetching your eligible jobs..."):
    jobs_df = database.get_eligible_jobs_for_student(st.session_state['email'])

if jobs_df.empty:
    st.info("📭 No jobs have been posted for you yet. Check back later!")
    st.markdown("""
    **Note:** Jobs will appear here automatically when:
    - An admin posts a new job
    - Your profile matches the job requirements (CGPA, Branch, Backlogs, Year Gap)
    """)
else:
    st.success(f"✅ You are eligible for {len(jobs_df)} job(s)!")
    st.markdown("---")
    
    # Display jobs in a simple list format
    for index, row in jobs_df.iterrows():
        company_name = row['company_name']
        
        # Create a card-like display
        with st.container():
            st.markdown(f"### {company_name}")
            st.markdown("---")
            
            # Display key information vertically
            info_items = []
            
            # CTC
            if pd.notna(row.get('ctc')) and row.get('ctc'):
                info_items.append(("💰 CTC", str(row['ctc'])))
            else:
                info_items.append(("💰 CTC", "Not specified"))
            
            # Stipend
            if pd.notna(row.get('stipend')) and row.get('stipend'):
                info_items.append(("💵 Stipend", str(row['stipend'])))
            else:
                info_items.append(("💵 Stipend", "N/A"))
            
            # Last Date
            if pd.notna(row.get('last_date')) and row.get('last_date'):
                info_items.append(("📅 Last Date to Apply", str(row['last_date'])))
            else:
                info_items.append(("📅 Last Date to Apply", "Not specified"))
            
            # Display info items vertically
            for label, value in info_items:
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{label}:**")
                with col2:
                    st.markdown(value)
            
            # PDF Download
            st.markdown("---")
            pdf_path = row.get('pdf_path')
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download Job Description PDF",
                        data=pdf_file.read(),
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        key=f"pdf_{index}",
                        use_container_width=True
                    )
            else:
                st.info("📄 No PDF available for this job")
            
            # Company Description
            if pd.notna(row.get('company_description')) and row.get('company_description'):
                st.markdown("---")
                st.markdown("#### About the Company")
                st.info(row['company_description'])
            
            st.markdown("---")
            st.markdown("")  # Add some spacing between jobs
