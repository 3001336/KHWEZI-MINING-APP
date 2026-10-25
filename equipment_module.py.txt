"""
equipment_module.py
===================

Mining Health, Safety and Equipment Monitoring Application
MINN2020A - Project 2026

PART: Equipment + Maintenance
    * Equipment database
    * Temperature & vibration monitoring
    * Equipment alerts
    * Maintenance monitoring
    * Downtime & availability
    * Maintenance warnings

This file holds ALL the logic (no Streamlit code), so every function can be
tested on its own and re-used by the rest of the group (dashboard, reports).

NOTE: Thresholds are EDUCATIONAL PROTOTYPE values only. They are NOT
manufacturer or mine-safety limits.
"""

from datetime import date, datetime, timedelta
import os
import re

import pandas as pd

# ----------------------------------------------------------------------
# 1. CONFIGURATION
# ----------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "equipment_data.csv")

# (warning_limit, critical_limit)
TEMP_LIMITS = (80.0, 100.0)        # deg C   : <80 normal, 80-100 warning, >100 critical
VIB_LIMITS = (5.0, 8.0)            # mm/s    : <5 normal, 5-8 warning, >8 critical

LOW_AVAILABILITY = 85.0            # % below this = low availability
CRITICAL_AVAILABILITY = 70.0       # % below this = critical
EXCESSIVE_DOWNTIME_PCT = 15.0      # % downtime above this = excessive
DUE_WINDOW_DAYS = 7                # maintenance due within this many days
REPEATED_ALERT_COUNT = 3           # alerts in last 30 days to count as "repeated"

EQUIPMENT_TYPES = ["Haul Truck", "Loader", "Excavator", "Drilling Machine",
                   "Bulldozer", "Scraper Winch", "Crusher", "Conveyor"]
COMPONENT_STATUS = ["Good", "Worn", "Fault", "N/A"]
MAINT_STATUS_OPTIONS = ["Operational", "Under Maintenance"]

REQUIRED_COLUMNS = [
    "equipment_id", "equipment_type", "manufacturer", "operating_hours",
    "downtime_hours", "temperature_c", "vibration_mms", "fuel_lph",
    "brake_status", "tyre_status", "engine_status", "maintenance_status",
    "last_maintenance", "next_maintenance", "alerts_30d", "location",
]

# Roles allowed to open the equipment / maintenance pages (see Table 1)
EQUIPMENT_ROLES = ["Administrator", "Mining Engineer",
                   "Maintenance Engineer", "Manager"]

ID_PATTERN = re.compile(r"^[A-Z]{2,4}-\d{3}$")   # e.g. TRK-012

SEVERITY_RANK = {"CRITICAL": 3, "WARNING": 2, "INFO": 1, "NORMAL": 0}


# ----------------------------------------------------------------------
# 2. ACCESS CONTROL (uses the group's role names)
# ----------------------------------------------------------------------
def can_access_equipment(role):
    """Return True if the role may view equipment & maintenance data."""
    return role in EQUIPMENT_ROLES


def can_edit_equipment(role):
    """Only Administrator, Mining Engineer and Maintenance Engineer may add/edit."""
    return role in ("Administrator", "Mining Engineer", "Maintenance Engineer")


