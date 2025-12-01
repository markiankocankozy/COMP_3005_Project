import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg.errors import DatabaseError, UniqueViolation, ExclusionViolation

def _conn_kwargs() -> dict:
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "gym_db"),
        "user": os.getenv("PGUSER", "markiankozy"),
        "password": os.getenv("PGPASSWORD", ""),
    }

@contextmanager
def get_conn():
    conn = psycopg.connect(**_conn_kwargs(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_members():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT mid, full_name, date_of_birth, phone_number, email
            FROM member
            ORDER BY mid;
        """)
        return cur.fetchall()

def register_member(full_name, dob, phone, email):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO member (full_name, date_of_birth, phone_number, email)
            VALUES (%s, %s, %s, %s)
            RETURNING mid;
            """,
            (full_name, dob, phone, email),
        )
        row = cur.fetchone()
        return row["mid"]

def update_member_profile(mid, full_name=None, dob=None, phone=None, email=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE member
            SET full_name = COALESCE(%s, full_name),
                date_of_birth = COALESCE(%s, date_of_birth),
                phone_number = COALESCE(%s, phone_number),
                email = COALESCE(%s, email)
            WHERE mid = %s;
            """,
            (full_name, dob, phone, email, mid),
        )
        return cur.rowcount

def add_health_metric(mid, weight_kg=None, heart_bpm=None, body_fat_pct=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO health_metric (mid, weight_kg, heart_bpm, body_fat_pct)
            VALUES (%s, %s, %s, %s);
            """,
            (mid, weight_kg, heart_bpm, body_fat_pct),
        )
                
        return cur.rowcount

def list_fitness_goals(mid: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                gid,
                mid,
                goal_type,
                target_value,
                created_at,
                achieved_at
            FROM fitness_goals
            WHERE mid = %s
            ORDER BY created_at DESC;
            """,
            (mid,),
        )
        return cur.fetchall()

def update_goal(gid, goal_type=None, target_value=None, achieved_at=None):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE fitness_goals
            SET goal_type   = COALESCE(%s, goal_type),
                target_value = COALESCE(%s, target_value),
                achieved_at  = %s
            WHERE gid = %s;
        """, (goal_type, target_value, achieved_at, gid))
        return cur.rowcount

def get_member_dashboard(mid):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM v_member_dashboard
            WHERE mid = %s;
            """,
            (mid,),
        )
        return cur.fetchone()

def register_for_class(mid, scid):
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO class_registration (mid, scid)
                VALUES (%s, %s);
                """,
                (mid, scid),
            )
            return True, None
        except DatabaseError as e:
            return False, str(e)

def list_scheduled_classes():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                sc.scid,
                fc.title,
                sc.start_at,
                sc.end_at,
                sc.capacity,
                t.full_name AS trainer,
                r.name AS room
            FROM scheduled_class sc
            JOIN fitnessclass fc ON fc.cid = sc.cid
            JOIN trainer t ON t.tid = sc.tid
            JOIN room r ON r.rid = sc.rid
            ORDER BY sc.start_at;
            """
        )
        return cur.fetchall()

def list_member_registrations(mid):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                cr.crid,
                sc.scid,
                fc.title,
                sc.start_at,
                sc.end_at,
                cr.register_at
            FROM class_registration cr
            JOIN scheduled_class sc ON sc.scid = cr.scid
            JOIN fitnessclass fc ON fc.cid = sc.cid
            WHERE cr.mid = %s
            ORDER BY sc.start_at;
            """,
            (mid,),
        )
        return cur.fetchall()

def add_trainer_availability(tid, start_at, end_at):
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO trainer_availability (tid, start_at, end_at)
                VALUES (%s, %s, %s);
                """,
                (tid, start_at, end_at),
            )
            return True, None
        except DatabaseError as e:
            return False, str(e)

def list_trainer_availability(tid):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT aid, tid, start_at, end_at
            FROM trainer_availability
            WHERE tid = %s
            ORDER BY start_at;
            """,
            (tid,),
        )
        return cur.fetchall()

def list_trainer_schedule(tid, only_future=True):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                sc.scid,
                fc.title,
                sc.start_at,
                sc.end_at,
                sc.capacity,
                r.name      AS room
            FROM scheduled_class sc
            JOIN fitnessclass fc ON fc.cid = sc.cid
            JOIN room r          ON r.rid = sc.rid
            WHERE sc.tid = %s
              AND (%s = FALSE OR sc.start_at >= now())
            ORDER BY sc.start_at;
            """,
            (tid, only_future),
        )
        return cur.fetchall()

def create_scheduled_class(cid, tid, rid, start_at, end_at, capacity):
    with get_conn() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO scheduled_class (cid, tid, rid, start_at, end_at, capacity)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING scid;
                """,
                (cid, tid, rid, start_at, end_at, capacity),
            )
            row = cur.fetchone()

            return True, row["scid"], None
        except DatabaseError as e:
            return False, None, str(e)


