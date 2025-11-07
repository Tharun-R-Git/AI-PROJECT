"""
Branch name mapping and normalization module
Maps various branch name formats to standardized codes
"""
import re

# Standard branch codes (as stored in database)
BRANCH_CODES = {
    'CSE': 'CSE',
    'ECE': 'ECE', 
    'IT': 'IT',
    'EEE': 'EEE',
    'MECH': 'MECH',
    'CIVIL': 'CIVIL',
    'AERO': 'AERO',
    'BIO': 'BIO',
    'CHEM': 'CHEM',
    'AUTO': 'AUTO',
    'BCE': 'CSE',  # CSE Core
    'BCI': 'CSE',  # CSE Information Security
    'BCT': 'CSE',  # CSE IoT
    'BDS': 'CSE',  # CSE Data Science
    'BBS': 'CSE',  # CSE Business Systems
    'BKT': 'CSE',  # CSE Blockchain
    'BIT': 'IT',   # Information Technology
    'BEC': 'ECE',  # Electronics
    'BEE': 'EEE',  # Electrical
}

# Mapping of common branch name variations to standard codes
BRANCH_MAPPING = {
    # CSE variations
    'computer science': 'CSE',
    'computer science engineering': 'CSE',
    'cse': 'CSE',
    'cs': 'CSE',
    'computer science and engineering': 'CSE',
    'bce': 'CSE',
    'bci': 'CSE',
    'bct': 'CSE',
    'bds': 'CSE',
    'bbs': 'CSE',
    'bkt': 'CSE',
    
    # ECE variations
    'electronics and communication': 'ECE',
    'electronics and communication engineering': 'ECE',
    'ece': 'ECE',
    'ec': 'ECE',
    'electronics': 'ECE',
    'bec': 'ECE',
    
    # IT variations
    'information technology': 'IT',
    'it': 'IT',
    'bit': 'IT',
    'information tech': 'IT',
    
    # EEE variations
    'electrical and electronics': 'EEE',
    'electrical and electronics engineering': 'EEE',
    'eee': 'EEE',
    'ee': 'EEE',
    'electrical': 'EEE',
    'electrical engineering': 'EEE',
    'bee': 'EEE',
    
    # Mechanical variations
    'mechanical engineering': 'MECH',
    'mechanical': 'MECH',
    'mech': 'MECH',
    'me': 'MECH',
    
    # Civil variations
    'civil engineering': 'CIVIL',
    'civil': 'CIVIL',
    
    # Aerospace variations
    'aerospace engineering': 'AERO',
    'aerospace': 'AERO',
    'aero': 'AERO',
    
    # Biotechnology variations
    'biotechnology': 'BIO',
    'biotech': 'BIO',
    'bio': 'BIO',
    
    # Chemical variations
    'chemical engineering': 'CHEM',
    'chemical': 'CHEM',
    'chem': 'CHEM',
    
    # Automobile variations
    'automobile engineering': 'AUTO',
    'automobile': 'AUTO',
    'auto': 'AUTO',
}

def normalize_branch(branch_input):
    """
    Normalize branch name to standard code.
    
    Args:
        branch_input: Branch name in any format (string)
    
    Returns:
        Standardized branch code (e.g., 'CSE', 'ECE', 'IT') or None if not found
    """
    if not branch_input:
        return None
    
    # Convert to lowercase and strip whitespace
    branch_lower = branch_input.strip().lower()
    
    # Direct lookup in mapping
    if branch_lower in BRANCH_MAPPING:
        return BRANCH_MAPPING[branch_lower]
    
    # Check if it's already a standard code (case-insensitive)
    branch_upper = branch_input.strip().upper()
    if branch_upper in BRANCH_CODES:
        return BRANCH_CODES[branch_upper]
    
    # Try partial matching for common patterns
    for key, code in BRANCH_MAPPING.items():
        if key in branch_lower or branch_lower in key:
            return code
    
    # Try to extract from common patterns
    patterns = [
        (r'computer\s*science', 'CSE'),
        (r'electronics\s*(?:and\s*)?communication', 'ECE'),
        (r'information\s*technology', 'IT'),
        (r'electrical\s*(?:and\s*)?electronics', 'EEE'),
        (r'mechanical', 'MECH'),
        (r'civil', 'CIVIL'),
        (r'aerospace', 'AERO'),
        (r'biotech', 'BIO'),
        (r'chemical', 'CHEM'),
        (r'automobile', 'AUTO'),
    ]
    
    for pattern, code in patterns:
        if re.search(pattern, branch_lower):
            return code
    
    return None

def normalize_branch_list(branch_list):
    """
    Normalize a list of branch names to standard codes.
    
    Args:
        branch_list: List of branch names
    
    Returns:
        List of standardized branch codes (duplicates removed)
    """
    if not branch_list:
        return []
    
    normalized = []
    for branch in branch_list:
        code = normalize_branch(branch)
        if code and code not in normalized:
            normalized.append(code)
    
    return normalized

def get_branch_display_name(code):
    """
    Get a user-friendly display name for a branch code.
    
    Args:
        code: Branch code (e.g., 'CSE', 'ECE')
    
    Returns:
        Display name (e.g., 'Computer Science Engineering')
    """
    display_names = {
        'CSE': 'Computer Science Engineering',
        'ECE': 'Electronics and Communication Engineering',
        'IT': 'Information Technology',
        'EEE': 'Electrical and Electronics Engineering',
        'MECH': 'Mechanical Engineering',
        'CIVIL': 'Civil Engineering',
        'AERO': 'Aerospace Engineering',
        'BIO': 'Biotechnology',
        'CHEM': 'Chemical Engineering',
        'AUTO': 'Automobile Engineering',
    }
    return display_names.get(code, code)

def get_all_branches():
    """
    Get list of all available branch codes with display names.
    
    Returns:
        List of tuples: [(code, display_name), ...]
    """
    return [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('IT', 'Information Technology'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('AERO', 'Aerospace Engineering'),
        ('BIO', 'Biotechnology'),
        ('CHEM', 'Chemical Engineering'),
        ('AUTO', 'Automobile Engineering'),
    ]