# ----------------------------------------------------------------------
# 3. EQUIPMENT DATABASE (CSV)
# ----------------------------------------------------------------------
def create_sample_data(path=DATA_FILE):
    """Create a realistic sample dataset (24 machines) relative to today."""
    t = date.today()
    d = lambda n: (t + timedelta(days=n)).isoformat()   # day offset helper

    # id, type, maker, op_hrs, down_hrs, temp, vib, fuel, brake, tyre, engine,
    # status, last_maint, next_maint, alerts_30d, location
    rows = [
        ("TRK-001", "Haul Truck", "Caterpillar", 612, 48, 74.5, 3.1, 118, "Good", "Good", "Good", "Operational", d(-40), d(20), 0, "Pit A"),
        ("TRK-002", "Haul Truck", "Komatsu", 580, 80, 88.2, 4.6, 124, "Good", "Worn", "Good", "Operational", d(-55), d(5), 1, "Pit A"),
        ("TRK-007", "Haul Truck", "Caterpillar", 540, 120, 96.0, 6.4, 131, "Worn", "Worn", "Good", "Operational", d(-70), d(-3), 3, "Pit B"),
        ("TRK-012", "Haul Truck", "Komatsu", 455, 205, 104.3, 9.2, 140, "Worn", "Fault", "Worn", "Operational", d(-95), d(-14), 5, "Pit B"),
        ("TRK-015", "Haul Truck", "Hitachi", 630, 30, 71.0, 2.8, 112, "Good", "Good", "Good", "Operational", d(-20), d(40), 0, "Pit A"),
        ("LDR-003", "Loader", "Caterpillar", 590, 70, 79.0, 4.9, 85, "Good", "Good", "Good", "Operational", d(-30), d(30), 0, "Pit A"),
        ("LDR-004", "Loader", "Volvo", 520, 140, 91.5, 5.8, 92, "Good", "Worn", "Worn", "Under Maintenance", d(-60), d(2), 2, "Stockpile"),
        ("LDR-009", "Loader", "Komatsu", 605, 55, 76.4, 3.5, 80, "Good", "Good", "Good", "Operational", d(-25), d(35), 0, "Stockpile"),
        ("EXC-001", "Excavator", "Hitachi", 560, 100, 85.0, 5.2, 150, "Good", "N/A", "Good", "Operational", d(-45), d(4), 1, "Pit A"),
        ("EXC-002", "Excavator", "Liebherr", 498, 170, 101.7, 7.9, 158, "Worn", "N/A", "Worn", "Operational", d(-80), d(-8), 4, "Pit B"),
        ("EXC-005", "Excavator", "Komatsu", 615, 45, 72.8, 2.9, 142, "Good", "N/A", "Good", "Operational", d(-15), d(45), 0, "Pit B"),
        ("DRL-001", "Drilling Machine", "Epiroc", 570, 90, 82.3, 5.5, 60, "Good", "Good", "Good", "Operational", d(-35), d(6), 1, "Bench 3"),
        ("DRL-002", "Drilling Machine", "Sandvik", 500, 160, 94.9, 8.6, 66, "Good", "Worn", "Worn", "Under Maintenance", d(-75), d(-1), 4, "Bench 3"),
        ("DRL-004", "Drilling Machine", "Epiroc", 620, 40, 70.2, 2.5, 55, "Good", "Good", "Good", "Operational", d(-18), d(38), 0, "Bench 1"),
        ("DOZ-001", "Bulldozer", "Caterpillar", 575, 85, 83.6, 4.4, 105, "Good", "N/A", "Good", "Operational", d(-42), d(18), 1, "Pit A"),
        ("DOZ-003", "Bulldozer", "Komatsu", 530, 130, 97.4, 6.9, 110, "Worn", "N/A", "Worn", "Operational", d(-66), d(-5), 3, "Waste Dump"),
        ("SCW-001", "Scraper Winch", "Joy Global", 600, 60, 68.5, 3.3, 0, "Good", "N/A", "Good", "Operational", d(-28), d(32), 0, "Stope 12"),
        ("SCW-002", "Scraper Winch", "Joy Global", 470, 190, 86.1, 7.2, 0, "Fault", "N/A", "Worn", "Operational", d(-90), d(-20), 5, "Stope 14"),
        ("CRS-001", "Crusher", "Metso", 650, 25, 77.9, 4.2, 0, "N/A", "N/A", "Good", "Operational", d(-22), d(25), 0, "Plant"),
        ("CRS-002", "Crusher", "Sandvik", 505, 150, 99.2, 8.4, 0, "N/A", "N/A", "Worn", "Operational", d(-85), d(-10), 4, "Plant"),
        ("CNV-001", "Conveyor", "Siemens", 660, 18, 62.4, 2.2, 0, "N/A", "N/A", "Good", "Operational", d(-12), d(50), 0, "Plant"),
        ("CNV-002", "Conveyor", "Siemens", 585, 75, 81.5, 5.1, 0, "N/A", "N/A", "Good", "Operational", d(-38), d(3), 1, "Shaft 1"),
        ("CNV-003", "Conveyor", "Metso", 545, 115, 90.8, 6.1, 0, "N/A", "N/A", "Worn", "Under Maintenance", d(-58), d(1), 2, "Shaft 1"),
        ("LDR-011", "Loader", "Volvo", 635, 35, 73.1, 3.0, 78, "Good", "Good", "Good", "Operational", d(-10), d(50), 0, "Pit B"),
    ]
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df.to_csv(path, index=False)
    return df


