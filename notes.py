import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import os

class NotePad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad")

        # Path to the notes file
        self.notes_file = "notes.json"

        # Dictionary to store notes with titles as keys
        self.notes = {}

        # Load notes from file
        self.load_notes()

        # PanedWindow to make the title window adjustable in width
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        # Left frame for note titles with initial width
        self.left_frame = tk.Frame(self.paned_window, width=200)  # Set initial width
        self.paned_window.add(self.left_frame)

        self.listbox = tk.Listbox(self.left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=1)  # Make listbox fill the frame
        self.listbox.bind("<<ListboxSelect>>", self.show_note)

        self.scrollbar = tk.Scrollbar(self.left_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # Right frame for note content
        self.right_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame)

        self.title_label = tk.Label(self.right_frame, text="Title:")
        self.title_label.pack(anchor=tk.W)

        self.title_entry = tk.Entry(self.right_frame)
        self.title_entry.pack(fill=tk.X)

        self.content_text = tk.Text(self.right_frame)
        self.content_text.pack(fill=tk.BOTH, expand=1)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X)

        self.add_button = tk.Button(self.button_frame, text="Add Note", command=self.add_note)
        self.add_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.button_frame, text="Save Note", command=self.save_note)
        self.save_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.button_frame, text="Delete Note", command=self.delete_note)
        self.delete_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.button_frame, text="Clear Note", command=self.clear_note)
        self.clear_button.pack(side=tk.LEFT)

        # Populate the listbox with loaded notes
        self.populate_listbox()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r') as file:
                self.notes = json.load(file)

    def save_notes_to_file(self):
        with open(self.notes_file, 'w') as file:
            json.dump(self.notes, file)

    def populate_listbox(self):
        for title in self.notes.keys():
            self.listbox.insert(tk.END, title)

    def add_note(self):
        title = self.title_entry.get()
        content = self.content_text.get(1.0, tk.END).strip()

        if title and content:
            self.save_note()

        self.clear_note()
        self.title_entry.focus_set()

    def save_note(self):
        title = self.title_entry.get()
        content = self.content_text.get(1.0, tk.END).strip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if title:
            new_title = f"{title} ({current_time})"
            if title in self.notes:
                self.notes[title] = content
                # Update the listbox title with the new date and time
                idx = self.listbox.get(0, tk.END).index(title)
                self.listbox.delete(idx)
                self.listbox.insert(idx, new_title)
            else:
                self.listbox.insert(tk.END, new_title)
                self.notes[new_title] = content
            self.save_notes_to_file()
            self.clear_note()
        else:
            messagebox.showerror("Error", "Title cannot be empty.")

    def delete_note(self):
        selected_idx = self.listbox.curselection()
        if selected_idx:
            title = self.listbox.get(selected_idx)
            del self.notes[title]
            self.listbox.delete(selected_idx)
            self.save_notes_to_file()
            self.clear_note()
        else:
            messagebox.showerror("Error", "No note selected to delete.")

    def show_note(self, event):
        selected_idx = self.listbox.curselection()
        if selected_idx:
            title = self.listbox.get(selected_idx)
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(tk.END, title)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, self.notes[title])

    def clear_note(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotePad(root)
    root.mainloop()
