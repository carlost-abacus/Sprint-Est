from tkinter import Toplevel, Label

def show_loading_window(app):
    app.loading_window = Toplevel(app.master)
    app.loading_window.title("Loading")
    app.loading_window.geometry("300x185")
    Label(app.loading_window, text="Fetching Data from Gitlab...\nPlease wait.", font=("Arial", 12)).pack(expand=True)
    app.loading_window.grab_set()
    app.master.update_idletasks()

def hide_loading_window(app):
    if app.loading_window:
        app.loading_window.destroy()
        app.loading_window = None