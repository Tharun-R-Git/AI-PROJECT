# 1_🏠_Home.py
import streamlit as st
from modules import database, auth, branch_mapper
import re
from dotenv import load_dotenv

# --- Page Config (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="AI Placement Assistant",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Load Environment Variables ---
# This loads API keys from .env for all other pages
load_dotenv() 

# --- Initialize Database ---
# This creates all the tables if they don't exist
database.init_database()

# --- Session State Initialization ---
# This is the "memory" of your app
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

# --- Utility Function ---
def is_valid_email(email):
    """Simple regex check for email validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

# --- Main App Logic ---
st.title("Welcome to the AI Placement Assistant 🚀")
st.caption("Your one-stop solution for placement preparation and opportunities.")

# If user is already logged in, show a welcome message
if st.session_state["logged_in"]:
    st.success(f"Logged in as **{st.session_state['email']}** ({st.session_state['role']})")
    st.markdown("Navigate to other pages using the sidebar on the left.")
    
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.session_state["email"] = None
        st.rerun()

# If user is not logged in, show Login and Signup tabs
else:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # --- LOGIN TAB ---
    with tab1:
        st.subheader("Login to your Account")
        with st.form("login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                elif not is_valid_email(login_email):
                    st.error("Please enter a valid email address.")
                else:
                    user_data = database.get_user(login_email)  # (hashed_pass, role)
                    
                    if user_data and auth.verify_password(login_password, user_data[0]):
                        st.session_state["logged_in"] = True
                        st.session_state["email"] = login_email
                        st.session_state["role"] = user_data[1]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

    # --- SIGN UP TAB ---
    with tab2:
        st.subheader("Create a New Account")
        with st.form("signup_form"):
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Create Password", type="password", key="signup_pass")
            signup_role = st.selectbox("I am a:", ("Student", "Admin"), key="signup_role")
            
            profile_data = {}
            if signup_role == "Student":
                st.markdown("---")
                st.write("Please fill in your academic profile:")
                col1, col2 = st.columns(2)
                profile_data['full_name'] = col1.text_input("Full Name")
                profile_data['roll_number'] = col2.text_input("Roll Number (e.g., 20BCE1234)")
                
                # Branch dropdown with mapping
                branch_options = branch_mapper.get_all_branches()
                branch_display = [f"{code} - {name}" for code, name in branch_options]
                selected_branch_display = col1.selectbox("Branch", branch_display, key="branch_select")
                # Extract branch code from selection
                if selected_branch_display:
                    profile_data['branch'] = selected_branch_display.split(' - ')[0]
                else:
                    profile_data['branch'] = None
                
                profile_data['cgpa'] = col2.number_input("Current CGPA (out of 10)", min_value=0.0, max_value=10.0, step=0.01)
                profile_data['class_10_perc'] = col1.number_input("Class 10 Percentage", min_value=0.0, max_value=100.0, step=0.1)
                profile_data['class_12_perc'] = col2.number_input("Class 12 Percentage", min_value=0.0, max_value=100.0, step=0.1)
                # Backlogs and year_gap default to 0 if not filled
                profile_data['backlogs'] = col1.number_input("Active Backlogs", min_value=0, step=1, value=0)
                profile_data['year_gap'] = col2.number_input("Year Gaps (in years)", min_value=0, step=1, value=0)
            
            signup_button = st.form_submit_button("Sign Up")

            if signup_button:
                if not signup_email or not signup_password:
                    st.error("Please fill in all required fields.")
                elif not is_valid_email(signup_email):
                    st.error("Please enter a valid email address.")
                elif len(signup_password.encode('utf-8')) > 72:
                    st.error("Password is too long. Please use a password with 72 characters or less.")
                elif signup_role == "Student":
                    # Check required fields (excluding backlogs and year_gap which default to 0)
                    required_fields = ['full_name', 'roll_number', 'branch', 'cgpa', 'class_10_perc', 'class_12_perc']
                    missing_fields = [field for field in required_fields if not profile_data.get(field) or (isinstance(profile_data.get(field), str) and profile_data.get(field).strip() == '')]
                    if missing_fields:
                        st.error("Please fill in all required student profile details (Full Name, Roll Number, Branch, CGPA, Class 10%, Class 12%).")
                    else:
                        # Ensure backlogs and year_gap have default values (they should already be 0 from number_input)
                        if profile_data.get('backlogs') is None:
                            profile_data['backlogs'] = 0
                        if profile_data.get('year_gap') is None:
                            profile_data['year_gap'] = 0
                        
                        hashed_pass = auth.hash_password(signup_password)
                        role_to_db = signup_role.lower()
                        
                        success, message = database.add_user_and_profile(
                            signup_email, hashed_pass, role_to_db, profile_data
                        )
                        
                        if success:
                            st.success(message)
                            st.info("You can now log in using the 'Login' tab.")
                        else:
                            st.error(message)
                else:
                    # Admin signup (no profile needed)
                    hashed_pass = auth.hash_password(signup_password)
                    role_to_db = signup_role.lower()
                    
                    success, message = database.add_user_and_profile(
                        signup_email, hashed_pass, role_to_db, {}
                    )
                    
                    if success:
                        st.success(message)
                        st.info("You can now log in using the 'Login' tab.")
                    else:
                        st.error(message)