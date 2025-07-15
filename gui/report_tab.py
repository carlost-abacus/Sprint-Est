from tkinter import LabelFrame, Label, Button, Frame, Scrollbar, Toplevel, Text, StringVar, Entry, Checkbutton, BooleanVar
from tkinter import RIGHT, Y, BOTH, VERTICAL, LEFT, WORD, END, DISABLED, X
from tkinter.ttk import Combobox, Treeview
from utils.export_util import export_to_excel, export_to_csv, send_email
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
    app.has_actHour_filter_combo = Combobox(filter_frame, values=["All", "Has Actual Hours", "Missing Actual Hours"], state="readonly", width=25)
    app.has_actHour_filter_combo.set("All")
    app.has_actHour_filter_combo.grid(row=1, column=3, padx=5, pady=2, sticky="ew")

    Label(filter_frame, text="Timesheet Owner:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
    app.owner_filter_combo = Combobox(filter_frame, values=["All"], state="readonly", width=25)
    app.owner_filter_combo.set("All")
    app.owner_filter_combo.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

    Label(filter_frame, text="Timesheet Action:").grid(row=2, column=2, padx=5, pady=2, sticky="w")
    app.timesheet_action_filter_combo = Combobox(filter_frame, values=["All"], state="readonly", width=25)
    app.timesheet_action_filter_combo.set("All")
    app.timesheet_action_filter_combo.grid(row=2, column=3, padx=5, pady=2, sticky="ew")


    # Apply Filters Button
    Button(filter_frame, text="Apply Filters", command=lambda: apply_filters(app)).grid(row=3, column=0, columnspan=4, pady=5)
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
    Button(button_frame, text="Show Error Report", command=lambda: open_error_email_ui(app)).pack(side=LEFT, padx=5)

def open_error_email_ui(app):
    error_window = Toplevel(app.master)
    error_window.title("Send Time Sheet Error Reports")
    error_window.geometry("500x500")
    error_window.transient(app.master)
    error_window.grab_set()

    Label(error_window, text="Owner", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
    Label(error_window, text="Email Address", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)
    Label(error_window, text="# Errors", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)
    Label(error_window, text="Preview", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5)
    Label(error_window, text="Send?", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5)

    # Keep references to entries and checkboxes
    owner_email_entries = {}
    send_flags = {}

    for idx, (owner, errors) in enumerate(app.time_sheet_errors.items(), start=1):
        Label(error_window, text=owner).grid(row=idx, column=0, sticky="w", padx=5)

        email_var = StringVar()
        Entry(error_window, textvariable=email_var, width=35).grid(row=idx, column=1, padx=5)
        owner_email_entries[owner] = email_var

        Label(error_window, text=str(len(errors))).grid(row=idx, column=2)

        Button(
            error_window,
            text="Preview",
            command=lambda o=owner: preview_owner_errors(o, app, error_window)
        ).grid(row=idx, column=3, padx=5)

        send_var = BooleanVar(value=True)
        Checkbutton(error_window, variable=send_var).grid(row=idx, column=4)
        send_flags[owner] = send_var

    def send_reports():
        for owner, errors in app.time_sheet_errors.items():
            if send_flags[owner].get():
                email = owner_email_entries[owner].get().strip()
                if not email:
                    messagebox.showwarning("Missing Email", f"Email for '{owner}' is missing.")
                    continue
                try:
                    send_email(app, owner, email, errors)
                except Exception as e:
                    messagebox.showerror("Send Failed", f"Failed to send to {email}.\nError: {e}")
        messagebox.showinfo("Done", "Emails sent (or attempted) for all selected owners.")

    Button(error_window, text="Send Emails", command=send_reports).grid(row=idx + 1, column=0, columnspan=5, pady=10)


def preview_owner_errors(owner, app, parent_window=None):
    preview_win = Toplevel(parent_window or app.master)
    preview_win.title(f"Errors for {owner}")
    preview_win.geometry("1000x400")
    preview_win.transient(parent_window or app.master)  # Set window parent
    preview_win.grab_set()  # Makes this preview window modal relative to parent

    text = Text(preview_win, wrap=WORD)
    text.pack(expand=True, fill=BOTH, padx=10, pady=10)
    errors = app.time_sheet_errors.get(owner, [])
    text.insert(END, f"Error Report for {owner}:\n\n")
    for line in errors:
        text.insert(END, f"- {line}\n")
    text.config(state=DISABLED)

    # Optional: Close button
    Button(preview_win, text="Close", command=preview_win.destroy).pack(pady=5)