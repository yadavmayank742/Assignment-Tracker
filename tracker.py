# @Author MAYANK YADAV

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar # type: ignore
import json
import os

""" @TODO
1. Update the assignment
2. Add remarks and notes for the assignment
3. GUI and UX
4. Search results display
"""

class AssignmentTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Homework and Assignment Tracker")
        self.master.bind("<Control-f>", self.open_search_dialog)

        # Initialize assignments list and classes
        self.assignments = []
        self.completed_assignments = []
        self.classes = []

        # UI Elements
        self.create_widgets()
        self.load_data()

    def open_search_dialog(self, event=None):
        """ Open a dialog for searching assignments. """
        self.search_window = tk.Toplevel(self.master)
        self.search_window.title("Search Assignments")

        ttk.Label(self.search_window, text="Enter search term:").grid(row=0, column=0)
        self.search_entry = ttk.Entry(self.search_window)
        self.search_entry.grid(row=0, column=1)
        self.search_entry.bind("<Return>", self.perform_search)

        confirm_button = ttk.Button(self.search_window, text="Search", command=self.perform_search)
        confirm_button.grid(row=1, columnspan=2)

    def perform_search(self, event=None):
        """ Perform the fuzzy search and update the display. """
        search_term = self.search_entry.get().lower()
        filtered_assignments = [a for a in self.assignments if search_term in a["course"].lower() or
                                search_term in a["assignment"].lower()]

        self.update_filtered_list(filtered_assignments)

    def update_filtered_list(self, filtered_assignments):
        """ Update the list to show only filtered assignments. """
        for item in self.assignment_list.get_children():
            self.assignment_list.delete(item)

        for assignment in filtered_assignments:
            self.assignment_list.insert("", "end", values=(assignment["course"], assignment["assignment"], assignment["due_date"]))

        self.search_window.destroy()

    def create_widgets(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10), padding=6)
        style.configure('TLabel', font=('Helvetica', 10), padding=6)
        
        # Frame for active assignments
        self.active_frame = ttk.LabelFrame(self.master, text="Active Assignments")
        self.active_frame.grid(row=0, column=0, padx=10, pady=10)

        # Class Name Dropdown
        ttk.Label(self.active_frame, text="Course Name:").grid(row=0, column=0)
        self.class_name_var = tk.StringVar()
        self.class_name_dropdown = ttk.Combobox(self.active_frame, textvariable=self.class_name_var)
        self.class_name_dropdown.grid(row=0, column=1)
        self.class_name_dropdown['values'] = self.classes

        # Assignment Name Input
        ttk.Label(self.active_frame, text="Assignment Name:").grid(row=1, column=0)
        self.assignment_name_entry = ttk.Entry(self.active_frame)
        self.assignment_name_entry.grid(row=1, column=1)

        # Due Date Input
        ttk.Label(self.active_frame, text="Due Date:").grid(row=2, column=0)
        self.due_date_var = tk.StringVar()
        self.due_date_entry = ttk.Entry(self.active_frame, textvariable=self.due_date_var, state='readonly')
        self.due_date_entry.grid(row=2, column=1)

        # Calendar Button
        self.calendar_button = ttk.Button(self.active_frame, text="Select Date", command=self.show_calendar)
        self.calendar_button.grid(row=2, column=2)

        # Add Assignment Button
        self.add_button = ttk.Button(self.active_frame, text="Add Assignment", command=self.add_assignment)
        self.add_button.grid(row=3, column=0)

        # Complete Assignment Button
        self.complete_button = ttk.Button(self.active_frame, text="Complete Assignment", command=self.complete_assignment)
        self.complete_button.grid(row=3, column=1)

        # Assignment List with sorting capabilities
        self.assignment_list = ttk.Treeview(self.active_frame, columns=("Course", "Assignment", "Due Date"), show='headings')
        self.assignment_list.heading("Course", text="Course", command=lambda: self.sort_column("Course"))
        self.assignment_list.heading("Assignment", text="Assignment", command=lambda: self.sort_column("Assignment"))
        self.assignment_list.heading("Due Date", text="Due Date", command=lambda: self.sort_column("Due Date"))
        self.assignment_list.grid(row=4, columnspan=3, pady=(10, 0))

        # Frame for completed assignments
        self.completed_frame = ttk.LabelFrame(self.master, text="Completed Assignments")
        self.completed_frame.grid(row=1, column=0, padx=10, pady=10)

        # Completed Assignment List
        self.completed_list = ttk.Treeview(self.completed_frame, columns=("Course", "Assignment", "Due Date", "Marks"), show='headings')
        self.completed_list.heading("Course", text="Course")
        self.completed_list.heading("Assignment", text="Assignment")
        self.completed_list.heading("Due Date", text="Due Date")
        self.completed_list.heading("Marks", text="Marks")
        self.completed_list.grid(row=0, column=0)

        # Marks Entry
        ttk.Label(self.completed_frame, text="Marks Awarded:").grid(row=1, column=0)
        self.marks_entry = ttk.Entry(self.completed_frame)
        self.marks_entry.grid(row=1, column=1)

        # Save Data Button
        self.save_button = ttk.Button(self.master, text="Save Data", command=self.save_data)
        self.save_button.grid(row=2, column=0, padx=10, pady=10)

        self.assignment_list.bind("<<TreeviewSelect>>", self.on_select)
        self.completed_list.bind("<<TreeviewSelect>>", self.on_select_completed)

        # Add Update Marks Button
        self.update_marks_button = ttk.Button(self.completed_frame, text="Update Marks", command=self.update_marks)
        self.update_marks_button.grid(row=2, column=0)

    def on_select_completed(self, event):
        """Handle the selection of a completed assignment."""
        selected_item = self.completed_list.selection()
        if selected_item:
            index = self.completed_list.index(selected_item[0])
            selected_assignment = self.completed_assignments[index]

            # Set the marks entry to the current marks of the selected assignment
            current_marks = selected_assignment.get("marks", "")
            self.marks_entry.delete(0, tk.END)
            self.marks_entry.insert(0, current_marks)

    def sort_column(self, col):
        """ Sort the treeview based on the selected column. """
        if col == "Course":
            self.assignments.sort(key=lambda x: x["course"])
        elif col == "Assignment":
            self.assignments.sort(key=lambda x: x["assignment"])
        elif col == "Due Date":
            self.assignments.sort(key=lambda x: datetime.strptime(x["due_date"], "%d-%m-%Y"))

        self.update_active_list()


    def show_calendar(self):
        # Open a calendar dialog
        self.calendar_window = tk.Toplevel(self.master)
        self.calendar_window.title("Select Due Date")
        self.calendar = Calendar(self.calendar_window, selectmode='day')
        self.calendar.pack(padx=10, pady=10)
        
        # Confirm button
        confirm_button = ttk.Button(self.calendar_window, text="Confirm", command=self.get_date)
        confirm_button.pack(pady=(0, 10))

    def get_date(self):
        # Get the selected date from the calendar in MM/DD/YY format
        selected_date = self.calendar.get_date()

        # Convert the date to DD-MM-YYYY format
        formatted_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%d-%m-%Y")

        # Update the entry field with the formatted date
        self.due_date_var.set(formatted_date)
        self.calendar_window.destroy()



    def add_assignment(self):
        class_name = self.class_name_var.get()
        assignment_name = self.assignment_name_entry.get()
        due_date = self.due_date_var.get()

        # Ensure the due date is in the correct format
        try:
            formatted_date = datetime.strptime(due_date, "%d-%m-%Y").strftime("%d-%m-%Y")
        except ValueError:
            messagebox.showwarning("Input Error", "Due date must be in DD-MM-YYYY format.")
            return

        if class_name and assignment_name and due_date:
            assignment = {"course": class_name, "assignment": assignment_name, "due_date": formatted_date}
            self.assignments.append(assignment)
            self.update_active_list()
            self.clear_entries()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields")


    def complete_assignment(self):
        selected_item = self.assignment_list.selection()
        if selected_item:
            index = self.assignment_list.index(selected_item[0])
            completed_assignment = self.assignments.pop(index)
            completed_assignment["marks"] = ""
            self.completed_assignments.append(completed_assignment)
            self.update_active_list()
            self.update_completed_list()
        else:
            messagebox.showwarning("Selection Error", "Please select an assignment to complete")

    def update_active_list(self):
        # Clear the current list
        for item in self.assignment_list.get_children():
            self.assignment_list.delete(item)

        # Add updated assignments to the list
        for assignment in self.assignments:
            self.assignment_list.insert("", "end", values=(assignment["course"], assignment["assignment"], assignment["due_date"]))

    def update_marks(self):
        selected_item = self.completed_list.selection()
        if selected_item:
            index = self.completed_list.index(selected_item[0])
            marks = self.marks_entry.get()
            self.completed_assignments[index]["marks"] = marks
            self.update_completed_list()
        else:
            messagebox.showwarning("Selection Error", "Please select an assignment to update marks")

    def update_completed_list(self):
        # Clear the completed list
        for item in self.completed_list.get_children():
            self.completed_list.delete(item)

        # Add completed assignments to the list
        for assignment in self.completed_assignments:
            marks = assignment.get("marks", "")
            self.completed_list.insert("", "end", values=(assignment["course"], assignment["assignment"], assignment["due_date"], marks))

    def clear_entries(self):
        self.class_name_var.set('')
        self.assignment_name_entry.delete(0, tk.END)
        self.due_date_var.set('')

    def on_select(self, event):
        selected_item = self.assignment_list.selection()
        if selected_item:
            index = self.assignment_list.index(selected_item[0])
            self.class_name_var.set(self.assignments[index]["course"])
            self.assignment_name_entry.delete(0, tk.END)
            self.assignment_name_entry.insert(0, self.assignments[index]["assignment"])
            self.due_date_var.set(self.assignments[index]["due_date"])

    def save_data(self):
        data = {
            "assignments": self.assignments,
            "completed_assignments": self.completed_assignments,
            "courses": list(set(self.classes))  # Save unique courses
        }
        with open("assignments.json", "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Save Data", "Assignments saved successfully!")

    def load_data(self):
        if os.path.exists("assignments.json"):
            with open("assignments.json", "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.assignments = data.get("assignments", [])
                        self.completed_assignments = data.get("completed_assignments", [])

                        # Convert date formats if necessary
                        for assignment in self.assignments:
                            if "/" in assignment["due_date"]:
                                assignment["due_date"] = datetime.strptime(assignment["due_date"], "%d/%m/%y").strftime("%d-%m-%Y")

                        # Extract unique classes
                        classes_set = {assignment["course"] for assignment in self.assignments}
                        classes_set.update(assignment["course"] for assignment in self.completed_assignments)
                        classes_set.update(data.get("courses", []))
                        self.classes = list(classes_set)
                        self.classes = list(classes_set)

                        self.class_name_dropdown['values'] = self.classes
                        
                        # Update the active assignments list in the UI
                        self.update_active_list()
                        self.update_completed_list()
                    else:
                        self.assignments = []
                        self.completed_assignments = []
                        self.classes = []
                except json.JSONDecodeError:
                    self.assignments = []
                    self.completed_assignments = []
                    self.classes = []
        else:
            self.assignments = []
            self.completed_assignments = []
            self.classes = []



if __name__ == "__main__":
    root = tk.Tk()
    app = AssignmentTracker(root)
    root.mainloop()
