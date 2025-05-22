import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
import sqlite3
import matplotlib.pyplot as plt
import csv

DB_PATH = "data/tracker.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()


class FitnessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fitness & Meal Tracker")
        self.setGeometry(100, 100, 500, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Workout Entry
        layout.addWidget(QLabel("Workout Entry"))
        self.workout_date = QLineEdit()
        self.workout_date.setPlaceholderText("Date (YYYY-MM-DD)")
        layout.addWidget(self.workout_date)

        self.exercise_type = QComboBox()
        self.exercise_type.addItems(["Pushups", "Squats", "Pullups"])
        layout.addWidget(self.exercise_type)

        self.reps_input = QLineEdit()
        self.reps_input.setPlaceholderText("Reps")
        layout.addWidget(self.reps_input)

        workout_btn = QPushButton("Save Workout")
        workout_btn.clicked.connect(self.save_workout)
        layout.addWidget(workout_btn)

        # Meal Entry
        layout.addWidget(QLabel("Meal Entry"))
        self.meal_date = QLineEdit()
        self.meal_date.setPlaceholderText("Date (YYYY-MM-DD)")
        layout.addWidget(self.meal_date)

        self.meal_type = QComboBox()
        self.meal_type.addItems(["Breakfast", "Lunch", "Dinner", "Snack"])
        layout.addWidget(self.meal_type)

        self.meal_items = QTextEdit()
        self.meal_items.setPlaceholderText("What did you eat?")
        layout.addWidget(self.meal_items)

        meal_btn = QPushButton("Save Meal")
        meal_btn.clicked.connect(self.save_meal)
        layout.addWidget(meal_btn)

        # Chart and Export Buttons
        btn_layout = QHBoxLayout()
        chart_btn = QPushButton("Show Workout Chart")
        chart_btn.clicked.connect(self.show_chart)
        btn_layout.addWidget(chart_btn)

        meal_chart_btn = QPushButton("Show Meal Stats")
        meal_chart_btn.clicked.connect(self.show_meal_chart)
        btn_layout.addWidget(meal_chart_btn)

        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        btn_layout.addWidget(export_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_workout(self):
        date = self.workout_date.text()
        exercise = self.exercise_type.currentText()
        reps = self.reps_input.text()

        if not date or not reps.isdigit():
            QMessageBox.warning(self, "Input Error", "Please fill workout fields correctly.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO workouts (date, exercise, reps) VALUES (?, ?, ?)",
                  (date, exercise, int(reps)))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", "Workout saved successfully!")
        self.workout_date.clear()
        self.reps_input.clear()

    def save_meal(self):
        date = self.meal_date.text()
        meal_type = self.meal_type.currentText()
        items = self.meal_items.toPlainText()

        if not date or not items:
            QMessageBox.warning(self, "Input Error", "Please fill meal fields correctly.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO meals (date, meal_type, items) VALUES (?, ?, ?)",
                  (date, meal_type, items))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", "Meal saved successfully!")
        self.meal_date.clear()
        self.meal_items.clear()

    def show_chart(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT date, SUM(reps) FROM workouts GROUP BY date")
        data = c.fetchall()
        conn.close()

        if not data:
            QMessageBox.information(self, "No Data", "No workouts to show.")
            return

        dates, reps = zip(*data)
        plt.figure(figsize=(10, 5))
        plt.plot(dates, reps, marker='o')
        plt.title("Total Reps Over Time")
        plt.xlabel("Date")
        plt.ylabel("Reps")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_meal_chart(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT meal_type, COUNT(*) FROM meals GROUP BY meal_type")
        data = c.fetchall()
        conn.close()

        if not data:
            QMessageBox.information(self, "No Data", "No meals to show.")
            return

        types, counts = zip(*data)
        plt.figure(figsize=(6, 6))
        plt.pie(counts, labels=types, autopct='%1.1f%%')
        plt.title("Meal Type Distribution")
        plt.tight_layout()
        plt.show()

    def export_to_csv(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM workouts")
        workouts = c.fetchall()
        c.execute("SELECT * FROM meals")
        meals = c.fetchall()
        conn.close()

        with open("data/workouts.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Exercise", "Reps"])
            writer.writerows(workouts)

        with open("data/meals.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Meal Type", "Items"])
            writer.writerows(meals)

        QMessageBox.information(self, "Exported", "Data exported to CSV successfully!")


if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)
    window = FitnessApp()
    window.show()
    sys.exit(app.exec_())
