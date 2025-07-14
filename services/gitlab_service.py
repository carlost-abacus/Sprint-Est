import gitlab
from datetime import datetime, timedelta
from tkinter import messagebox
import threading
from gui.loading_window import show_loading_window, hide_loading_window
from services.timesheet_processor import _process_timesheet_files, _populate_report_ui

def fetch_data(app):
    """
    Coordinates fetching GitLab issues and processing timesheets in a thread,
    then updates the UI.
    """
    gitlab_url = app.gitlab_url.get().strip()
    private_token = app.private_token.get().strip()
    project_id_str = app.project_id.get().strip()

    start_date_obj = app.start_cal.selection_get()
    end_date_obj = app.end_cal.selection_get()

    if not gitlab_url or not private_token or not project_id_str:
        messagebox.showerror("Missing Information", "Please enter all GitLab credentials.")
        return
    try:
        project_id = int(project_id_str)
    except ValueError:
        messagebox.showerror("Invalid Project ID", "Project ID must be a number.")
        return

    if not start_date_obj or not end_date_obj:
        messagebox.showerror("Missing Dates", "Please select both start and end dates for 'Last Update'.")
        return
    if start_date_obj > end_date_obj:
        messagebox.showerror("Date Error", "Start date cannot be after end date.")
        return

    # Store dates for GitLab API
    app.start_date_str_gitlab.set(start_date_obj.strftime('%Y-%m-%d'))
    app.end_date_str_gitlab.set(end_date_obj.strftime('%Y-%m-%d'))

    # Show loading screen
    show_loading_window(app)

    # Run data fetching and processing in a separate thread
    threading.Thread(target=fetch_gitlab_issues,
                        args=(app, gitlab_url, private_token, project_id,
                            app.start_date_str_gitlab.get(), app.end_date_str_gitlab.get())).start()

def process_data(app):
    """Worker thread to fetch GitLab data and process timesheets."""
    try:
        # Process timesheets (assuming files were already selected and app.timesheet_file_paths is set)
        if hasattr(app, 'timesheet_file_paths') and app.timesheet_file_paths:
            processed_hours, errors = _process_timesheet_files(app.timesheet_file_paths)
        else:
            processed_hours, errors = {}, {}

        app.task_hours_processed = processed_hours
        app.time_sheet_errors = errors

        # Update UI on the main thread
        app.master.after(0, lambda: _populate_report_ui(app)) # Populate filters and table
        app.master.after(0, lambda: app.notebook.select(app.report_frame)) # Switch to report tab

    except Exception as e:
        app.master.after(0, lambda: hide_loading_window(app))
        app.master.after(0, lambda e=e: messagebox.showerror(
            "Processing Error",
            f"An error occurred during data fetching or processing: {e}"
        ))
        print(f"Error in fetch_and_process_data_thread: {e}")

def fetch_gitlab_issues(app, gitlab_url, private_token, project_id, start_date_str, end_date_str):
    """
    Fetches GitLab issues. This is run in a separate thread.
    Returns a list of issue data.
    """
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        project = gl.projects.get(project_id)
    except gitlab.exceptions.GitlabError as e:
        app.master.after(0, lambda: messagebox.showerror("GitLab Error", f"Error accessing GitLab or project. Check URL, token, and project ID.\nError Details: {e}"))
        return []

    issues_data = []
    page = 1
    start_iso = datetime.strptime(start_date_str, '%Y-%m-%d').isoformat() + "Z"
    # Add one day to end_date to include issues updated on the end_date itapp
    end_date_plus_one = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
    end_iso = end_date_plus_one.isoformat() + "Z"

    try:
        while True:
            issues = project.issues.list(
                updated_after=start_iso,
                updated_before=end_iso,
                all=True # Ensure all issues are fetched, not just the first page
            )
            # GitLab API 'list' method with all=True handles pagination automatically.
            # No need for manual page iteration with per_page if using all=True
            # The loop `while True` with `page += 1` is redundant with `all=True`.
            # Let's simplify this part based on how python-gitlab works.

            for issue in issues:
                assignees_names = [assignee['name'] for assignee in issue.assignees] if issue.assignees else []
                milestone_title = issue.milestone['title'] if issue.milestone else None
                issue_weight = issue.weight if hasattr(issue, 'weight') and issue.weight is not None else None
                labels = issue.labels if hasattr(issue, 'labels') else []

                issues_data.append({
                    'iid': issue.iid,
                    'title': issue.title,
                    'assignees': assignees_names,
                    'milestone': milestone_title,
                    'weight': issue_weight,
                    'created_at': issue.created_at,
                    'updated_at': issue.updated_at,
                    'labels': labels
                })
            break # Exit loop as all=True fetches all
    except gitlab.exceptions.GitlabError as e:
        app.master.after(0, lambda e=e: messagebox.showerror(
            "GitLab Error", f"Error fetching issues from GitLab.\nError Details: {e}"
        ))
        return []
    app.master.after(0, lambda: hide_loading_window(app))
    app.issues_data_raw = issues_data
