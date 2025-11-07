"""
Script to generate fake student data in CSV format for testing
"""
import csv
import random
import string

# Branch codes and their variations
BRANCHES = {
    'CSE': ['Computer Science Engineering', 'CSE', 'Computer Science', 'CS'],
    'ECE': ['Electronics and Communication Engineering', 'ECE', 'Electronics', 'EC'],
    'IT': ['Information Technology', 'IT', 'Information Tech'],
    'EEE': ['Electrical and Electronics Engineering', 'EEE', 'Electrical Engineering', 'EE'],
    'MECH': ['Mechanical Engineering', 'MECH', 'Mechanical', 'ME'],
    'CIVIL': ['Civil Engineering', 'CIVIL', 'Civil'],
    'AERO': ['Aerospace Engineering', 'AERO', 'Aerospace'],
    'BIO': ['Biotechnology', 'BIO', 'Biotech'],
    'CHEM': ['Chemical Engineering', 'CHEM', 'Chemical'],
    'AUTO': ['Automobile Engineering', 'AUTO', 'Automobile']
}

def generate_roll_number(year, branch_code, num):
    """Generate a roll number like 20BCE1234"""
    return f"{year}{branch_code}{num:04d}"

def generate_email(name, roll_number):
    """Generate email from name and roll number"""
    name_parts = name.lower().split()
    if len(name_parts) >= 2:
        email = f"{name_parts[0]}.{name_parts[-1]}.{roll_number.lower()}@vit.ac.in"
    else:
        email = f"{name_parts[0]}.{roll_number.lower()}@vit.ac.in"
    return email

def generate_fake_name():
    """Generate a random Indian name"""
    first_names = ['Arjun', 'Priya', 'Rahul', 'Sneha', 'Vikram', 'Ananya', 'Karan', 'Divya', 
                   'Rohan', 'Kavya', 'Aditya', 'Meera', 'Siddharth', 'Pooja', 'Raj', 'Neha',
                   'Aryan', 'Shreya', 'Vishal', 'Anjali', 'Kunal', 'Riya', 'Aman', 'Sakshi',
                   'Nikhil', 'Tanvi', 'Rohit', 'Isha', 'Varun', 'Swati', 'Abhishek', 'Nisha',
                   'Sahil', 'Preeti', 'Gaurav', 'Deepika', 'Harsh', 'Manisha', 'Yash', 'Pallavi']
    last_names = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Reddy', 'Rao', 'Nair',
                  'Iyer', 'Menon', 'Joshi', 'Desai', 'Mehta', 'Agarwal', 'Malhotra', 'Verma',
                  'Chopra', 'Kapoor', 'Shah', 'Bansal', 'Arora', 'Saxena', 'Tiwari', 'Mishra',
                  'Pandey', 'Yadav', 'Jain', 'Goyal', 'Seth', 'Bhatia']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_student_data(num_students=100):
    """Generate fake student data"""
    students = []
    year = 20  # Batch year (e.g., 2020)
    branch_codes = list(BRANCHES.keys())
    
    for i in range(1, num_students + 1):
        # Random branch
        branch_code = random.choice(branch_codes)
        roll_number = generate_roll_number(year, branch_code, i)
        
        # Generate name and email
        name = generate_fake_name()
        email = generate_email(name, roll_number)
        
        # Generate academic data
        cgpa = round(random.uniform(6.0, 9.8), 2)  # CGPA between 6.0 and 9.8
        class_10 = round(random.uniform(75.0, 98.0), 1)  # Class 10 percentage
        class_12 = round(random.uniform(75.0, 98.0), 1)  # Class 12 percentage
        
        # Backlogs (most students have 0, some have 1-2)
        backlogs = random.choices([0, 0, 0, 0, 0, 1, 1, 2], weights=[70, 70, 70, 70, 70, 20, 5, 5])[0]
        
        # Year gaps (most have 0, few have 1)
        year_gap = random.choices([0, 0, 0, 1], weights=[85, 85, 85, 15])[0]
        
        students.append({
            'email': email,
            'roll_number': roll_number,
            'full_name': name,
            'branch': branch_code,
            'cgpa': cgpa,
            'class_10_perc': class_10,
            'class_12_perc': class_12,
            'backlogs': backlogs,
            'year_gap': year_gap
        })
    
    return students

def save_to_csv(students, filename='fake_students.csv'):
    """Save student data to CSV file"""
    fieldnames = ['email', 'roll_number', 'full_name', 'branch', 'cgpa', 
                  'class_10_perc', 'class_12_perc', 'backlogs', 'year_gap']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students)
    
    print(f"Generated {len(students)} fake student records in {filename}")

if __name__ == "__main__":
    print("Generating fake student data...")
    students = generate_student_data(num_students=150)  # Generate 150 students
    save_to_csv(students)
    print(f"\nSample records:")
    for i, student in enumerate(students[:3]):
        print(f"\n{i+1}. {student['full_name']} ({student['roll_number']})")
        print(f"   Email: {student['email']}")
        print(f"   Branch: {student['branch']}, CGPA: {student['cgpa']}")
        print(f"   Class 10: {student['class_10_perc']}%, Class 12: {student['class_12_perc']}%")
        print(f"   Backlogs: {student['backlogs']}, Year Gap: {student['year_gap']}")

