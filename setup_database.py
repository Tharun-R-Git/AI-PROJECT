"""
Script to populate data.db from data.csv
Run this script once to set up the database for Voice Query Engine and Placement Insights
"""
import sqlite3
import pandas as pd
import os

def setup_placement_database():
    """Creates and populates the companies table in data.db from data.csv"""
    
    db_path = "data.db"
    csv_path = "data.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found!")
        return False
    
    # Read CSV file
    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Rename column to match code expectations (Average_CTC_(LPA) -> Average_CTC_LPA)
    if 'Average_CTC_(LPA)' in df.columns:
        df = df.rename(columns={'Average_CTC_(LPA)': 'Average_CTC_LPA'})
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create companies table
    print("Creating companies table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        Company TEXT,
        Month TEXT,
        Average_CTC_LPA REAL,
        BBS INTEGER,
        BCB INTEGER,
        BCE INTEGER,
        BCI INTEGER,
        BCT INTEGER,
        BDS INTEGER,
        BEC INTEGER,
        BEE INTEGER,
        BIT INTEGER,
        BKT INTEGER
    )
    """)
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    cursor.execute("DELETE FROM companies")
    
    # Insert data from CSV
    print("Inserting data into companies table...")
    df.to_sql('companies', conn, if_exists='append', index=False)
    
    # Commit and close
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM companies")
    count = cursor.fetchone()[0]
    print(f"Successfully inserted {count} records into companies table.")
    
    conn.close()
    print(f"Database setup complete! {db_path} is ready to use.")
    return True

if __name__ == "__main__":
    setup_placement_database()

