from partecipanti import CourseManager, ParticipantManager, EnrollmentManager
from registro_presenze import AttendanceManager, normalize_date

def pause():
    input("\nPremi INVIO per continuare...")


def choose_from_list(items, label_fn):
    if not items:
        return None
    for i, it in enumerate(items, start=1):
        print(f"{i}) {label_fn(it)}")
    while True:
        choice = input("Seleziona numero (o INVIO per annullare): ").strip()
        if choice == "":
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(items):
                return items[idx - 1]
        print("Scelta non valida.")


def menu_courses(cm: CourseManager):
    while True:
        print("\n=== CORSI ===")
        print("1) Lista corsi")
        print("2) Crea corso")
        print("0) Indietro")
        c = input("Scelta: ").strip()

        if c == "1":
            courses = cm.list_courses()
            if not courses:
                print("Nessun corso.")
            else:
                for co in courses:
                    print(f"- {co.id}: {co.name} ({co.description})")
            pause()