def load_equipment(path=DATA_FILE):
    """Read the equipment CSV and clean it. Creates sample data if file missing."""
    if not os.path.exists(path):
        create_sample_data(path)
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError("Equipment file is missing columns: " + ", ".join(missing))

    # --- cleaning ---
    df = df.drop_duplicates(subset="equipment_id", keep="last").copy()
    df["equipment_id"] = df["equipment_id"].astype(str).str.strip().str.upper()
    for col in ["operating_hours", "downtime_hours", "temperature_c",
                "vibration_mms", "fuel_lph", "alerts_30d"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["equipment_id", "operating_hours", "downtime_hours",
                           "temperature_c", "vibration_mms"])
    df["alerts_30d"] = df["alerts_30d"].fillna(0).astype(int)
    df["fuel_lph"] = df["fuel_lph"].fillna(0)
    for col in ["last_maintenance", "next_maintenance"]:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    # a row with an unreadable maintenance date would crash maintenance_state(),
    # so such rows are removed here (error prevention)
    df = df.dropna(subset=["last_maintenance", "next_maintenance"])
    return df.reset_index(drop=True)


def save_equipment(df, path=DATA_FILE):
    """Write the equipment table back to CSV."""
    df[REQUIRED_COLUMNS].to_csv(path, index=False)


def validate_equipment_input(record, existing_ids):
    """
    Check one new record. Returns a list of error messages
    (empty list = valid). Prevents bad data from crashing the app.
    """
    errors = []
    eid = str(record.get("equipment_id", "")).strip().upper()
    if not eid:
        errors.append("Equipment ID is required.")
    elif not ID_PATTERN.match(eid):
        errors.append("Equipment ID must look like 'TRK-012' (2-4 letters, dash, 3 digits).")
    elif eid in existing_ids:
        errors.append(f"Equipment ID {eid} already exists.")
    if record.get("equipment_type") not in EQUIPMENT_TYPES:
        errors.append("Select a valid equipment type.")
    if not str(record.get("manufacturer", "")).strip():
        errors.append("Manufacturer is required.")

    for key, allowed, label in (("brake_status", COMPONENT_STATUS, "Brake status"),
                                ("tyre_status", COMPONENT_STATUS, "Tyre status"),
                                ("engine_status", COMPONENT_STATUS, "Engine status"),
                                ("maintenance_status", MAINT_STATUS_OPTIONS, "Maintenance status")):
        if record.get(key) not in allowed:
            errors.append(f"{label} must be one of: {', '.join(allowed)}.")

    checks = [("operating_hours", 0, 10000, "Operating hours"),
              ("downtime_hours", 0, 10000, "Downtime hours"),
              ("temperature_c", -20, 300, "Temperature"),
              ("vibration_mms", 0, 100, "Vibration"),
              ("fuel_lph", 0, 1000, "Fuel consumption")]
    for key, lo, hi, label in checks:
        try:
            v = float(record.get(key))
            if v < lo or v > hi:
                errors.append(f"{label} must be between {lo} and {hi}.")
        except (TypeError, ValueError):
            errors.append(f"{label} must be a number.")

    try:
        if float(record.get("operating_hours")) + float(record.get("downtime_hours")) <= 0:
            errors.append("Operating hours + downtime hours must be greater than 0.")
    except (TypeError, ValueError):
        pass

    try:
        if record["next_maintenance"] < record["last_maintenance"]:
            errors.append("Next maintenance date cannot be before the last maintenance date.")
    except Exception:
        errors.append("Maintenance dates are invalid.")
    return errors


def add_equipment(df, record):
    """Append a validated record and return the new DataFrame."""
    record = dict(record)
    record["equipment_id"] = str(record["equipment_id"]).strip().upper()
    return pd.concat([df, pd.DataFrame([record])[REQUIRED_COLUMNS]],
                     ignore_index=True)


def search_equipment(df, text="", eq_type="All", status="All"):
    """Filter the equipment table by free text, type and maintenance state."""
    out = df.copy()
    if eq_type != "All":
        out = out[out["equipment_type"] == eq_type]
    if status != "All":
        out = out[out["maint_state"] == status]
    if text.strip():
        t = text.strip().lower()
        mask = (out["equipment_id"].str.lower().str.contains(t)
                | out["manufacturer"].str.lower().str.contains(t)
                | out["location"].astype(str).str.lower().str.contains(t))
        out = out[mask]
    return out


