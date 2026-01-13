import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")


def _load_db() -> Dict:
    if not os.path.exists(DB_PATH):
        return {"courses": [], "participants": [], "enrollments": [], "attendance": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_db(db: Dict) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def _next_id(prefix: str, items: List[Dict], key: str = "id") -> str:
    # Genera ID tipo C1, C2... oppure P1, P2...
    max_n = 0
    for it in items:
        _id = str(it.get(key, ""))
        if _id.startswith(prefix):
            try:
                n = int(_id[len(prefix):])
                max_n = max(max_n, n)
            except ValueError:
                pass
    return f"{prefix}{max_n + 1}"


@dataclass
class Course:
    id: str
    name: str
    description: str = ""


@dataclass
class Participant:
    id: str
    first_name: str
    last_name: str
    email: str = ""


class CourseManager:
    def list_courses(self) -> List[Course]:
        db = _load_db()
        return [Course(**c) for c in db["courses"]]

    def add_course(self, name: str, description: str = "") -> Course:
        db = _load_db()
        new_id = _next_id("C", db["courses"])
        course = Course(id=new_id, name=name.strip(), description=description.strip())
        db["courses"].append(asdict(course))
        _save_db(db)
        return course

    def get_course(self, course_id: str) -> Optional[Course]:
        db = _load_db()
        for c in db["courses"]:
            if c["id"] == course_id:
                return Course(**c)
        return None


class ParticipantManager:
    def list_participants(self) -> List[Participant]:
        db = _load_db()
        return [Participant(**p) for p in db["participants"]]

    def add_participant(self, first_name: str, last_name: str, email: str = "") -> Participant:
        db = _load_db()
        new_id = _next_id("P", db["participants"])
        p = Participant(
            id=new_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip()
        )
        db["participants"].append(asdict(p))
        _save_db(db)
        return p

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        db = _load_db()
        for p in db["participants"]:
            if p["id"] == participant_id:
                return Participant(**p)
        return None


class EnrollmentManager:
    def enroll(self, course_id: str, participant_id: str) -> bool:
        """Ritorna True se iscrizione aggiunta, False se già presente."""
        db = _load_db()

        exists = any(
            e["course_id"] == course_id and e["participant_id"] == participant_id
            for e in db["enrollments"]
        )
        if exists:
            return False

        db["enrollments"].append({"course_id": course_id, "participant_id": participant_id})
        _save_db(db)
        return True

    def list_enrolled(self, course_id: str) -> List[str]:
        """Ritorna lista di participant_id iscritti al corso."""
        db = _load_db()
        return [e["participant_id"] for e in db["enrollments"] if e["course_id"] == course_id]

    def remove_enrollment(self, course_id: str, participant_id: str) -> bool:
        db = _load_db()
        before = len(db["enrollments"])
        db["enrollments"] = [
            e for e in db["enrollments"]
            if not (e["course_id"] == course_id and e["participant_id"] == participant_id)
        ]
        after = len(db["enrollments"])
        if after != before:
            _save_db(db)
            return True
        return False