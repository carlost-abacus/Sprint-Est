from tkinter import LabelFrame, Label, Entry, Button, filedialog
from tkinter.ttk import Combobox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import os
from services.gitlab_service import fetch_all_data
from services.timesheet_processor import load_timesheet_files   

def setup_config_ui(app):
    frame = app.config_frame

    credentials_frame = LabelFrame(frame, text="GitLab Credentials", padx=10, pady=10)
    credentials_frame.pack(padx=20, pady=10, fill="x")
    
    Label(credentials_frame, text="GitLab URL:").grid(row=0, column=0, sticky="w")
    Entry(credentials_frame, textvariable=app.gitlab_url, width=60).grid(row=0, column=1)
    Label(credentials_frame, text="Token:").grid(row=1, column=0, sticky="w")
    Entry(credentials_frame, textvariable=app.private_token, show="*", width=60).grid(row=1, column=1)
    Label(credentials_frame, text="Project ID:").grid(row=2, column=0, sticky="w")
    Entry(credentials_frame, textvariable=app.project_id, width=60).grid(row=2, column=1)

    date_frame = LabelFrame(frame, text="Date Range", padx=10, pady=10)
    date_frame.pack(padx=20, pady=10, fill="x")
    
    Label(date_frame, text="Start Date:").grid(row=0, column=0)
    app.start_cal = Calendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd')
    app.start_cal.grid(row=1, column=0)
    app.start_cal.selection_set(datetime.now() - timedelta(days=30))

    Label(date_frame, text="End Date:").grid(row=0, column=1)
    app.end_cal = Calendar(date_frame, selectmode='day', date_pattern='yyyy-mm-dd')
    app.end_cal.grid(row=1, column=1)
    app.end_cal.selection_set(datetime.now())

    ts_frame = LabelFrame(frame, text="Time Sheets", padx=10, pady=10)
    ts_frame.pack(padx=20, pady=10, fill="x")

    app.timesheet_path_label = Label(ts_frame, text="No files selected.")
    app.timesheet_path_label.pack()

    Button(ts_frame, text="Select Time Sheet Files", command= lambda: load_timesheet_files(app)).pack()
    Button(frame, text="Fetch Data", command=lambda: fetch_all_data(app)).pack(pady=10)
