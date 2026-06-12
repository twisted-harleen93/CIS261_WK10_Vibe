#!/usr/bin/env python3
"""
Student Grade Calculator
Features:
- Manage student records (name, id, 3 test scores)
- Calculate average and letter grade
- Display students in a table
- Class statistics (highest, lowest, average)
- Search by name (case-insensitive)
- Save/load to/from `student_grades.txt` (pipe-delimited)
- Press ESC at the start of the menu to exit

File format: name|id|test1|test2|test3|average|grade

"""

import os
import sys
import termios
import tty
from typing import List, Optional

DATA_FILE = "student_grades.txt"


class Student:
    def __init__(self, name: str, student_id: str, test1: float, test2: float, test3: float):
        self.name = name
        self.student_id = student_id
        self.test1 = float(test1)
        self.test2 = float(test2)
        self.test3 = float(test3)
        self.average = self.calculate_average()
        self.grade = self.calculate_grade()

    def calculate_average(self) -> float:
        return round((self.test1 + self.test2 + self.test3) / 3.0, 2)

    def calculate_grade(self) -> str:
        avg = self.average
        if avg >= 90:
            return "A"
        if avg >= 80:
            return "B"
        if avg >= 70:
            return "C"
        if avg >= 60:
            return "D"
        return "F"

    def to_pipe(self) -> str:
        return f"{self.name}|{self.student_id}|{self.test1:.2f}|{self.test2:.2f}|{self.test3:.2f}|{self.average:.2f}|{self.grade}\n"


def get_single_key(prompt: Optional[str] = None) -> str:
    if prompt:
        print(prompt, end=' ', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print()
    return ch


def load_students(filename: str) -> List[Student]:
    students: List[Student] = []
    if not os.path.exists(filename):
        return students
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) < 6:
                    continue
                name = parts[0]
                sid = parts[1]
                try:
                    t1 = float(parts[2])
                    t2 = float(parts[3])
                    t3 = float(parts[4])
                except ValueError:
                    print(f"Skipping malformed line: {line}")
                    continue
                # Recompute average/grade from tests to ensure consistency
                students.append(Student(name, sid, t1, t2, t3))
    except OSError as e:
        print(f"Error loading file '{filename}': {e}")
    return students


def save_students(filename: str, students: List[Student]) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for s in students:
                f.write(s.to_pipe())
        print(f"Saved {len(students)} record(s) to '{filename}'.")
    except OSError as e:
        print(f"Error saving file '{filename}': {e}")


def add_student(students: List[Student]) -> None:
    print("Enter new student (press Enter to cancel any prompt):")
    name = input("Name: ").strip()
    if not name:
        print("Cancelled adding student.")
        return
    sid = input("Student ID: ").strip()
    if not sid:
        print("Cancelled adding student.")
        return

    def get_score(prompt: str) -> Optional[float]:
        while True:
            val = input(prompt).strip()
            if val == "":
                return None
            try:
                f = float(val)
                if f < 0 or f > 100:
                    print("Enter a score between 0 and 100.")
                    continue
                return f
            except ValueError:
                print("Invalid number. Try again or press Enter to cancel.")

    t1 = get_score("Test 1 score: ")
    if t1 is None:
        print("Cancelled adding student.")
        return
    t2 = get_score("Test 2 score: ")
    if t2 is None:
        print("Cancelled adding student.")
        return
    t3 = get_score("Test 3 score: ")
    if t3 is None:
        print("Cancelled adding student.")
        return

    s = Student(name, sid, t1, t2, t3)
    students.append(s)
    print(f"Added student: {s.name} (Avg: {s.average:.2f}, Grade: {s.grade})")


def display_students(students: List[Student]) -> None:
    if not students:
        print("No student records available.")
        return
    header = f"{'Name':30} | {'ID':10} | {'T1':6} | {'T2':6} | {'T3':6} | {'Avg':6} | {'Grade':5}"
    print(header)
    print('-' * len(header))
    for s in students:
        print(f"{s.name:30} | {s.student_id:10} | {s.test1:6.2f} | {s.test2:6.2f} | {s.test3:6.2f} | {s.average:6.2f} | {s.grade:5}")


def class_statistics(students: List[Student]) -> None:
    if not students:
        print("No student records to calculate statistics.")
        return
    avgs = [s.average for s in students]
    highest = max(avgs)
    lowest = min(avgs)
    class_avg = round(sum(avgs) / len(avgs), 2)
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average:  {lowest:.2f}")
    print(f"Class average:   {class_avg:.2f}")


def search_student(students: List[Student]) -> None:
    key = input("Enter student name to search (case-insensitive): ").strip().lower()
    if not key:
        print("Empty search.")
        return
    results = [s for s in students if key in s.name.lower()]
    if not results:
        print("No matching students found.")
        return
    print(f"Found {len(results)} result(s):")
    display_students(results)


def main():
    print("Student Grade Calculator")
    students = load_students(DATA_FILE)
    if students:
        print(f"Loaded {len(students)} record(s) from '{DATA_FILE}'.")

    while True:
        ch = get_single_key("Press ESC to exit, or any other key to continue:")
        if ch and ord(ch) == 27:
            print("Exiting program.")
            break

        print("\nMenu Options:")
        print("1 - Add new student")
        print("2 - Display all students")
        print("3 - Search student by name")
        print("4 - Show class statistics")
        print("5 - Save records to file")
        print("6 - Exit")

        choice = input("Choose an option (1-6): ").strip()
        if choice == '1':
            add_student(students)
        elif choice == '2':
            display_students(students)
        elif choice == '3':
            search_student(students)
        elif choice == '4':
            class_statistics(students)
        elif choice == '5':
            save_students(DATA_FILE, students)
        elif choice == '6':
            confirm = input("Exit without saving? (y/N): ").strip().lower()
            if confirm == 'y':
                print("Exiting without saving.")
                break
            else:
                print("Exit cancelled.")
        else:
            print("Invalid choice. Please choose 1-6.")

    # Auto-save on normal exit
    if students:
        try:
            save_students(DATA_FILE, students)
        except Exception:
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
