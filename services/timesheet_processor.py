import pandas as pd
import os
from tkinter import filedialog, END
from datetime import datetime, timedelta
from tkinter import messagebox


def load_timesheet_files(app):
    """Opens file dialog for timesheet files and updates the label."""
    file_paths = filedialog.askopenfilenames(
        title="Open Time Sheet Files",
        filetypes=[("CSV and Excel files", "*.csv *.xlsx *.xls")]
    )
    if file_paths:
        app.timesheet_file_paths = file_paths
        display_names = [os.path.basename(p) for p in file_paths]
        app.timesheet_path_label.config(text=f"Selected files: {', '.join(display_names)}")
    else:
        app.timesheet_path_label.config(text="No files selected.")
        app.timesheet_file_paths = [] # Clear if user cancels

def _process_timesheet_files(file_paths):
    """
    Processes selected CSV/Excel files for time sheet data.
    Returns:
        tuple: (task_hours, time_sheet_errors)
        task_hours (dict): Dictionary mapping task_id to total hours.
        time_sheet_errors (dict): Dictionary mapping owner/file to a list of error messages.
    """
    task_hours = {}
    time_sheet_errors = {}

    if not file_paths:
        return {}, {}

    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        file_basename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(file_basename)[0]
        current_owner = filename_without_ext[25:]
        if ext in ['.xlsx', '.xls']:
            all_sheets = pd.read_excel(file_path, sheet_name=None)
            dfs = [df for df in all_sheets.values()]
        else:
            if current_owner not in time_sheet_errors:
                time_sheet_errors[current_owner] = []
            time_sheet_errors[current_owner].append(f"Skipping unsupported file type: {file_basename}")
            continue

        try:

            for df_index, df in enumerate(dfs):

                if current_owner not in time_sheet_errors:
                    time_sheet_errors[current_owner] = []

                if 'Task' not in df.columns or 'Hrs' not in df.columns:
                    time_sheet_errors[current_owner].append(f"Sheet {df_index+1} in '{file_basename}': Missing 'Task' or 'Hrs' column.")
                    continue

                for row_num, row in df.iterrows():
                    task_str_raw = row.get('Task')
                    hrs_raw = row.get('Hrs')

                    try:
                        if isinstance(task_str_raw, str) and task_str_raw.startswith('#'):
                            task_str = task_str_raw[1:]
                        else:
                            task_str = str(task_str_raw)
                        if pd.isna(hrs_raw) or str(hrs_raw).strip() == '':
                            if(str(task_str_raw).strip() == ''):
                                time_sheet_errors[current_owner].append(f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): 'Hrs' is empty for Task '{task_str}'.")
                            continue
                        if not task_str.strip().isnumeric(): # Use strip() to handle whitespace
                            time_sheet_errors[current_owner].append(f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): Invalid Task format '{task_str_raw}'. Must be a number")
                            continue
                        task_num = int(task_str.strip())

                        hrs = float(hrs_raw)
                        if hrs < 0:
                            time_sheet_errors[current_owner].append(f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): 'Hrs' cannot be negative ('{hrs_raw}').")
                            continue

                        task_hours[task_num] = task_hours.get(task_num, 0) + hrs

                    except (ValueError, TypeError) as e:
                        time_sheet_errors[current_owner].append(f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): Data type error for Task '{task_str_raw}' or Hrs '{hrs_raw}'. Error: {e}")
                        continue

        except FileNotFoundError:
            if current_owner not in time_sheet_errors:
                time_sheet_errors[current_owner] = []
            time_sheet_errors[current_owner].append(f"File not found: {file_basename}")
        except pd.errors.EmptyDataError:
            if current_owner not in time_sheet_errors:
                time_sheet_errors[current_owner] = []
            time_sheet_errors[current_owner].append(f"Empty file: {file_basename}")
        except Exception as e:
            if current_owner not in time_sheet_errors:
                time_sheet_errors[current_owner] = []
            time_sheet_errors[current_owner].append(f"General error processing file: {file_basename} - {e}")
        print(time_sheet_errors)
    return task_hours, time_sheet_errors

def _populate_report_ui(app):
    """Populates the Treeview and filter dropdowns after data is fetched."""
    # Clear existing treeview data
    for item in app.tree.get_children():
        app.tree.delete(item)

    # Clear and populate filter dropdowns
    all_labels = sorted(list(set(label for issue in app.issues_data_raw for label in issue.get('labels', []))))
    app.label_filter_combo['values'] = ["All"] + all_labels
    app.label_filter_combo.set("All")

    all_milestones = sorted(list(set(issue['milestone'] for issue in app.issues_data_raw if issue['milestone'])))
    app.milestone_filter_combo['values'] = ["All"] + all_milestones
    app.milestone_filter_combo.set("All")

    all_assignees = sorted(list(set(assignee for issue in app.issues_data_raw for assignee in issue.get('assignees', []))))
    app.assignee_filter_combo['values'] = ["All"] + all_assignees
    app.assignee_filter_combo.set("All")

    app.action_filter_combo.set("All") # Reset action filter

    # Prepare data for display (store the full processed rows)
    app.current_display_data = [] # This will hold the filtered data for display
    for issue in app.issues_data_raw:
        task_number = issue['iid']
        milestone = issue['milestone'] if issue['milestone'] else 'None'
        estimateHours = issue['weight'] * 2 if issue['weight'] is not None else "None"
        created_at_date = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') if issue.get('created_at') else 'N/A'
        updated_at_date = datetime.strptime(issue['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') if issue.get('updated_at') else 'N/A'
        assignees_str = ", ".join(issue.get('assignees', []))
        labels_str = ", ".join(issue.get('labels', []))

        actualHour = app.task_hours_processed.get(task_number, 0)

        row_values = (
            task_number,
            issue['title'],
            assignees_str,
            milestone,
            labels_str,
            issue['weight'],
            estimateHours,
            actualHour,
            created_at_date,
            updated_at_date
        )
        # Store the data as a dictionary or a custom object if more complex filtering is needed
        # For now, a tuple is fine, but tracking original issue data might be better for filtering
        app.current_display_data.append(row_values)

    # Initially apply filters (which will populate the treeview with all data by default)
    apply_filters(app)

def apply_filters(app):
    """Applies selected filters to the displayed data."""
    selected_label = app.label_filter_combo.get()
    selected_milestone = app.milestone_filter_combo.get()
    selected_assignee = app.assignee_filter_combo.get()
    selected_action = app.action_filter_combo.get()

    # Clear current display
    for item in app.tree.get_children():
        app.tree.delete(item)

    # Filter and re-insert
    for row_values in app.current_display_data:
        task_id, title, assignees_str, milestone, labels_str, weight, est_hrs, act_hrs, created_at, updated_at = row_values

        # Label filter
        if selected_label != "All" and selected_label not in labels_str.split(', '):
            continue

        # Milestone filter
        if selected_milestone != "All" and selected_milestone != milestone:
            continue

        # Assignee filter
        if selected_assignee != "All" and selected_assignee not in assignees_str.split(', '):
            continue

        # Actual Hours filter (Action)
        if selected_action == "Has Actual Hours" and (act_hrs == 0 or act_hrs == 'N/A' or act_hrs is None):
            continue
        if selected_action == "Missing Actual Hours" and (act_hrs != 0 and act_hrs != 'N/A' and act_hrs is not None):
            continue

        app.tree.insert('', END, values=row_values)

