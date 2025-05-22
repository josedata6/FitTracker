import sqlite3

DB_PATH = "data/tracker.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise TEXT,
                reps INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                meal_type TEXT,
                items TEXT
            )
        ''')
        conn.commit()

def insert_workout(date, exercise, reps):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO workouts (date, exercise, reps) VALUES (?, ?, ?)",
                  (date, exercise, reps))
        conn.commit()

def insert_meal(date, meal_type, items):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO meals (date, meal_type, items) VALUES (?, ?, ?)",
                  (date, meal_type, items))
        conn.commit()

def get_workout_summary():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT date, SUM(reps) FROM workouts GROUP BY date")
        return c.fetchall()

def get_meal_summary():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT meal_type, COUNT(*) FROM meals GROUP BY meal_type")
        return c.fetchall()

def get_all_data():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM workouts")
        workouts = c.fetchall()
        c.execute("SELECT * FROM meals")
        meals = c.fetchall()
        return workouts, meals
