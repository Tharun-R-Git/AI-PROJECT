# Student Data Setup Guide

## Overview
This guide explains how to generate fake student data and import it into the database for testing the job matching feature.

## Step 1: Generate Fake Student Data

Run the script to generate a CSV file with fake student records:

```bash
python generate_fake_students.py
```

This will create `fake_students.csv` with 150 fake student records including:
- Random Indian names
- Email addresses (format: firstname.lastname.rollnumber@vit.ac.in)
- Roll numbers (format: 20BRANCHCODE####)
- Random CGPA (6.0 - 9.8)
- Random Class 10 and 12 percentages (75% - 98%)
- Random backlogs (mostly 0, some 1-2)
- Random year gaps (mostly 0, some 1)

**Branches included:**
- CSE (Computer Science Engineering)
- ECE (Electronics and Communication Engineering)
- IT (Information Technology)
- EEE (Electrical and Electronics Engineering)
- MECH (Mechanical Engineering)
- CIVIL (Civil Engineering)
- AERO (Aerospace Engineering)
- BIO (Biotechnology)
- CHEM (Chemical Engineering)
- AUTO (Automobile Engineering)

## Step 2: Import Students into Database

After generating the CSV, import the students into the database:

```bash
python import_students_from_csv.py
```

Or specify a custom CSV file:

```bash
python import_students_from_csv.py your_file.csv
```

**What this does:**
- Creates user accounts for each student
- Sets a default password: `Student@123` (all students have the same password)
- Creates student profiles with all academic data
- Skips duplicate emails if they already exist

**Note:** Students should change their password after first login.

## Step 3: Test the Feature

1. Log in as Admin
2. Go to Admin Panel
3. Post a job with a Job Description
4. The system will:
   - Extract criteria from JD using Gemini
   - Normalize branch names automatically
   - Find matching students
   - Show eligible students

## Branch Name Normalization

The system automatically normalizes branch names from various formats:

**Examples:**
- "Computer Science Engineering" → "CSE"
- "Electronics and Communication" → "ECE"
- "Information Technology" → "IT"
- "Mechanical Engineering" → "MECH"
- "CSE", "CS", "Computer Science" → "CSE"

This works for:
- Student signup (dropdown menu)
- Job Description parsing (Gemini extracts and normalizes)
- Database queries (normalized before matching)

## CSV File Format

The CSV file should have these columns:
- `email` - Student email address
- `roll_number` - Roll number (e.g., 20BCE1234)
- `full_name` - Full name
- `branch` - Branch code (CSE, ECE, IT, etc.)
- `cgpa` - CGPA (0.0 - 10.0)
- `class_10_perc` - Class 10 percentage
- `class_12_perc` - Class 12 percentage
- `backlogs` - Number of active backlogs
- `year_gap` - Year gaps in years

## Customizing the Data

To generate more/fewer students, edit `generate_fake_students.py`:

```python
students = generate_student_data(num_students=200)  # Change 200 to your desired number
```

To change the default password, edit `import_students_from_csv.py`:

```python
import_students_from_csv('fake_students.csv', default_password='YourPassword123')
```

## Troubleshooting

**Error: "File not found"**
- Make sure you run `generate_fake_students.py` first to create the CSV

**Error: "Email already exists"**
- Some students may already be in the database
- The script will skip duplicates and continue

**Students not matching jobs**
- Check that branch names in JD are recognizable
- Verify CGPA, backlogs, and year gap criteria
- Check that students meet all criteria (AND condition)

## Branch Dropdown in Signup

Students now see a dropdown menu with branch options:
- CSE - Computer Science Engineering
- ECE - Electronics and Communication Engineering
- IT - Information Technology
- etc.

This ensures consistent branch codes in the database and prevents typos.

