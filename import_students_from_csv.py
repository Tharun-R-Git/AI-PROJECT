"""
Script to import student data from CSV file into the database
This creates user accounts and student profiles from the CSV data
"""
import csv
import sys
from modules import database, auth

def import_students_from_csv(csv_filename='fake_students.csv', default_password='Student@123'):
    """
    Import students from CSV file into the database.
    All students will have the same default password (they should change it later).
    """
    students_imported = 0
    students_skipped = 0
    errors = []
    
    try:
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                try:
                    email = row['email'].strip()
                    roll_number = row['roll_number'].strip()
                    full_name = row['full_name'].strip()
                    branch = row['branch'].strip()
                    cgpa = float(row['cgpa'])
                    class_10_perc = float(row['class_10_perc'])
                    class_12_perc = float(row['class_12_perc'])
                    backlogs = int(row['backlogs'])
                    year_gap = int(row['year_gap'])
                    
                    # Hash the default password
                    hashed_password = auth.hash_password(default_password)
                    
                    # Prepare profile data
                    profile_data = {
                        'roll_number': roll_number,
                        'full_name': full_name,
                        'cgpa': cgpa,
                        'branch': branch,
                        'class_10_perc': class_10_perc,
                        'class_12_perc': class_12_perc,
                        'backlogs': backlogs,
                        'year_gap': year_gap
                    }
                    
                    # Add user and profile
                    success, message = database.add_user_and_profile(
                        email, hashed_password, 'student', profile_data
                    )
                    
                    if success:
                        students_imported += 1
                        if students_imported % 10 == 0:
                            print(f"  Imported {students_imported} students...")
                    else:
                        students_skipped += 1
                        errors.append(f"Row {row_num} ({email}): {message}")
                
                except KeyError as e:
                    errors.append(f"Row {row_num}: Missing column - {e}")
                    students_skipped += 1
                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid data format - {e}")
                    students_skipped += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: Unexpected error - {e}")
                    students_skipped += 1
        
        print(f"\nImport complete!")
        print(f"   Successfully imported: {students_imported} students")
        print(f"   Skipped/Failed: {students_skipped} students")
        
        if errors:
            print(f"\nErrors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"   {error}")
            if len(errors) > 10:
                print(f"   ... and {len(errors) - 10} more errors")
        
        print(f"\nDefault password for all imported students: {default_password}")
        print(f"   (Students should change this after first login)")
        
        return students_imported, students_skipped
    
    except FileNotFoundError:
        print(f"Error: File '{csv_filename}' not found!")
        print(f"   Please run 'python generate_fake_students.py' first to create the CSV file.")
        return 0, 0
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return 0, 0

if __name__ == "__main__":
    print("=" * 60)
    print("Student Data Import Tool")
    print("=" * 60)
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'fake_students.csv'
    print(f"\nImporting students from: {csv_file}")
    print("This will create user accounts and student profiles...\n")
    
    imported, skipped = import_students_from_csv(csv_file)
    
    if imported > 0:
        print(f"\nSuccessfully imported {imported} students into the database!")
        print("   You can now test the Admin Panel job matching feature.")