# ----------------------------------------------------------------------
# 4. DOWNTIME & AVAILABILITY
# ----------------------------------------------------------------------
def calc_availability(operating, downtime):
    """Availability (%) = Operating / (Operating + Downtime) x 100."""
    total = operating + downtime
    if total <= 0:
        return 0.0
    return round(operating / total * 100, 1)


def calc_downtime_pct(operating, downtime):
    """Downtime as a percentage of total scheduled time."""
    total = operating + downtime
    if total <= 0:
        return 0.0
    return round(downtime / total * 100, 1)


# ----------------------------------------------------------------------
# 5. TEMPERATURE & VIBRATION MONITORING
# ----------------------------------------------------------------------
def classify_parameter(value, limits):
    """Return 'NORMAL', 'WARNING' or 'CRITICAL' for a value vs (warn, crit)."""
    warn, crit = limits
    if value > crit:
        return "CRITICAL"
    if value >= warn:
        return "WARNING"
    return "NORMAL"


def condition_message(temp_state, vib_state):
    """Build the status message required by the brief."""
    if "CRITICAL" in (temp_state, vib_state):
        if vib_state == "CRITICAL":
            return "CRITICAL: Equipment vibration exceeds predefined threshold. Inspection required"
        return "CRITICAL: Equipment temperature exceeds predefined threshold. Inspection required"
    if "WARNING" in (temp_state, vib_state):
        if temp_state == "WARNING":
            return "WARNING: Equipment temperature approaching predefined threshold."
        return "WARNING: Equipment vibration approaching predefined threshold."
    return "NORMAL: Equipment operating within defined monitoring limits."


def evaluate_condition(df):
    """Add temp_state, vib_state, condition and condition_msg columns."""
    out = df.copy()
    out["temp_state"] = out["temperature_c"].apply(lambda v: classify_parameter(v, TEMP_LIMITS))
    out["vib_state"] = out["vibration_mms"].apply(lambda v: classify_parameter(v, VIB_LIMITS))
    out["condition"] = out.apply(
        lambda r: max(r["temp_state"], r["vib_state"], key=lambda s: SEVERITY_RANK[s]), axis=1)
    out["condition_msg"] = out.apply(
        lambda r: condition_message(r["temp_state"], r["vib_state"]), axis=1)
    return out


# ----------------------------------------------------------------------
# 6. MAINTENANCE MONITORING
# ----------------------------------------------------------------------
def maintenance_state(row, today=None):
    """
    Decide the maintenance state of one machine:
        Under Maintenance / Overdue / Due Soon / OK
    """
    today = today or date.today()
    if row["maintenance_status"] == "Under Maintenance":
        return "Under Maintenance"
    nxt = row["next_maintenance"]
    if nxt < today:
        return "Overdue"
    if (nxt - today).days <= DUE_WINDOW_DAYS:
        return "Due Soon"
    return "OK"


def evaluate_maintenance(df, today=None):
    """Add availability, downtime %, maintenance state and all flags."""
    today = today or date.today()
    out = df.copy()
    out["availability"] = out.apply(
        lambda r: calc_availability(r["operating_hours"], r["downtime_hours"]), axis=1)
    out["downtime_pct"] = out.apply(
        lambda r: calc_downtime_pct(r["operating_hours"], r["downtime_hours"]), axis=1)
    out["maint_state"] = out.apply(lambda r: maintenance_state(r, today), axis=1)
    out["days_to_maint"] = out["next_maintenance"].apply(lambda d: (d - today).days)

    out["flag_due"] = out["maint_state"] == "Due Soon"
    out["flag_overdue"] = out["maint_state"] == "Overdue"
    out["flag_under_maint"] = out["maint_state"] == "Under Maintenance"
    out["flag_excess_downtime"] = out["downtime_pct"] > EXCESSIVE_DOWNTIME_PCT
    out["flag_repeated_alerts"] = out["alerts_30d"] >= REPEATED_ALERT_COUNT
    out["flag_low_availability"] = out["availability"] < LOW_AVAILABILITY
    return out


