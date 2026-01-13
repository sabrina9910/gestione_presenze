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

        elif c == "2":
            name = input("Nome corso: ").strip()
            desc = input("Descrizione (opzionale): ").strip()
            if not name:
                print("Nome obbligatorio.")
            else:
                course = cm.add_course(name, desc)
                print(f"Creato corso {course.id}")
            pause()

        elif c == "0":
            return
        else:
            print("Scelta non valida.")


def menu_participants(pm: ParticipantManager):
    while True:
        print("\n=== PARTECIPANTI ===")
        print("1) Lista partecipanti")
        print("2) Crea partecipante")
        print("0) Indietro")
        c = input("Scelta: ").strip()

        if c == "1":
            ps = pm.list_participants()
            if not ps:
                print("Nessun partecipante.")
            else:
                for p in ps:
                    email = f" <{p.email}>" if p.email else ""
                    print(f"- {p.id}: {p.first_name} {p.last_name}{email}")
            pause()

        elif c == "2":
            fn = input("Nome: ").strip()
            ln = input("Cognome: ").strip()
            em = input("Email (opzionale): ").strip()
            if not fn or not ln:
                print("Nome e cognome obbligatori.")
            else:
                p = pm.add_participant(fn, ln, em)
                print(f"Creato partecipante {p.id}")
            pause()

        elif c == "0":
            return
        else:
            print("Scelta non valida.")


def menu_enrollments(cm: CourseManager, pm: ParticipantManager, em: EnrollmentManager):
    while True:
        print("\n=== ISCRIZIONI ===")
        print("1) Iscrivi partecipante a corso")
        print("2) Lista iscritti di un corso")
        print("3) Rimuovi iscrizione")
        print("0) Indietro")
        c = input("Scelta: ").strip()

        if c == "1":
            courses = cm.list_courses()
            course = choose_from_list(courses, lambda x: f"{x.id} - {x.name}")
            if not course:
                continue

            participants = pm.list_participants()
            participant = choose_from_list(participants, lambda x: f"{x.id} - {x.first_name} {x.last_name}")
            if not participant:
                continue

            added = em.enroll(course.id, participant.id)
            print("Iscrizione aggiunta." if added else "Era già iscritto.")
            pause()

        elif c == "2":
            courses = cm.list_courses()
            course = choose_from_list(courses, lambda x: f"{x.id} - {x.name}")
            if not course:
                continue

            enrolled_ids = em.list_enrolled(course.id)
            if not enrolled_ids:
                print("Nessun iscritto.")
            else:
                all_p = {p.id: p for p in pm.list_participants()}
                print(f"Iscritti a {course.name}:")
                for pid in enrolled_ids:
                    p = all_p.get(pid)
                    if p:
                        print(f"- {p.id}: {p.first_name} {p.last_name}")
                    else:
                        print(f"- {pid}: (partecipante non trovato)")
            pause()

        elif c == "3":
            courses = cm.list_courses()
            course = choose_from_list(courses, lambda x: f"{x.id} - {x.name}")
            if not course:
                continue

            enrolled_ids = em.list_enrolled(course.id)
            if not enrolled_ids:
                print("Nessun iscritto.")
                pause()
                continue

            all_p = {p.id: p for p in pm.list_participants()}
            enrolled_participants = [all_p[pid] for pid in enrolled_ids if pid in all_p]

            participant = choose_from_list(enrolled_participants, lambda x: f"{x.id} - {x.first_name} {x.last_name}")
            if not participant:
                continue

            removed = em.remove_enrollment(course.id, participant.id)
            print("Iscrizione rimossa." if removed else "Non trovata.")
            pause()

        elif c == "0":
            return
        else:
            print("Scelta non valida.")


