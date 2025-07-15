import tkinter as tk
import os
from tkinter import PhotoImage, messagebox
from tkinter.ttk import Notebook
from app_config import get_executable_dir, load_config
from gui.config_tab import setup_config_ui
from gui.report_tab import setup_report_ui

class GitLabReportApp:
    def __init__(self, master):
        self.master = master
        master.title("GitLab Progress Report")
        master.geometry("1200x800")
        master.resizable(True, True)

        try:
            photo_path = os.path.join(get_executable_dir(), "assets", "abacus_icon.png")
            photo = PhotoImage(file=photo_path)
            master.iconphoto(True, photo)
        except Exception:
            pass

        # Load config
        config = load_config()
        self.gitlab_url = tk.StringVar(value=config.get("gitlab_url", ""))
        self.private_token = tk.StringVar(value=config.get("private_token", ""))
        self.project_id = tk.StringVar(value=str(config.get("project_id", "")))

        self.app_password = str(config.get("app_password", ""))
        self.sender_email = str(config.get("sender_email", ""))

        self.start_date_str_gitlab = tk.StringVar()
        self.end_date_str_gitlab = tk.StringVar()

        self.issues_data_raw = []
        self.task_hours_processed = {}
        self.time_sheet_errors = {}
        self.current_display_data = []

        self.notebook = Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        self.config_frame = tk.Frame(self.notebook)
        self.report_frame = tk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.notebook.add(self.report_frame, text="Report")

        setup_config_ui(self)
        setup_report_ui(self)

        self.loading_window = None
        self.notebook.select(self.config_frame)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.master.destroy()

    def on_tab_change(self, event):
        if self.notebook.tab(self.notebook.select(), "text") == "Report":
            if not self.issues_data_raw:
                messagebox.showinfo("No Data", "Please fetch data from the 'Configuration' tab first.")
                self.notebook.select(self.config_frame)
