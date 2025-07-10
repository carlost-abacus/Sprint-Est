import pandas as pd
from tkinter import filedialog, messagebox
import xlsxwriter

def export_to_excel(app):
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save As Excel File"
        )
        if not file_path:
            return

        data_to_export = []
        for item_id in app.tree.get_children():
            values = app.tree.item(item_id)['values']
            # Reconstruct dict with column names for clarity in export
            row_data = {
                'Task ID': values[0], 'Title': values[1], 'Assignees': values[2],
                'Milestone': values[3], 'Labels': values[4], 'Est Points': values[5],
                'Est Hrs': values[6], 'Act Hrs': values[7], 'Created At': values[8],
                'Updated At': values[9]
            }
            data_to_export.append(row_data)

        if not data_to_export:
            messagebox.showinfo("Export Info", "No data to export (table is empty after filtering).")
            return

        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet('Report')

        # Write header
        header = list(data_to_export[0].keys())
        for col_num, header_text in enumerate(header):
            worksheet.write(0, col_num, header_text)

        # Write data rows
        for row_num, row_dict in enumerate(data_to_export):
            for col_num, header_text in enumerate(header):
                worksheet.write(row_num + 1, col_num, row_dict.get(header_text, ''))

        workbook.close()
        messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")

def export_to_csv(app):
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save As CSV File"
        )

        if not file_path:
            return

        data_to_export = []
        for item_id in app.tree.get_children():
            values = app.tree.item(item_id)['values']
            row_data = {
                'Task ID': values[0], 'Title': values[1], 'Assignees': values[2],
                'Milestone': values[3], 'Labels': values[4], 'Est Points': values[5],
                'Est Hrs': values[6], 'Act Hrs': values[7], 'Created At': values[8],
                'Updated At': values[9]
            }
            data_to_export.append(row_data)

        if not data_to_export:
            messagebox.showinfo("Export Info", "No data to export (table is empty after filtering).")
            return

        df = pd.DataFrame(data_to_export)
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Export Successful", f"Data exported to {file_path}")

    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")