def maintenance_priority(row):
    """
    Simple priority score (higher = fix first). Used to rank machines.
    Educational scoring: each problem adds points.
    """
    score = 0
    score += 40 if row["flag_overdue"] else 0
    score += 15 if row["flag_due"] else 0
    score += {"CRITICAL": 30, "WARNING": 12, "NORMAL": 0}[row["condition"]]
    score += 10 if row["flag_excess_downtime"] else 0
    score += 10 if row["flag_low_availability"] else 0
    score += 10 if row["flag_repeated_alerts"] else 0
    score += 10 if "Fault" in (row["brake_status"], row["tyre_status"], row["engine_status"]) else 0
    return score


def maintenance_warnings(row):
    """Return a list of readable maintenance warning strings for one machine."""
    w = []
    if row["flag_overdue"]:
        w.append(f"Maintenance overdue by {abs(row['days_to_maint'])} day(s).")
    if row["flag_due"]:
        w.append(f"Maintenance due in {row['days_to_maint']} day(s).")
    if row["flag_under_maint"]:
        w.append("Equipment currently under maintenance.")
    if row["flag_excess_downtime"]:
        w.append(f"Excessive downtime ({row['downtime_pct']}%).")
    if row["flag_low_availability"]:
        w.append(f"Low availability ({row['availability']}%).")
    if row["flag_repeated_alerts"]:
        w.append(f"Repeated alerts ({row['alerts_30d']} in the last 30 days).")
    return w


def prepare(df, today=None):
    """Run every calculation in one go: condition + maintenance + priority."""
    out = evaluate_maintenance(evaluate_condition(df), today)
    out["priority_score"] = out.apply(maintenance_priority, axis=1)
    out["warnings"] = out.apply(lambda r: " | ".join(maintenance_warnings(r)), axis=1)
    return out


# ----------------------------------------------------------------------
# 7. EQUIPMENT ALERTS
# ----------------------------------------------------------------------
def _alert(row, severity, parameter, value, status, action):
    return {
        "severity": severity,
        "equipment_id": row["equipment_id"],
        "equipment_type": row["equipment_type"],
        "parameter": parameter,
        "value": value,
        "status": status,
        "action": action,
    }


def generate_alerts(df):
    """
    Build the list of alerts for every machine.
    `df` must already be processed with prepare().
    Returns a DataFrame sorted: Critical first.
    """
    alerts = []
    for _, r in df.iterrows():
        # temperature
        if r["temp_state"] == "CRITICAL":
            alerts.append(_alert(r, "CRITICAL", "Temperature", f"{r['temperature_c']} C",
                                 "Above Critical Threshold",
                                 "Inspect equipment and initiate appropriate maintenance/safety procedures."))
        elif r["temp_state"] == "WARNING":
            alerts.append(_alert(r, "WARNING", "Temperature", f"{r['temperature_c']} C",
                                 "Approaching Critical Threshold",
                                 "Monitor closely and check cooling system at next stop."))
        # vibration
        if r["vib_state"] == "CRITICAL":
            alerts.append(_alert(r, "CRITICAL", "Vibration", f"{r['vibration_mms']} mm/s",
                                 "Above Critical Threshold",
                                 "Inspect equipment and initiate appropriate maintenance/safety procedures."))
        elif r["vib_state"] == "WARNING":
            alerts.append(_alert(r, "WARNING", "Vibration", f"{r['vibration_mms']} mm/s",
                                 "Approaching Critical Threshold",
                                 "Monitor closely and schedule a bearing/mounting check."))
        # component faults
        for comp, col in (("Brakes", "brake_status"), ("Tyres", "tyre_status"),
                          ("Engine", "engine_status")):
            if r[col] == "Fault":
                alerts.append(_alert(r, "CRITICAL", comp, "Fault", "Component Fault",
                                     f"Take equipment out of service and repair {comp.lower()}."))
            elif r[col] == "Worn":
                alerts.append(_alert(r, "WARNING", comp, "Worn", "Component Worn",
                                     f"Plan {comp.lower()} replacement/inspection."))
        # downtime & availability
        if r["downtime_pct"] > EXCESSIVE_DOWNTIME_PCT:
            sev = "CRITICAL" if r["availability"] < CRITICAL_AVAILABILITY else "WARNING"
            alerts.append(_alert(r, sev, "Downtime", f"{r['downtime_pct']} %",
                                 "Excessive Downtime",
                                 "Investigate cause of downtime and review maintenance plan."))
        if r["availability"] < LOW_AVAILABILITY:
            sev = "CRITICAL" if r["availability"] < CRITICAL_AVAILABILITY else "WARNING"
            alerts.append(_alert(r, sev, "Availability", f"{r['availability']} %",
                                 "Below Minimum Availability",
                                 "Prioritise equipment for maintenance to restore availability."))
        # maintenance
        if r["flag_overdue"]:
            alerts.append(_alert(r, "CRITICAL", "Maintenance", f"{abs(r['days_to_maint'])} day(s) overdue",
                                 "Maintenance Overdue",
                                 "Schedule maintenance immediately."))
        elif r["flag_due"]:
            alerts.append(_alert(r, "WARNING", "Maintenance", f"due in {r['days_to_maint']} day(s)",
                                 "Maintenance Due Soon",
                                 "Book a maintenance slot."))
        # repeated alerts
        if r["flag_repeated_alerts"]:
            alerts.append(_alert(r, "WARNING", "Repeated Alerts", f"{r['alerts_30d']} in 30 days",
                                 "Recurring Problem",
                                 "Carry out root-cause investigation."))

    cols = ["severity", "equipment_id", "equipment_type", "parameter",
            "value", "status", "action"]
    out = pd.DataFrame(alerts, columns=cols)
    if not out.empty:
        out["_r"] = out["severity"].map(SEVERITY_RANK)
        out = out.sort_values(["_r", "equipment_id"], ascending=[False, True]).drop(columns="_r")
    return out.reset_index(drop=True)


