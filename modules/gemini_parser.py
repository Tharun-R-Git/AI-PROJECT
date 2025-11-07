# modules/gemini_parser.py
import google.generativeai as genai
import os
import json
import re
from modules import branch_mapper

def get_gemini_json_response(jd_text):
    """
    Sends the JD to Gemini and asks for structured JSON output.
    """
    # Configure the API (assumes GOOGLE_API_KEY is in .env)
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY_1") or os.getenv("GOOGLE_API_KEY"))
    except Exception as e:
        return None, f"Error configuring Gemini API: {e}. Make sure API key is in .env."

    model = genai.GenerativeModel('gemini-2.5-flash') # Use a model good at JSON
    
    prompt = f"""
    You are an expert HR data extractor. From the following job description, extract all relevant information.
    Return *only* a valid JSON object. Do not include any text before or after the JSON.
    
    The JSON should have these keys:
    - "cgpa": The minimum CGPA required (e.g., 7.5). If not mentioned, use null.
    - "branches": A Python list of allowed branches (e.g., ["CSE", "ECE", "IT", "Mechanical"]). If all branches are allowed or not specified, use an empty list [].
    - "backlogs": The maximum number of *active* backlogs allowed (e.g., 0 or 1). If not mentioned, use null.
    - "year_gap": The maximum allowed year gap (e.g., 1 or 0). If not mentioned, use null.
    - "ctc": The CTC (Cost to Company) package offered (e.g., "15 LPA", "8-12 LPA", "25 LPA"). If not mentioned, use null.
    - "stipend": The stipend/internship salary if mentioned (e.g., "30k/month", "50k"). If not mentioned, use null.
    - "last_date": The last date to apply (e.g., "2024-12-31", "31st December 2024", "Dec 31, 2024"). If not mentioned, use null.
    - "company_description": A brief description about the company (2-3 sentences). If not mentioned, use null.

    Job Description:
    ---
    {jd_text}
    ---
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean the response to find the JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            return None, "Gemini did not return a valid JSON object."
            
        json_str = match.group(0)
        criteria = json.loads(json_str)
        
        # Standardize keys
        default_criteria = {
            'cgpa': None,
            'branches': [],
            'backlogs': None,
            'year_gap': None,
            'ctc': None,
            'stipend': None,
            'last_date': None,
            'company_description': None
        }
        # Update default with whatever Gemini found
        default_criteria.update(criteria)
        
        # Normalize branch names to standard codes
        if default_criteria.get('branches'):
            normalized_branches = branch_mapper.normalize_branch_list(default_criteria['branches'])
            default_criteria['branches'] = normalized_branches

        return default_criteria, "Successfully parsed criteria."

    except json.JSONDecodeError:
        return None, f"Error decoding JSON. Gemini response was: {text}"
    except Exception as e:
        return None, f"An error occurred with Gemini: {e}"