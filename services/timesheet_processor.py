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
    task_entries = []
    time_sheet_errors = {}

    if not file_paths:
        return [], {}

    for file_path in file_paths:
        ext = os.path.splitext(file_path)[1].lower()
        file_basename = os.path.basename(file_path)
        filename_without_ext = os.path.splitext(file_basename)[0]
        current_owner = filename_without_ext[25:]

        if ext in ['.xlsx', '.xls']:
            all_sheets = pd.read_excel(file_path, sheet_name=None)
            dfs = [df for df in all_sheets.values()]
        else:
            time_sheet_errors.setdefault(current_owner, []).append(f"Skipping unsupported file type: {file_basename}")
            continue

        try:
            for df_index, df in enumerate(dfs):
                time_sheet_errors.setdefault(current_owner, [])

                if 'Task' not in df.columns or 'Hrs' not in df.columns:
                    time_sheet_errors[current_owner].append(f"Sheet {df_index+1} in '{file_basename}': Missing 'Task' or 'Hrs' column.")
                    continue

                for row_num, row in df.iterrows():
                    task_str_raw = row.get('Task')
                    hrs_raw = row.get('Hrs')
                    action_raw = row.get('Action', 'None')

                    try:
                        if isinstance(task_str_raw, str) and task_str_raw.startswith('#'):
                            task_str = task_str_raw[1:]
                        else:
                            task_str = str(task_str_raw)

                        if pd.isna(hrs_raw) or str(hrs_raw).strip() == '':
                            if str(task_str_raw).strip() == '':
                                time_sheet_errors[current_owner].append(
                                    f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): 'Hrs' is empty for Task '{task_str}'.")
                            continue

                        if not task_str.strip().isnumeric():
                            time_sheet_errors[current_owner].append(
                                f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): Invalid Task format '{task_str_raw}'. Must be a number")
                            continue

                        task_num = int(task_str.strip())
                        hrs = float(hrs_raw)

                        if hrs < 0:
                            time_sheet_errors[current_owner].append(
                                f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): 'Hrs' cannot be negative ('{hrs_raw}').")
                            continue

                        action = str(action_raw).strip()
                        task_entries.append({
                            'task_id': task_num,
                            'owner': current_owner,
                            'action': action,
                            'hours': hrs
                        })

                    except (ValueError, TypeError) as e:
                        time_sheet_errors[current_owner].append(
                            f"Row {row_num + 2} in '{file_basename}' (Sheet {df_index+1}): Data type error. Task: '{task_str_raw}', Hrs: '{hrs_raw}'. Error: {e}")
                        continue

        except Exception as e:
            time_sheet_errors.setdefault(current_owner, []).append(f"Error processing '{file_basename}': {e}")

    return task_entries, time_sheet_errors

def _populate_report_ui(app):
    app.tree.delete(*app.tree.get_children())

    all_labels = sorted(list(set(label for issue in app.issues_data_raw for label in issue.get('labels', []))))
    app.label_filter_combo['values'] = ["All"] + all_labels
    app.label_filter_combo.set("All")

    all_milestones = sorted(list(set(issue['milestone'] for issue in app.issues_data_raw if issue['milestone'])))
    app.milestone_filter_combo['values'] = ["All"] + all_milestones
    app.milestone_filter_combo.set("All")

    all_assignees = sorted(list(set(assignee for issue in app.issues_data_raw for assignee in issue.get('assignees', []))))
    app.assignee_filter_combo['values'] = ["All"] + all_assignees
    app.assignee_filter_combo.set("All")

    if hasattr(app, 'task_entries'):
        all_owners = sorted(set(entry['owner'] for entry in app.task_entries))
        all_actions = sorted(set(entry['action'] for entry in app.task_entries))

        app.owner_filter_combo['values'] = ["All"] + all_owners
        app.owner_filter_combo.set("All")

        app.timesheet_action_filter_combo['values'] = ["All"] + all_actions
        app.timesheet_action_filter_combo.set("All")
    else:
        app.owner_filter_combo['values'] = ["All"]
        app.timesheet_action_filter_combo['values'] = ["All"]

    app.has_actHour_filter_combo.set("All")

    app.current_display_data = []

    for issue in app.issues_data_raw:
        task_number = issue['iid']
        milestone = issue['milestone'] if issue['milestone'] else 'None'
        estimateHours = issue['weight'] * 2 if issue['weight'] is not None else "None"
        created_at_date = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') if issue.get('created_at') else 'N/A'
        updated_at_date = datetime.strptime(issue['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d') if issue.get('updated_at') else 'N/A'
        assignees_str = ", ".join(issue.get('assignees', []))
        labels_str = ", ".join(issue.get('labels', []))

        row_values = (
            task_number,
            issue['title'],
            assignees_str,
            milestone,
            labels_str,
            issue['weight'],
            estimateHours,
            created_at_date,
            updated_at_date
        )
        app.current_display_data.append(row_values)

    apply_filters(app)


def apply_filters(app):
    selected_label = app.label_filter_combo.get()
    selected_milestone = app.milestone_filter_combo.get()
    selected_assignee = app.assignee_filter_combo.get()
    selected_has_actHour = app.has_actHour_filter_combo.get()
    selected_owner = app.owner_filter_combo.get()
    selected_ts_action = app.timesheet_action_filter_combo.get()

    # Step 1: Recalculate actual hours based on current timesheet filters
    filtered_actual_hours = {}
    for entry in getattr(app, 'task_entries', []):
        if selected_owner != "All" and entry['owner'] != selected_owner:
            continue
        if selected_ts_action != "All" and entry['action'] != selected_ts_action:
            continue

        task_id = entry['task_id']
        filtered_actual_hours[task_id] = filtered_actual_hours.get(task_id, 0) + entry['hours']

    # Step 2: Filter and display
    app.tree.delete(*app.tree.get_children())

    for row in app.current_display_data:
        (
            task_id, title, assignees_str, milestone,
            labels_str, weight, estimateHours,
            created_at, updated_at
        ) = row

        if selected_label != "All" and selected_label not in labels_str.split(', '):
            continue
        if selected_milestone != "All" and selected_milestone != milestone:
            continue
        if selected_assignee != "All" and selected_assignee not in assignees_str.split(', '):
            continue

        actualHour = filtered_actual_hours.get(task_id, 0)

        if selected_has_actHour == "Has Actual Hours" and actualHour == 0:
            continue
        if selected_has_actHour == "Missing Actual Hours" and actualHour != 0:
            continue

        app.tree.insert('', END, values=(
            task_id, title, assignees_str, milestone,
            labels_str, weight, estimateHours, actualHour,
            created_at, updated_at
        ))

