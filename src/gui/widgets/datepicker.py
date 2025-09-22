import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime

class Datepicker(tk.Toplevel):
    def __init__(self, parent, entry_widget):
        super().__init__(parent)
        self.entry_widget = entry_widget
        self.selected_date = None

        self.title("Select a Date")
        self.geometry("250x220")
        self.resizable(False, False)

        today = datetime.today()
        self.year = today.year
        self.month = today.month

        self.create_widgets()
        self.update_calendar()

        # Center on parent
        self.transient(parent)
        self.grab_set()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


    def create_widgets(self):
        # Header for navigation
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=5)

        ttk.Button(header_frame, text="<", command=self.prev_month, width=2).pack(side=tk.LEFT, padx=5)
        self.month_year_label = ttk.Label(header_frame, text="", font=("Arial", 12, "bold"), width=15, anchor="center")
        self.month_year_label.pack(side=tk.LEFT)
        ttk.Button(header_frame, text=">", command=self.next_month, width=2).pack(side=tk.LEFT, padx=5)

        # Calendar Frame
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack()

    def update_calendar(self):
        # Clear old calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update month/year label
        self.month_year_label.config(text=f"{calendar.month_name[self.month]} {self.year}")

        # Day names
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(days):
            ttk.Label(self.calendar_frame, text=day, width=4, anchor="center").grid(row=0, column=i)

        # Create calendar days
        month_calendar = calendar.monthcalendar(self.year, self.month)
        for row_idx, week in enumerate(month_calendar, 1):
            for col_idx, day in enumerate(week):
                if day != 0:
                    day_button = ttk.Button(self.calendar_frame, text=str(day), width=4,
                                            command=lambda d=day: self.select_date(d))
                    day_button.grid(row=row_idx, column=col_idx)

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.update_calendar()

    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.update_calendar()

    def select_date(self, day):
        self.selected_date = f"{self.year}-{self.month:02d}-{day:02d}"
        self.entry_widget.delete(0, tk.END)
        self.entry_widget.insert(0, self.selected_date)
        self.destroy()

def create_datepicker_entry(parent, text="Date:"):
    """Helper function to create a label, entry, and button for a datepicker."""
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=text).pack(side=tk.LEFT, padx=(0, 5))
    entry = ttk.Entry(frame, width=12)
    entry.pack(side=tk.LEFT)

    def open_datepicker():
        Datepicker(parent, entry)

    button = ttk.Button(frame, text="📅", width=2, command=open_datepicker)
    button.pack(side=tk.LEFT, padx=(2, 0))

    return frame, entry
