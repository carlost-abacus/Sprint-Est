from tkinter import LabelFrame, Label, Button, Frame, Scrollbar
from tkinter import RIGHT, Y, BOTH, VERTICAL, LEFT
from tkinter.ttk import Combobox, Treeview
from tkinter import messagebox
from utils.export_util import export_to_excel, export_to_csv    
from services.timesheet_processor import apply_filters


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
    # Button(button_frame, text="Show Error Report", command=app.show_error_report).pack(side=LEFT, padx=5)
