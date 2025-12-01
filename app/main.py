# app/main.py
#Simple CLI to demonstrate CRUD functions required by the assignment

import sys
from tabulate import tabulate

from db import (
    get_all_members,
    register_member,
    update_member_profile,
    add_health_metric,
    list_fitness_goals,
    update_goal,
    get_member_dashboard,
    list_scheduled_classes,
    register_for_class,
    list_member_registrations,
    add_trainer_availability,
    list_trainer_availability,
    list_trainer_schedule,
    create_scheduled_class,
)

def usage():
    print(
        "Usage:\n"
        "  python3 app/main.py members\n"
        "  python3 app/main.py add-member <full_name> <dob|None> <phone|None> <email>\n"
        "  python3 app/main.py update-member <mid> <full_name|None> <dob|None> <phone|None> <email|None>\n"
        "  python3 app/main.py add-metric <mid> <weight_kg|None> <heart_bpm|None> <body_fat_pct|None>\n"
        "  python3 main.py goals <mid>\n"
        "  python3 main.py update-goal <gid> <goal_type|None> <target_value|None> <achieved_at|None>"
        "  python3 app/main.py dashboard <mid>\n"
        "  python3 app/main.py register-class <mid> <scid>\n"
        "  python3 app/main.py classes\n"
        "  python3 app/main.py member-classes <mid>\n"
        "  python3 app/main.py add-availability <tid> <start_at> <end_at>\n"
        "  python3 app/main.py trainer-availability <tid>\n"
        "  python3 app/main.py trainer-schedule <tid>\n"
        "  python3 app/main.py add-class <cid> <tid> <rid> <start_at> <end_at> <capacity>\n"
    )
    
def parse_nullable(arg):
    if arg is None:
        return None
    return None if arg.lower() == "none" else arg

def print_table(rows, title=None):
    if title:
        print(f"\n=== {title} ===")
    if not rows:
        print("(no rows)")
    else:
        print(tabulate(rows, headers="keys", tablefmt="github"))
    print()
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "members":
            rows = get_all_members()
            print_table(rows, "Members")

        elif cmd == "add-member":
            if len(sys.argv) != 6:
                usage()
                sys.exit(1)
            full_name = sys.argv[2]
            dob       = parse_nullable(sys.argv[3])
            phone     = parse_nullable(sys.argv[4])
            email     = sys.argv[5]
            mid = register_member(full_name, dob, phone, email)
            print(f"Inserted member MID={mid}")
            rows = get_all_members()
            print_table(rows, "Members")

        elif cmd == "update-member":
            if len(sys.argv) != 7:
                usage()
                sys.exit(1)
            mid        = int(sys.argv[2])
            full_name  = parse_nullable(sys.argv[3])
            dob        = parse_nullable(sys.argv[4])
            phone      = parse_nullable(sys.argv[5])
            email      = parse_nullable(sys.argv[6])
            updated = update_member_profile(mid, full_name, dob, phone, email)
            print(f"Rows updated: {updated}")
            rows = get_all_members()
            print_table(rows, "Members")

        elif cmd == "add-metric":
            if len(sys.argv) != 6:
                usage()
                sys.exit(1)
            mid          = int(sys.argv[2])
            weight_arg   = parse_nullable(sys.argv[3])
            heart_arg    = parse_nullable(sys.argv[4])
            fat_arg      = parse_nullable(sys.argv[5])
            weight_kg    = float(weight_arg) if weight_arg is not None else None
            heart_bpm    = int(heart_arg) if heart_arg is not None else None
            body_fat_pct = float(fat_arg) if fat_arg is not None else None
            add_health_metric(mid, weight_kg, heart_bpm, body_fat_pct)
            print("Inserted health metric.")

        elif cmd == "goals":
            if len(sys.argv) != 3:
                usage()
                sys.exit(1)
            mid = int(sys.argv[2])
            rows = list_fitness_goals(mid)
            print_table(rows, f"Fitness goals for MID={mid}")

        elif cmd == "update-goal":
            if len(sys.argv) != 6:
                usage()
                sys.exit(1)

            gid        = int(sys.argv[2])
            goal_type  = parse_nullable(sys.argv[3])
            target_arg = parse_nullable(sys.argv[4])
            achieved_arg = parse_nullable(sys.argv[5])

            target_value = float(target_arg) if target_arg not in (None, "None") else None
            achieved_at  = achieved_arg if achieved_arg not in (None, "None") else None

            updated = update_goal(gid, goal_type, target_value, achieved_at)
            print(f"Rows updated: {updated}")
    
        elif cmd == "dashboard":
            if len(sys.argv) != 3:
                usage()
                sys.exit(1)
            mid = int(sys.argv[2])
            row = get_member_dashboard(mid)
            if row:
                print_table([row], f"Dashboard for MID={mid}")
            else:
                print(f"No dashboard data for MID={mid}")

        elif cmd == "classes":
            rows = list_scheduled_classes()
            print_table(rows, "Scheduled Classes")

        elif cmd == "register-class":
            if len(sys.argv) != 4:
                usage()
                sys.exit(1)
            mid  = int(sys.argv[2])
            scid = int(sys.argv[3])
            ok, err = register_for_class(mid, scid)
            if ok:
                print(f"Member {mid} registered for class {scid}.")
            else:
                print(f"Registration failed: {err}")

        elif cmd == "member-classes":
            if len(sys.argv) != 3:
                usage()
                sys.exit(1)
            mid = int(sys.argv[2])
            rows = list_member_registrations(mid)
            print_table(rows, f"Registrations for MID={mid}")

        elif cmd == "add-availability":
            if len(sys.argv) != 5:
                usage()
                sys.exit(1)
            tid      = int(sys.argv[2])
            start_at = sys.argv[3]  # e.g. "2025-04-01 09:00"
            end_at   = sys.argv[4]
            ok, err = add_trainer_availability(tid, start_at, end_at)
            if ok:
                print(f"Added availability for TID={tid} from {start_at} to {end_at}")
            else:
                print(f"Failed to add availability: {err}")

        elif cmd == "trainer-availability":
            if len(sys.argv) != 3:
                usage()
                sys.exit(1)
            tid = int(sys.argv[2])
            rows = list_trainer_availability(tid)
            print_table(rows, f"Availability for TID={tid}")

        elif cmd == "trainer-schedule":
            if len(sys.argv) != 3:
                usage()
                sys.exit(1)
            tid = int(sys.argv[2])
            rows = list_trainer_schedule(tid, only_future=True)
            print_table(rows, f"Upcoming classes for TID={tid}")

        elif cmd == "add-class":
            if len(sys.argv) != 8:
                usage()
                sys.exit(1)

            cid = int(sys.argv[2])
            tid      = int(sys.argv[3])
            rid      = int(sys.argv[4])
            start_at = sys.argv[5]
            end_at   = sys.argv[6]
            capacity = int(sys.argv[7])
            
            ok, scid, err = create_scheduled_class(
                cid, tid, rid, start_at, end_at, capacity
            )

            if ok:
                print(f"Created Scheduled_Class SCID={scid} (class {cid}, trainer {tid}, room {rid}).")
            else:
                print("Failed to create scheduled class:")
                print(err)

        else:
            usage()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)
