"""Self-tests.  Run with:  python test_equipment_module.py   (or: pytest)"""
import os
import tempfile
import warnings
from datetime import date, timedelta

import pandas as pd

import equipment_module as em


def _good_record(**changes):
    rec = dict(equipment_id="TRK-099", equipment_type="Haul Truck",
               manufacturer="Test", operating_hours=500, downtime_hours=50,
               temperature_c=70, vibration_mms=3, fuel_lph=100,
               brake_status="Good", tyre_status="Good", engine_status="Good",
               maintenance_status="Operational",
               last_maintenance=date(2026, 9, 1), next_maintenance=date(2026, 12, 1),
               alerts_30d=0, location="Pit A")
    rec.update(changes)
    return rec


def test_temperature_and_vibration_boundaries_follow_brief():
    assert [em.classify_parameter(v, em.TEMP_LIMITS) for v in (79.9, 80, 100, 100.1)] == \
        ["NORMAL", "WARNING", "WARNING", "CRITICAL"]
    assert [em.classify_parameter(v, em.VIB_LIMITS) for v in (4.9, 5, 8, 8.1)] == \
        ["NORMAL", "WARNING", "WARNING", "CRITICAL"]


def test_availability_formula_and_zero_time():
    assert em.calc_availability(900, 100) == 90.0
    assert em.calc_availability(0, 0) == 0.0
    assert em.calc_downtime_pct(900, 100) == 10.0


def test_maintenance_state_rules():
    today = date(2026, 10, 11)
    base = {"maintenance_status": "Operational"}
    assert em.maintenance_state({**base, "next_maintenance": today - timedelta(days=1)}, today) == "Overdue"
    assert em.maintenance_state({**base, "next_maintenance": today + timedelta(days=7)}, today) == "Due Soon"
    assert em.maintenance_state({**base, "next_maintenance": today + timedelta(days=8)}, today) == "OK"
    assert em.maintenance_state({"maintenance_status": "Under Maintenance",
                                 "next_maintenance": today + timedelta(days=90)}, today) == "Under Maintenance"


def test_validation_accepts_good_and_rejects_bad_records():
    assert em.validate_equipment_input(_good_record(), []) == []
    assert em.validate_equipment_input(_good_record(equipment_id="bad id"), [])
    assert em.validate_equipment_input(_good_record(temperature_c="hot"), [])
    assert em.validate_equipment_input(_good_record(brake_status="Broken"), [])
    assert em.validate_equipment_input(_good_record(), ["TRK-099"])           # duplicate
    assert em.validate_equipment_input(_good_record(next_maintenance=date(2026, 1, 1)), [])


def test_add_save_and_reload_round_trip():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "eq.csv")
        table = em.load_equipment(path)                    # creates sample data
        before = len(table)
        table = em.add_equipment(table, _good_record())
        em.save_equipment(table, path)
        assert len(em.load_equipment(path)) == before + 1


def test_unreadable_dates_do_not_crash_the_app():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "eq.csv")
        em.create_sample_data(path)
        raw = pd.read_csv(path)
        raw.loc[0, "next_maintenance"] = "not a date"
        raw.to_csv(path, index=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")            # pandas notes the bad date
            data = em.prepare(em.load_equipment(path))     # must not raise
        assert len(data) == len(raw) - 1


def test_alerts_and_figure_1_format():
    data = em.prepare(em.load_equipment())
    alerts = em.generate_alerts(data)
    assert alerts.iloc[0]["severity"] == "CRITICAL"
    box = em.format_alert(alerts.iloc[0])
    assert "MINING MONITORING ALERT" in box and "Recommended Action:" in box


def test_role_access_matches_table_1():
    assert not em.can_access_equipment("Safety Officer")
    assert all(em.can_access_equipment(r) for r in
               ("Administrator", "Mining Engineer", "Maintenance Engineer", "Manager"))
    assert not em.can_edit_equipment("Manager")


def test_every_analysis_question_has_an_answer():
    data = em.prepare(em.load_equipment())
    alerts = em.generate_alerts(data)
    for q in em.ANALYSIS_QUESTIONS:
        text, _ = em.answer_question(q, data, alerts)
        assert text and text != "Question not recognised."
    assert em.generate_recommendations(data, alerts)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