def format_alert(alert):
    """Return one alert as text in the layout of Figure 1 in the brief."""
    bar = "=" * 53
    return (f"{bar}\nMINING MONITORING ALERT\n{bar}\n"
            f"[{alert['severity']}]\n"
            f"Equipment ID: {alert['equipment_id']}\n"
            f"Parameter: {alert['parameter']}\n"
            f"Value: {alert['value']}\n"
            f"Status: {alert['status']}\n"
            f"Recommended Action:\n {alert['action']}\n{bar}")


# ----------------------------------------------------------------------
# 8. KPI SUMMARY (can be re-used by the main dashboard)
# ----------------------------------------------------------------------
def equipment_kpis(df, alerts):
    """Return a dict of equipment KPIs for the group dashboard."""
    total = len(df)
    critical_alerts = int((alerts["severity"] == "CRITICAL").sum()) if len(alerts) else 0
    return {
        "total_equipment": total,
        "equipment_available": int((df["maint_state"] != "Under Maintenance").sum()),
        "under_maintenance": int(df["flag_under_maint"].sum()),
        "overdue": int(df["flag_overdue"].sum()),
        "total_alerts": len(alerts),
        "critical_alerts": critical_alerts,
        "avg_availability": float(round(df["availability"].mean(), 1)) if total else 0.0,
        "pct_normal": float(round((df["condition"] == "NORMAL").sum() / total * 100, 1)) if total else 0.0,
    }


