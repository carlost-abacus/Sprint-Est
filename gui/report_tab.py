from tkinter import LabelFrame, Label, Button, Frame, Scrollbar, Toplevel, Text
from tkinter import RIGHT, Y, BOTH, VERTICAL, LEFT, WORD, END, DISABLED
from tkinter.ttk import Combobox, Treeview
from utils.export_util import export_to_excel, export_to_csv    
from services.timesheet_processor import apply_filters
from tkinter import messagebox


def setup_report_ui(app):
    frame = app.report_frame
    # Filtering Section
    filter_frame = LabelFrame(frame, text="Filters", padx=10, pady=10)
    filter_frame.pack(padx=10, pady=5, fill="x")

    # Filter by Label
    Label(filter_frame, text="Label:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    app.label_filter_combo = Combobox(filter_frame, values=["All"], state="readonly", width=25)
    app.label_filter_combo.set("All")
    app.label_filter_combo.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

    # Filter by Milestone
    Label(filter_frame, text="Milestone:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
    app.milestone_filter_combo = Combobox(filter_frame, values=["All"], state="readonly", width=25)
    app.milestone_filter_combo.set("All")
    app.milestone_filter_combo.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

    # Filter by Assignee
    Label(filter_frame, text="Assignee:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
    app.assignee_filter_combo = Combobox(filter_frame, values=["All"], state="readonly", width=25)
    app.assignee_filter_combo.set("All")
    app.assignee_filter_combo.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

    # Filter by Actual Hours Action
    Label(filter_frame, text="Actual Hours:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
    app.action_filter_combo = Combobox(filter_frame, values=["All", "Has Actual Hours", "Missing Actual Hours"], state="readonly", width=25)
    app.action_filter_combo.set("All")
    app.action_filter_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")

    # Apply Filters Button
    Button(filter_frame, text="Apply Filters", command= lambda: apply_filters(app)).grid(row=2, column=0, columnspan=4, pady=5)
    filter_frame.columnconfigure(1, weight=1)
    filter_frame.columnconfigure(3, weight=1)


    # Report Table Section
    report_table_frame = Frame(frame)
    report_table_frame.pack(padx=10, pady=5, expand=True, fill="both")

    columns = ['iid', 'title', 'assignees', 'milestone', 'labels', 'weight', 'estimateHours', 'actualHours', 'created_at', 'updated_at']
    app.tree = Treeview(report_table_frame, columns=columns, show='headings')

    app.tree.heading('iid', text='Task ID')
    app.tree.heading('title', text='Title')
    app.tree.heading('assignees', text='Assignees')
    app.tree.heading('milestone', text='Milestone')
    app.tree.heading('labels', text='Labels')
    app.tree.heading('weight', text='Est Points')
    app.tree.heading('estimateHours', text='Est Hrs')
    app.tree.heading('actualHours', text='Act Hrs')
    app.tree.heading('created_at', text='Created At')
    app.tree.heading('updated_at', text='Updated At')

    for col in columns:
        app.tree.column(col, width=100, stretch=True) # Default width

    app.tree.column('iid', width=60)
    app.tree.column('title', width=250)
    app.tree.column('assignees', width=120)
    app.tree.column('milestone', width=100)
    app.tree.column('labels', width=120)
    app.tree.column('weight', width=70)
    app.tree.column('estimateHours', width=60)
    app.tree.column('actualHours', width=60)
    app.tree.column('created_at', width=90)
    app.tree.column('updated_at', width=90)


    scrollbar_y = Scrollbar(report_table_frame, orient=VERTICAL, command=app.tree.yview)
    scrollbar_y.pack(side=RIGHT, fill=Y)
    app.tree.configure(yscrollcommand=scrollbar_y.set)
    app.tree.pack(fill=BOTH, expand=True)

    # Export and Error Report Buttons
    button_frame = Frame(frame)
    button_frame.pack(pady=10)

    Button(button_frame, text="Export to Excel", command=export_to_excel).pack(side=LEFT, padx=5)
    Button(button_frame, text="Export to CSV", command=export_to_csv).pack(side=LEFT, padx=5)
    Button(button_frame, text="Show Error Report", command=lambda: show_error_report(app)).pack(side=LEFT, padx=5)


def show_error_report(app):
    if not app.time_sheet_errors:
        messagebox.showinfo("Error Report", "No time sheet errors found from the last data fetch.")
        return

    error_report_window = Toplevel(app.master)
    error_report_window.title("Time Sheet Error Report")
    error_report_window.geometry("700x500")
    error_report_window.transient(app.master) # Make it appear on top of main window
    error_report_window.grab_set() # Make it modal

    text_area = Text(error_report_window, wrap=WORD, font=("Arial", 10))
    text_area.pack(expand=True, fill=BOTH, padx=10, pady=10)

    report_content = "Time Sheet Processing Errors:\n\n"
    if not app.time_sheet_errors:
        report_content += "No errors to report."
    else:
        for owner, errors in app.time_sheet_errors.items():
            report_content += f"--- Owner/File: {owner if owner else 'Unknown'} ---\n"
            for error in errors:
                report_content += f"- {error}\n"
            report_content += "\n"
    text_area.insert(END, report_content)
    text_area.config(state=DISABLED)

    def copy_to_clipboard():
        error_report_window.clipboard_clear()
        error_report_window.clipboard_append(report_content)
        messagebox.showinfo("Copied", "Error report copied to clipboard.")

    copy_btn = Button(error_report_window, text="Copy to Clipboard", command=copy_to_clipboard)
    copy_btn.pack(pady=5)

    # Allow user to close
    close_btn = Button(error_report_window, text="Close", command=error_report_window.destroy)
    close_btn.pack(pady=5)