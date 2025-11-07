# Placement Assistant Project - Setup Instructions

## Overview
This document outlines what needs to be set up and fixed for the Placement Assistant application to work smoothly.

## ✅ Issues Fixed

1. **Database Setup Script Created**: `setup_database.py` - Populates `data.db` from `data.csv`
2. **Duplicate Code Removed**: Fixed duplicate code in `pages/3_JD_Resume_Matcher.py`
3. **Deprecated Function Fixed**: Replaced `st.experimental_rerun()` with `st.rerun()` in `pages/6_Mock_Interview.py`
4. **Requirements Updated**: Added `numpy` to `requirements.txt`
5. **Voice Engine Fixed**: Corrected OpenAI Whisper model name from `gpt-4o-mini-transcribe` to `whisper-1`

## 🔧 Required Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root with the following API keys:

```env
# Google Gemini API Keys (for JD parsing, Resume matching, Mock Interview)
GEMINI_API_KEY_1=your_gemini_api_key_1_here
GEMINI_API_KEY_2=your_gemini_api_key_2_here
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI API Key (for Voice Query Engine - Whisper transcription and GPT-4o-mini)
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: You can get:
- Gemini API keys from: https://makersuite.google.com/app/apikey
- OpenAI API key from: https://platform.openai.com/api-keys

### 3. Set Up Placement Database
Run the database setup script to populate `data.db` from `data.csv`:

```bash
python setup_database.py
```

This will:
- Create the `companies` table in `data.db`
- Populate it with data from `data.csv`
- Verify the data was inserted correctly

**Important**: The `data.csv` file must exist in the project root with the correct structure:
- Columns: `Company`, `Month`, `Average_CTC_(LPA)`, `BBS`, `BCB`, `BCE`, `BCI`, `BCT`, `BDS`, `BEC`, `BEE`, `BIT`, `BKT`

### 4. Verify Database Structure
The `data.db` should have a `companies` table with these columns:
- `Company` (TEXT)
- `Month` (TEXT)
- `Average_CTC_LPA` (REAL)
- `BBS`, `BCB`, `BCE`, `BCI`, `BCT`, `BDS`, `BEC`, `BEE`, `BIT`, `BKT` (all INTEGER)

## 📁 Project Structure

```
placement_assistant_project/
├── 1_Home.py                    # Main entry point with authentication
├── setup_database.py            # NEW: Script to populate data.db
├── data.csv                     # Source data for placement database
├── data.db                      # SQLite database (created by setup_database.py)
├── placement_users.db           # User authentication database
├── requirements.txt             # Python dependencies
├── .env                         # API keys (create this file)
├── modules/
│   ├── auth.py                  # Password hashing utilities
│   ├── database.py              # Database operations for users/jobs
│   └── gemini_parser.py         # Gemini API for JD parsing
├── pages/
│   ├── 2_Student_Dashboard.py   # Student view of eligible jobs
│   ├── 3_JD_Resume_Matcher.py   # Resume analysis tool
│   ├── 4_Voice_Query_Engine.py # Voice-based placement queries
│   ├── 5_Placement_Insights.py  # Analytics dashboard
│   ├── 6_Mock_Interview.py      # Interview preparation
│   └── 9_Admin_Panel.py        # Admin job posting interface
└── data/                        # CSV files (backup/reference)
```

## 🚀 Running the Application

1. Make sure all dependencies are installed
2. Create and populate `.env` file with API keys
3. Run `setup_database.py` to populate `data.db`
4. Start the Streamlit app:

```bash
streamlit run 1_Home.py
```

## ⚠️ Important Notes

### Voice Query Engine (`pages/4_Voice_Query_Engine.py`)
- **Requires**: `data.db` with `companies` table populated
- **Uses**: OpenAI API for Whisper transcription and GPT-4o-mini for queries
- **Note**: The voice recording uses `sounddevice` which may require audio drivers on Windows

### Placement Insights (`pages/5_Placement_Insights.py`)
- **Requires**: `data.db` with `companies` table populated
- **Uses**: Plotly for visualizations
- **Note**: Column names are normalized (uppercase, underscores) in the code

### JD Resume Matcher (`pages/3_JD_Resume_Matcher.py`)
- **Requires**: Gemini API keys (`GEMINI_API_KEY_1` and `GEMINI_API_KEY_2`)
- **Uses**: Google Gemini models for resume analysis
- **Fixed**: Removed duplicate code that was causing issues

### Mock Interview (`pages/6_Mock_Interview.py`)
- **Requires**: `GOOGLE_API_KEY` (Gemini API key)
- **Fixed**: Replaced deprecated `st.experimental_rerun()` with `st.rerun()`

## 🔍 Troubleshooting

### Database Issues
- **Error**: "Database file not found" or "Table 'companies' does not exist"
  - **Solution**: Run `python setup_database.py` to create and populate the database

### API Key Issues
- **Error**: "API key not found" or "Invalid API key"
  - **Solution**: Check that `.env` file exists and contains valid API keys
  - Make sure you're using `load_dotenv()` in your code (already done)

### Import Errors
- **Error**: "Module not found"
  - **Solution**: Run `pip install -r requirements.txt`

### Voice Recording Issues
- **Error**: Audio recording fails
  - **Solution**: Install audio drivers for Windows, or use text input instead

## 📝 Additional Notes

1. **Data Files**: The `data/` folder contains individual branch CSV files. These are not directly used by the application - only `data.csv` in the root is used.

2. **Database Files**: 
   - `placement_users.db` - Created automatically by `modules/database.py` on first run
   - `data.db` - Must be created using `setup_database.py`

3. **Authentication**: The app uses session state for authentication. Users must log in from the Home page before accessing other features.

4. **Admin Access**: To access the Admin Panel, create an account with role "Admin" during signup.

## ✅ Checklist Before Running

- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with all required API keys
- [ ] Run `python setup_database.py` to populate `data.db`
- [ ] Verify `data.db` exists and has the `companies` table
- [ ] Verify `placement_users.db` will be created on first run (automatic)
- [ ] Test the application: `streamlit run 1_Home.py`

## 🎯 Next Steps

1. Run the setup script to populate the database
2. Create a `.env` file with your API keys
3. Test each page to ensure everything works
4. Create test user accounts (Student and Admin)
5. Test the Voice Query Engine with actual queries
6. Test Placement Insights dashboard with filters

