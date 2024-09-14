import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from ultis import find_duplicate_files
import threading
from tkinter import ttk
import os
from constants import *

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_folder = tk.StringVar()
        self.title("Simple Remove Duplicate Files App")
        self.geometry('600x150')
        self.resizable(False, False)
        self.configure(bg=BG_ROOT_COLOR)
        self.location_label = tk.Label(self, text='Location: ', font=('arial', 13),
                                        bg=BG_ROOT_COLOR)
        self.location_label.place(relx=0.05, rely=0.1)
        self.location_entry = tk.Entry(self, state=tk.DISABLED, textvariable=self.root_folder)
        self.location_entry.place(relx=0.2, rely=0.1, height=25, width=400)
        self.browse_folder_btn = tk.Button(self, text='📂', font=('arial', 13), command=self.open_folder)
        self.browse_folder_btn.place(relx=0.9, rely=0.07)
        self.progress_value = tk.Label(self, text='0%', font=('arial', 13), bg=BG_ROOT_COLOR)
        self.progress_label = tk.Label(self, text='Progress: ', font=('arial', 13), bg=BG_ROOT_COLOR)
        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=400)
        self.progress_value.place(relx=0.9, rely=0.35)
        self.progress_bar.place(relx=0.2, rely=0.35)
        self.progress_label.place(relx=0.05, rely=0.35)
        self.scan_btn = tk.Button(self, text='Scan', font=('arial', 13), state=tk.DISABLED, command=self.run_scan)
        self.scan_btn.place(relx=0.5, rely=0.75, anchor='center')
        self.files_list = None
        self.top_level_window = None

    def open_folder(self):
        path = askdirectory(title='Select Folder')
        if path == "":
            self.root_folder.set("")
            self.scan_btn.configure(state=tk.DISABLED)
        else:
            self.root_folder.set(path)
            self.scan_btn.configure(state=tk.NORMAL)

    def remove_selected_duplicate_files(self):
        selected_indices = self.files_list.curselection()
        duplicates_count = len(selected_indices)

        if duplicates_count == 0:
            messagebox.showwarning("No file selected!","Please select files to delete!",
                                   parent=self.top_level_window)
        else:
            choice = messagebox.askyesno("Confirm",
                                         f"Are you sure you want to delete {duplicates_count} selected files?",
                                         parent=self.top_level_window)
            if choice:
                for index in reversed(selected_indices):
                    try:
                        os.remove(self.files_list.get(index))
                        self.files_list.delete(index)
                    except OSError as e:
                        messagebox.showerror("Can't delete this file!", f"Error: {e}",
                                             parent=self.top_level_window)
                        duplicates_count -= 1
                messagebox.showinfo("Result", f"Successfully deleted {duplicates_count} duplicate files",
                                    parent=self.top_level_window)

        if self.files_list.size() == 0:
            self.top_level_window.destroy()

    def remove_all_duplicate_files(self):
        duplicates_count = self.files_list.size()
        choice = messagebox.askyesno("Result",
                                     f"{duplicates_count} duplicate files found. Do you want to delete it?",
                                     parent=self.top_level_window)
        if choice:
            for duplicate in self.files_list.get(0, tk.END):
                try:
                    os.remove(duplicate)
                except OSError as e:
                    messagebox.showerror("Can't delete this file!", f"Error: {e}",
                                         parent=self.top_level_window)
                    duplicates_count -= 1
            messagebox.showinfo("Result", f"Successfully deleted {duplicates_count} duplicate files",
                                parent=self.top_level_window)
            self.top_level_window.destroy()

    def scan_duplicate_files(self):
        self.scan_btn.configure(state=tk.DISABLED)
        duplicates = find_duplicate_files(self.root_folder.get(), self.progress_bar, self.progress_value)
        self.root_folder.set("")
        if len(duplicates) == 0:
            messagebox.showinfo("Result", "No duplicate files found.")
        else:
            self.top_level_window = tk.Toplevel(bg=BG_ROOT_COLOR)
            self.top_level_window.title("Results")
            self.top_level_window.geometry('600x300')
            self.top_level_window.resizable(False, False)
            remove_selected_btn = tk.Button(self.top_level_window, text="Remove Selected Files", font=('arial', 13),
                                            command=self.remove_selected_duplicate_files)
            remove_selected_btn.place(relx=0.2, rely=0.75)
            remove_all_btn = tk.Button(self.top_level_window, text="Remove All Files", font=('arial', 13),
                                       command=self.remove_all_duplicate_files)
            remove_all_btn.place(relx=0.57, rely=0.75)
            list_frame = tk.Frame(self.top_level_window)
            list_frame.pack(fill=tk.X, padx=20, pady=20)
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.files_list = tk.Listbox(list_frame, height=10, selectmode=tk.MULTIPLE, activestyle=tk.NONE,
                                         bg=LIST_COLOR)
            for index, duplicate in enumerate(duplicates):
                self.files_list.insert(index, duplicate)
            self.files_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.files_list.configure(yscrollcommand=scrollbar.set)
            scrollbar.configure(command=self.files_list.yview)

    def run_scan(self):
        scan_thread = threading.Thread(target=self.scan_duplicate_files)
        scan_thread.start()

if __name__ == "__main__":
    app = App()
    app.mainloop()