# Testing Job Matching Feature

## Overview
This guide explains how to test that jobs posted by admins appear in student dashboards.

## How It Works

1. **Admin posts a job** → System extracts criteria from JD using Gemini
2. **System finds eligible students** → Matches based on CGPA, Branch, Backlogs, Year Gap
3. **System saves job and eligibility** → Creates entries in `eligibility` table
4. **Student logs in** → Student Dashboard queries `eligibility` table
5. **Jobs appear** → Student sees all jobs they're eligible for

## Testing Steps

### Step 1: Import Test Students
```bash
python import_students_from_csv.py
```
This creates 150 test students with default password: `Student@123`

### Step 2: Log in as Admin
1. Go to Home page
2. Sign up/Login as Admin
3. Navigate to Admin Panel

### Step 3: Post a Test Job
1. Enter Company Name: e.g., "Google"
2. Paste a Job Description like:
   ```
   We are looking for Software Engineers.
   Requirements:
   - Minimum CGPA: 7.5
   - Branches: Computer Science Engineering, Electronics and Communication Engineering
   - No active backlogs
   - Maximum 1 year gap allowed
   ```
3. Click "Extract Criteria & Find Eligible Students"
4. Review the extracted criteria and eligible students list
5. Click "Confirm and Post Job"

### Step 4: Log in as a Student
1. Logout from Admin account
2. Login as one of the eligible students
   - Email: Check `fake_students.csv` for student emails
   - Password: `Student@123`
3. Navigate to Student Dashboard

### Step 5: Verify Jobs Appear
- You should see the job you posted in the Student Dashboard
- The job should show:
  - Company name
  - Full job description
  - Eligibility criteria (CGPA, Branches, Backlogs, Year Gap)

## Expected Behavior

✅ **If student matches criteria:**
- Job appears in their dashboard immediately
- Shows all job details and criteria
- Multiple jobs can appear if multiple jobs match

❌ **If student doesn't match:**
- Dashboard shows: "No jobs have been posted for you yet"
- Job won't appear even if admin posted it

## Database Verification

You can verify the data is stored correctly:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('placement_users.db')

# Check jobs table
jobs_df = pd.read_sql_query("SELECT * FROM jobs", conn)
print("Jobs:", len(jobs_df))
print(jobs_df)

# Check eligibility table
eligibility_df = pd.read_sql_query("SELECT * FROM eligibility", conn)
print("\nEligibility mappings:", len(eligibility_df))
print(eligibility_df)

# Check specific student's jobs
student_email = "your_student_email@vit.ac.in"
student_jobs = pd.read_sql_query("""
    SELECT j.company_name, e.student_email
    FROM jobs j
    JOIN eligibility e ON j.job_id = e.job_id
    WHERE e.student_email = ?
""", conn, params=(student_email,))
print(f"\nJobs for {student_email}:")
print(student_jobs)

conn.close()
```

## Troubleshooting

### Jobs not appearing for students

1. **Check eligibility table:**
   - Verify entries exist in `eligibility` table
   - Check that `student_email` matches exactly

2. **Check student profile:**
   - Verify student has a profile in `student_profiles` table
   - Check branch code matches (should be normalized like "CSE", "ECE")

3. **Check criteria matching:**
   - Verify student's CGPA >= required CGPA
   - Verify student's branch is in eligible branches list
   - Verify student's backlogs <= max allowed
   - Verify student's year_gap <= max allowed

4. **Check database query:**
   - The query uses JOIN between `jobs` and `eligibility` tables
   - Filters by `student_email` from session state

### Common Issues

**Issue:** Student sees "No jobs" but admin posted job
- **Solution:** Check if student's profile matches all criteria (AND condition)
- All criteria must be met: CGPA, Branch, Backlogs, Year Gap

**Issue:** Branch not matching
- **Solution:** Check branch normalization
- JD might say "Computer Science" but student has "CSE"
- System should normalize automatically, but verify in criteria JSON

**Issue:** Jobs appear for wrong students
- **Solution:** Check eligibility table entries
- Verify `student_email` in eligibility table matches actual student emails

## Test Cases

### Test Case 1: Single Student Match
- Post job requiring: CGPA >= 8.0, Branch: CSE
- Import students with various CGPA and branches
- Verify only CSE students with CGPA >= 8.0 see the job

### Test Case 2: Multiple Students Match
- Post job requiring: CGPA >= 7.0, Branches: CSE, ECE
- Verify all CSE and ECE students with CGPA >= 7.0 see the job

### Test Case 3: No Students Match
- Post job requiring: CGPA >= 9.5
- If no students have CGPA >= 9.5, verify admin sees "No students match"
- Verify no eligibility entries are created

### Test Case 4: Backlog Filter
- Post job requiring: Backlogs <= 0
- Verify only students with 0 backlogs see the job
- Students with 1+ backlogs should not see it

### Test Case 5: Year Gap Filter
- Post job requiring: Year Gap <= 1
- Verify students with 0 or 1 year gap see the job
- Students with 2+ year gap should not see it

## Notes

- Jobs are linked to students via the `eligibility` table
- The relationship is many-to-many (one job can match many students, one student can match many jobs)
- Jobs appear in order: newest first (ORDER BY j.job_id DESC)
- Student Dashboard refreshes on page load (or click Refresh button)