# ----------------------------------------------------------------------
# 9. INTERACTIVE DATA ANALYSIS (Appendix A - Equipment questions)
# ----------------------------------------------------------------------
def answer_question(question, df, alerts):
    """
    Answer one of the Appendix A equipment questions.
    Returns (text_answer, table_or_None).
    """
    if question == "Which equipment has the highest downtime?":
        r = df.loc[df["downtime_hours"].idxmax()]
        return f"{r['equipment_id']} ({r['equipment_type']}) with {r['downtime_hours']} downtime hours.", \
            df.nlargest(5, "downtime_hours")[["equipment_id", "equipment_type", "downtime_hours", "downtime_pct"]]

    if question == "Which equipment has the lowest availability?":
        r = df.loc[df["availability"].idxmin()]
        return f"{r['equipment_id']} ({r['equipment_type']}) with {r['availability']}% availability.", \
            df.nsmallest(5, "availability")[["equipment_id", "equipment_type", "availability"]]

    if question == "Which equipment has the highest vibration?":
        r = df.loc[df["vibration_mms"].idxmax()]
        return f"{r['equipment_id']} ({r['equipment_type']}) at {r['vibration_mms']} mm/s.", \
            df.nlargest(5, "vibration_mms")[["equipment_id", "equipment_type", "vibration_mms", "vib_state"]]

    if question == "Which equipment has the highest operating temperature?":
        r = df.loc[df["temperature_c"].idxmax()]
        return f"{r['equipment_id']} ({r['equipment_type']}) at {r['temperature_c']} C.", \
            df.nlargest(5, "temperature_c")[["equipment_id", "equipment_type", "temperature_c", "temp_state"]]

    if question == "Which equipment has generated the most alerts?":
        if alerts.empty:
            return "No alerts have been generated.", None
        counts = alerts.groupby("equipment_id").size().reset_index(name="alerts").sort_values("alerts", ascending=False)
        top = counts.iloc[0]
        return f"{top['equipment_id']} generated the most alerts ({top['alerts']}).", counts.head(5)

    if question == "Which equipment requires maintenance?":
        sub = df[df["flag_due"] | df["flag_overdue"] | df["flag_under_maint"]]
        return f"{len(sub)} machine(s) are due, overdue or under maintenance.", \
            sub[["equipment_id", "equipment_type", "maint_state", "days_to_maint"]]

    if question == "Which equipment is overdue for maintenance?":
        sub = df[df["flag_overdue"]].sort_values("days_to_maint")
        return f"{len(sub)} machine(s) are overdue for maintenance.", \
            sub[["equipment_id", "equipment_type", "next_maintenance", "days_to_maint"]]

    if question == "What is the average equipment availability?":
        return f"The average equipment availability is {df['availability'].mean():.1f}%.", None

    if question == "Which equipment type has the highest downtime?":
        g = df.groupby("equipment_type")["downtime_hours"].sum().reset_index().sort_values("downtime_hours", ascending=False)
        return f"{g.iloc[0]['equipment_type']} has the highest total downtime ({g.iloc[0]['downtime_hours']:.0f} hours).", g

    if question == "Which equipment requires immediate inspection?":
        sub = df[df["condition"] == "CRITICAL"].sort_values("priority_score", ascending=False)
        return f"{len(sub)} machine(s) have critical temperature or vibration readings.", \
            sub[["equipment_id", "equipment_type", "temperature_c", "vibration_mms", "condition_msg"]]

    if question == "Which equipment should receive maintenance priority?":
        sub = df.sort_values("priority_score", ascending=False).head(5)
        return f"Highest priority: {sub.iloc[0]['equipment_id']} (score {sub.iloc[0]['priority_score']}).", \
            sub[["equipment_id", "equipment_type", "priority_score", "warnings"]]

    if question == "What percentage of monitored equipment is operating normally?":
        pct = (df["condition"] == "NORMAL").mean() * 100
        return f"{pct:.1f}% of monitored equipment is operating within normal limits.", None

    if question == "How many critical alerts are currently active?":
        n = int((alerts["severity"] == "CRITICAL").sum()) if len(alerts) else 0
        return f"There are {n} critical alert(s) active.", \
            alerts[alerts["severity"] == "CRITICAL"].head(15) if n else None

    return "Question not recognised.", None


ANALYSIS_QUESTIONS = [
    "Which equipment has the highest downtime?",
    "Which equipment has the lowest availability?",
    "Which equipment has the highest vibration?",
    "Which equipment has the highest operating temperature?",
    "Which equipment has generated the most alerts?",
    "Which equipment requires maintenance?",
    "Which equipment is overdue for maintenance?",
    "What is the average equipment availability?",
    "Which equipment type has the highest downtime?",
    "Which equipment requires immediate inspection?",
    "Which equipment should receive maintenance priority?",
    "What percentage of monitored equipment is operating normally?",
    "How many critical alerts are currently active?",
]


def generate_recommendations(df, alerts):
    """Plain-language recommendations from the monitoring results."""
    recs = []
    crit = df[df["condition"] == "CRITICAL"]
    if len(crit):
        recs.append(f"Inspect immediately: {', '.join(crit['equipment_id'])} (critical temperature/vibration).")
    ov = df[df["flag_overdue"]]
    if len(ov):
        recs.append(f"Schedule overdue maintenance: {', '.join(ov['equipment_id'])}.")
    low = df[df["flag_low_availability"]]
    if len(low):
        recs.append(f"Review availability of: {', '.join(low['equipment_id'])}.")
    rep = df[df["flag_repeated_alerts"]]
    if len(rep):
        recs.append(f"Investigate root causes for recurring alerts on: {', '.join(rep['equipment_id'])}.")
    if not recs:
        recs.append("All equipment is within monitoring limits. Continue routine monitoring.")
    return recs


if __name__ == "__main__":
    # Quick console test
    data = prepare(load_equipment())
    al = generate_alerts(data)
    print(equipment_kpis(data, al))
    print(format_alert(al.iloc[0]))
