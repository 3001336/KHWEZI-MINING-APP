
import sqlite3
from datetime import datetime

DATABASE = "safety_incidents.db"

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Create the database table
cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_date TEXT NOT NULL,
    incident_time TEXT,
    shift TEXT,
    location TEXT,
    department TEXT,
    incident_type TEXT,
    category TEXT,
    severity TEXT,
    injury_status TEXT,
    lost_time_status TEXT,
    cause TEXT,
    corrective_action TEXT,
    incident_status TEXT,
    likelihood INTEGER,
    consequence INTEGER,
    risk_score INTEGER,
    risk_classification TEXT
)
""")
conn.commit()


def add_incident():
    print("\n--- ADD SAFETY INCIDENT ---")

    incident_date = input("Date (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(incident_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    incident_time = input("Time (HH:MM): ").strip()
    shift = input("Shift: ").strip()
    location = input("Location: ").strip()
    department = input("Department: ").strip()
    incident_type = input("Incident type: ").strip()
    category = input("Category (Injury/Near Miss/Unsafe Act): ").strip()
    severity = input("Incident severity: ").strip()
    injury_status = input("Was anyone injured? (Yes/No): ").strip()
    lost_time_status = input("Lost-time injury? (Yes/No): ").strip()
    cause = input("Cause of incident: ").strip()
    corrective_action = input("Corrective action: ").strip()
    incident_status = input("Status (Open/Under Review/Closed): ").strip()

    try:
        likelihood = int(input("Likelihood (1-5): "))
        consequence = int(input("Consequence (1-5): "))
    except ValueError:
        print("Likelihood and consequence must be whole numbers.")
        return

    if not (1 <= likelihood <= 5 and 1 <= consequence <= 5):
        print("Likelihood and consequence must be between 1 and 5.")
        return

    risk_score, classification = assess_risk(
        likelihood, consequence
    )

    cursor.execute("""
        INSERT INTO incidents (
            incident_date, incident_time, shift, location,
            department, incident_type, category, severity,
            injury_status, lost_time_status, cause,
            corrective_action, incident_status,
            likelihood, consequence, risk_score,
            risk_classification
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?)
    """, (
        incident_date, incident_time, shift, location,
        department, incident_type, category, severity,
        injury_status, lost_time_status, cause,
        corrective_action, incident_status,
        likelihood, consequence, risk_score, classification
    ))

    conn.commit()

    print("\nIncident saved successfully!")
    print("Risk score:", risk_score)
    print("Risk classification:", classification)

    if classification == "High":
        print("WARNING: High risk! Corrective action is required.")
    elif classification == "Critical":
        print("CRITICAL WARNING: Take immediate action to control the risk.")
    elif classification == "Medium":
        print("Notice: Apply suitable risk control measures.")
    else:
        print("Low risk: Continue monitoring the risk.")


def view_incidents():
    cursor.execute("SELECT * FROM incidents ORDER BY id DESC")
    records = cursor.fetchall()

    if not records:
        print("\nNo incidents recorded.")
        return

    for r in records:
        print("\n" + "-" * 45)
        print(f"Incident ID: {r[0]}")
        print(f"Date: {r[1]} | Time: {r[2]}")
        print(f"Shift: {r[3]} | Location: {r[4]}")
        print(f"Department: {r[5]}")
        print(f"Incident type: {r[6]} | Category: {r[7]}")
        print(f"Severity: {r[8]} | Injury: {r[9]}")
        print(f"Lost-time injury: {r[10]}")
        print(f"Cause: {r[11]}")
        print(f"Corrective action: {r[12]}")
        print(f"Incident status: {r[13]}")
        print(f"Likelihood: {r[14]} | Consequence: {r[15]}")
        print(f"Risk score: {r[16]}")
        print(f"Risk classification: {r[17]}")


def search_incidents():
    keyword = input("Search ID, location, department or type: ").strip()

    cursor.execute("""
        SELECT * FROM incidents
        WHERE CAST(id AS TEXT) = ?
           OR location LIKE ?
           OR department LIKE ?
           OR incident_type LIKE ?
    """, (
        keyword,
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    results = cursor.fetchall()

    if results:
        for r in results:
            print("\n", r)
    else:
        print("No matching incidents found.")


def filter_incidents():
    print("\n1. Filter by risk classification")
    print("2. Filter by incident status")
    print("3. Filter by department")

    choice = input("Choose an option: ").strip()

    if choice == "1":
        column = "risk_classification"
        value = input("Risk (Low/Medium/High/Critical): ").strip()
    elif choice == "2":
        column = "incident_status"
        value = input("Status: ").strip()
    elif choice == "3":
        column = "department"
        value = input("Department: ").strip()
    else:
        print("Invalid option.")
        return

    cursor.execute(
        f"SELECT * FROM incidents WHERE LOWER({column}) = LOWER(?)",
        (value,)
    )
    results = cursor.fetchall()

    if results:
        for r in results:
            print("\n", r)
    else:
        print("No matching incidents found.")


def categorize_incidents():
    cursor.execute("""
        SELECT category, COUNT(*)
        FROM incidents
        GROUP BY category
        ORDER BY COUNT(*) DESC
    """)

    print("\n--- INCIDENT CATEGORIES ---")
    for category, total in cursor.fetchall():
        print(f"{category or 'Uncategorized'}: {total}")


def count_incidents():
    cursor.execute("SELECT COUNT(*) FROM incidents")
    print("\nTotal incidents:", cursor.fetchone()[0])

    cursor.execute("""
        SELECT risk_classification, COUNT(*)
        FROM incidents
        GROUP BY risk_classification
    """)

    print("\nIncidents by risk classification:")
    for classification, total in cursor.fetchall():
        print(f"{classification}: {total}")


def analyse_trends():
    cursor.execute("""
        SELECT SUBSTR(incident_date, 1, 7), COUNT(*)
        FROM incidents
        GROUP BY SUBSTR(incident_date, 1, 7)
        ORDER BY SUBSTR(incident_date, 1, 7)
    """)

    results = cursor.fetchall()

    print("\n--- MONTHLY INCIDENT TRENDS ---")
    if not results:
        print("No data available.")
    else:
        for month, total in results:
            print(f"{month}: {total} incident(s)")


def main():
    while True:
        print("\n====== SAFETY INCIDENT SYSTEM ======")
        print("1. Add safety incident")
        print("2. View all incidents")
        print("3. Search incidents")
        print("4. Filter incidents")
        print("5. Categorize incidents")
        print("6. Count incidents")
        print("7. Analyse incident trends")
        print("8. Exit")

        choice = input("Select option (1-8): ").strip()

        if choice == "1":
            add_incident()
        elif choice == "2":
            view_incidents()
        elif choice == "3":
            search_incidents()
        elif choice == "4":
            filter_incidents()
        elif choice == "5":
            categorize_incidents()
        elif choice == "6":
            count_incidents()
        elif choice == "7":
            analyse_trends()
        elif choice == "8":
            print("Closing Safety Incident System.")
            break
        else:
            print("Invalid option. Try again.")


try:
    main()
finally:
    conn.close()