def menu_attendance(cm: CourseManager, pm: ParticipantManager, em: EnrollmentManager, am: AttendanceManager):
    while True:
        print("\n=== PRESENZE ===")
        print("1) Registra presenze (giornata)")
        print("2) Visualizza presenze (giornata)")
        print("3) Modifica presenza singola")
        print("4) Storico partecipante (per corso)")
        print("0) Indietro")
        c = input("Scelta: ").strip()

        if c == "1":
            course = choose_from_list(cm.list_courses(), lambda x: f"{x.id} - {x.name}")
            if not course:
                continue

            d = normalize_date(input("Data (YYYY-MM-DD, INVIO=oggi): "))
            enrolled_ids = em.list_enrolled(course.id)
            if not enrolled_ids:
                print("Nessun iscritto al corso.")
                pause()
                continue

            all_p = {p.id: p for p in pm.list_participants()}

            print("\nInserisci stato per ciascuno: P=Presente, A=Assente, R=Ritardo, G=Giustificato")
            statuses = {}
            for pid in enrolled_ids:
                p = all_p.get(pid)
                if not p:
                    continue
                while True:
                    s = input(f"{p.first_name} {p.last_name} [{pid}] (default P): ").strip().upper()
                    if s == "":
                        statuses[pid] = "PRESENT"
                        break
                    full = am.status_from_shortcut(s)
                    if full:
                        statuses[pid] = full
                        break
                    print("Valore non valido (usa P/A/R/G o INVIO).")

            am.take_attendance_for_list(course.id, d, enrolled_ids, statuses)
            print(f"Presenze salvate per {course.name} in data {d}.")
            pause()

        elif c == "2":
            course = choose_from_list(cm.list_courses(), lambda x: f"{x.id} - {x.name}")
            if not course:
                continue
            d = normalize_date(input("Data (YYYY-MM-DD): "))
            sheet = am.get_day_sheet(course.id, d)
            if not sheet:
                print("Nessun record trovato per quella giornata.")
                pause()
                continue

            all_p = {p.id: p for p in pm.list_participants()}
            print(f"\nRegistro {course.name} - {d}")
            for r in sheet:
                p = all_p.get(r.participant_id)
                name = f"{p.first_name} {p.last_name}" if p else r.participant_id
                note = f" | note: {r.note}" if r.note else ""
                print(f"- {name}: {r.status}{note}")
            pause()

        elif c == "3":
            course = choose_from_list(cm.list_courses(), lambda x: f"{x.id} - {x.name}")
            if not course:
                continue
            d = normalize_date(input("Data (YYYY-MM-DD): "))

            enrolled_ids = em.list_enrolled(course.id)
            all_p = {p.id: p for p in pm.list_participants()}
            enrolled_participants = [all_p[pid] for pid in enrolled_ids if pid in all_p]
            if not enrolled_participants:
                print("Nessun iscritto trovato.")
                pause()
                continue

            participant = choose_from_list(enrolled_participants, lambda x: f"{x.id} - {x.first_name} {x.last_name}")
            if not participant:
                continue

            current = am.get_record(course.id, d, participant.id)
            if current:
                print(f"Stato attuale: {current.status} (note: {current.note})")
            else:
                print("Record non presente: verrà creato.")

            while True:
                s = input("Nuovo stato (P/A/R/G): ").strip().upper()
                full = am.status_from_shortcut(s)
                if full:
                    break
                print("Valore non valido.")

            note = input("Note (opzionale): ").strip()
            am.mark_attendance(course.id, d, participant.id, full, note)
            print("Aggiornato.")
            pause()

        elif c == "4":
            course = choose_from_list(cm.list_courses(), lambda x: f"{x.id} - {x.name}")
            if not course:
                continue

            enrolled_ids = em.list_enrolled(course.id)
            all_p = {p.id: p for p in pm.list_participants()}
            enrolled_participants = [all_p[pid] for pid in enrolled_ids if pid in all_p]
            if not enrolled_participants:
                print("Nessun iscritto trovato.")
                pause()
                continue

            participant = choose_from_list(enrolled_participants, lambda x: f"{x.id} - {x.first_name} {x.last_name}")
            if not participant:
                continue

            history = am.get_participant_history(course.id, participant.id)
            if not history:
                print("Nessun record presenze per questo partecipante.")
                pause()
                continue

            print(f"\nStorico presenze - {course.name} - {participant.first_name} {participant.last_name}")
            for r in history:
                note = f" | note: {r.note}" if r.note else ""
                print(f"- {r.date}: {r.status}{note}")
            pause()

        elif c == "0":
            return
        else:
            print("Scelta non valida.")


def main():
    cm = CourseManager()
    pm = ParticipantManager()
    em = EnrollmentManager()
    am = AttendanceManager()

    while True:
        print("\n===== GESTIONE PRESENZE (CLI) =====")
        print("1) Gestione corsi")
        print("2) Gestione partecipanti")
        print("3) Iscrizioni (partecipanti ↔ corsi)")
        print("4) Presenze")
        print("0) Esci")

        choice = input("Scelta: ").strip()
        if choice == "1":
            menu_courses(cm)
        elif choice == "2":
            menu_participants(pm)
        elif choice == "3":
            menu_enrollments(cm, pm, em)
        elif choice == "4":
            menu_attendance(cm, pm, em, am)
        elif choice == "0":
            print("Ciao!")
            break
        else:
            print("Scelta non valida.")


if __name__ == "_main_":
    main()