import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import date as dt_date

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")

VALID_STATUS = {
    "P": "PRESENT",
    "A": "ABSENT",
    "R": "LATE",      # Ritardo
    "G": "EXCUSED"    # Giustificato
}


def _load_db() -> Dict:
    if not os.path.exists(DB_PATH):
        return {"courses": [], "participants": [], "enrollments": [], "attendance": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(db: Dict) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def normalize_date(s: str) -> str:
    s = s.strip()
    if not s:
        return dt_date.today().isoformat()
    # non facciamo parsing complesso: assumiamo YYYY-MM-DD
    return s


@dataclass
class AttendanceRecord:
    course_id: str
    date: str          # YYYY-MM-DD
    participant_id: str
    status: str        # PRESENT/ABSENT/LATE/EXCUSED
    note: str = ""


class AttendanceManager:
    def mark_attendance(self, course_id: str, date: str, participant_id: str, status: str, note: str = "") -> None:
        """Crea o aggiorna il record (course_id, date, participant_id)."""
        db = _load_db()

        # update se esiste
        for r in db["attendance"]:
            if r["course_id"] == course_id and r["date"] == date and r["participant_id"] == participant_id:
                r["status"] = status
                r["note"] = note
                _save_db(db)
                return

        # altrimenti crea
        rec = AttendanceRecord(
            course_id=course_id,
            date=date,
            participant_id=participant_id,
            status=status,
            note=note.strip()
        )
        db["attendance"].append(asdict(rec))
        _save_db(db)

    def get_day_sheet(self, course_id: str, date: str) -> List[AttendanceRecord]:
        db = _load_db()
        out = []
        for r in db["attendance"]:
            if r["course_id"] == course_id and r["date"] == date:
                out.append(AttendanceRecord(**r))
        return out

    def get_record(self, course_id: str, date: str, participant_id: str) -> Optional[AttendanceRecord]:
        db = _load_db()
        for r in db["attendance"]:
            if r["course_id"] == course_id and r["date"] == date and r["participant_id"] == participant_id:
                return AttendanceRecord(**r)
        return None

    def get_participant_history(self, course_id: str, participant_id: str) -> List[AttendanceRecord]:
        db = _load_db()
        out = []
        for r in db["attendance"]:
            if r["course_id"] == course_id and r["participant_id"] == participant_id:
                out.append(AttendanceRecord(**r))
        # ordina per data
        out.sort(key=lambda x: x.date)
        return out

    def take_attendance_for_list(self, course_id: str, date: str, participant_ids: List[str], statuses: Dict[str, str]) -> None:
        """
        statuses: dict participant_id -> status string
        Se un partecipante non è in statuses, default PRESENT.
        """
        for pid in participant_ids:
            status = statuses.get(pid, "PRESENT")
            self.mark_attendance(course_id, date, pid, status, note="")

    def status_from_shortcut(self, shortcut: str) -> Optional[str]:
        s = shortcut.strip().upper()
        return VALID_STATUS.get(s)
