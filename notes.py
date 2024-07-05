import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
import json
import os
import webbrowser
import re

class NotePad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad")
        self.border_width = 19
        self.notes_file = "notes.json"
        self.notes = {}
        self.current_category = ""
        self.current_note_title_with_date = ""
        self.is_auto_saving = False

        self.setup_ui()
        self.center_window()
        self.load_notes()
        self.populate_categories()
        self.create_context_menu()
        self.start_auto_save()

    def setup_ui(self):
        self.root.geometry("1200x600")
        self.main_frame = tk.Frame(self.root, padx=self.border_width, pady=self.border_width)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.paned_window = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.setup_left_frame()
        self.setup_right_frame()

    def setup_left_frame(self):
        self.left_frame = tk.Frame(self.paned_window, width=400)
        self.paned_window.add(self.left_frame)

        self.category_frame = tk.Frame(self.left_frame)
        self.category_frame.pack(fill=tk.X)

        self.category_label = tk.Label(self.category_frame, text="Category:")
        self.category_label.pack(side=tk.LEFT)

        self.category_combobox = ttk.Combobox(self.category_frame, state="readonly")
        self.category_combobox.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.category_combobox.bind("<<ComboboxSelected>>", self.change_category)

        self.new_category_button = tk.Button(self.category_frame, text="New Category", command=self.new_category)
        self.new_category_button.pack(side=tk.LEFT)

        self.delete_category_button = tk.Button(self.category_frame, text="Delete Category", command=self.delete_category)
        self.delete_category_button.pack(side=tk.RIGHT)

        self.sort_frame = tk.Frame(self.left_frame)
        self.sort_frame.pack(fill=tk.X)

        self.sort_alpha_button = tk.Button(self.sort_frame, text="Sort Alphabetically", command=self.sort_notes_alphabetically)
        self.sort_alpha_button.pack(side=tk.LEFT)

        self.sort_date_button = tk.Button(self.sort_frame, text="Sort by Date", command=self.sort_notes_by_date)
        self.sort_date_button.pack(side=tk.RIGHT)

        self.listbox = tk.Listbox(self.left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=1)
        self.listbox.bind("<<ListboxSelect>>", self.show_note)

    def setup_right_frame(self):
        self.right_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame)

        self.title_frame = tk.Frame(self.right_frame)
        self.title_frame.pack(fill=tk.X)

        self.title_label = tk.Label(self.title_frame, text="Title:")
        self.title_label.pack(side=tk.LEFT)

        self.title_entry = tk.Entry(self.title_frame)
        self.title_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.title_entry.bind("<Button-3>", self.show_context_menu)

        self.content_text = tk.Text(self.right_frame, wrap=tk.WORD, undo=True, autoseparators=True, maxundo=-1)
        self.content_text.pack(fill=tk.BOTH, expand=1)
        self.content_text.tag_configure("link", foreground="blue", underline=True)
        self.content_text.tag_bind("link", "<Control-Button-1>", self.open_link)
        self.content_text.bind("<Button-3>", self.show_context_menu)

        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.pack(fill=tk.X)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_note)
        self.save_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_note)
        self.delete_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear_note, width=20)
        self.clear_button.pack(side=tk.LEFT, padx=(180, 0))

        self.always_on_top_var = tk.IntVar()
        self.always_on_top_checkbutton = tk.Checkbutton(self.button_frame, text="Always on Top",
                                                        variable=self.always_on_top_var, command=self.toggle_always_on_top)
        self.always_on_top_checkbutton.pack(side=tk.RIGHT)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.content_text, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_command(label="Delete", command=self.delete_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Undo", command=self.undo_text)
        self.context_menu.add_command(label="Redo", command=self.redo_text)

    def show_context_menu(self, event):
        self.context_menu.widget = event.widget
        self.context_menu.post(event.x_root, event.y_root)

    def cut_text(self):
        self.context_menu.widget.event_generate("<<Cut>>")

    def copy_text(self):
        self.context_menu.widget.event_generate("<<Copy>>")

    def paste_text(self):
        self.context_menu.widget.event_generate("<<Paste>>")

    def delete_text(self):
        self.context_menu.widget.delete("sel.first", "sel.last")

    def select_all_text(self):
        self.context_menu.widget.tag_add("sel", "1.0", "end")

    def undo_text(self):
        self.context_menu.widget.event_generate("<<Undo>>")

    def redo_text(self):
        self.context_menu.widget.event_generate("<<Redo>>")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r') as file:
                    self.notes = json.load(file)
                    self.convert_old_notes_format()
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Error", f"Failed to load notes: {e}")

    def save_notes_to_file(self):
        try:
            with open(self.notes_file, 'w') as file:
                json.dump(self.notes, file, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save notes: {e}")

    def convert_old_notes_format(self):
        for category, notes in self.notes.items():
            for title, content in notes.items():
                if isinstance(content, str):
                    self.notes[category][title] = {
                        'content': content,
                        'date': datetime.now().isoformat()
                    }

    def populate_categories(self):
        self.category_combobox['values'] = list(self.notes.keys())

    def change_category(self, event):
        self.auto_save_note()
        self.current_category = self.category_combobox.get()
        self.populate_notes()
        self.clear_note()

    def populate_notes(self):
        self.listbox.delete(0, tk.END)
        if self.current_category in self.notes:
            for title in self.notes[self.current_category]:
                self.listbox.insert(tk.END, title)

    def new_category(self):
        category = simpledialog.askstring("New Category", "Enter category name:")
        if category and category not in self.notes:
            self.notes[category] = {}
            self.save_notes_to_file()
            self.populate_categories()

    def delete_category(self):
        if self.current_category:
            del self.notes[self.current_category]
            self.save_notes_to_file()
            self.populate_categories()
            self.listbox.delete(0, tk.END)
            self.current_category = ""

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        if title and self.current_category:
            if self.current_category not in self.notes:
                self.notes[self.current_category] = {}
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title_with_date = f"{title} ({date_str})"
            self.notes[self.current_category][title_with_date] = {'content': content, 'date': date_str}
            if title_with_date not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, title_with_date)
            self.current_note_title_with_date = title_with_date
            self.save_notes_to_file()
            self.clear_note()
        else:
            messagebox.showerror("Error", "Title cannot be empty or no category selected.")

    def delete_note(self):
        selected_idx = self.listbox.curselection()
        if selected_idx:
            title = self.listbox.get(selected_idx)
            del self.notes[self.current_category][title]
            self.listbox.delete(selected_idx)
            self.save_notes_to_file()
            self.clear_note()
        else:
            messagebox.showerror("Error", "No note selected to delete.")

    def show_note(self, event):
        self.auto_save_note()
        selected_idx = self.listbox.curselection()
        if selected_idx:
            self.is_auto_saving = False  # Temporarily disable auto-save
            title_with_date = self.listbox.get(selected_idx)
            title = title_with_date.rsplit(' (', 1)[0]  # Remove the date part for the title entry
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(tk.END, title)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, self.notes[self.current_category][title_with_date]['content'])
            self.current_note_title_with_date = title_with_date
            self.highlight_links()
            self.is_auto_saving = True  # Re-enable auto-save

    def clear_note(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete(1.0, tk.END)
        self.current_note_title_with_date = ""

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.always_on_top_var.get())

    def highlight_links(self):
        content = self.content_text.get(1.0, tk.END)
        self.content_text.mark_set("matchStart", 1.0)
        self.content_text.mark_set("matchEnd", 1.0)
        self.content_text.mark_set("searchLimit", tk.END)

        pattern = r"https?://[^\s]+"
        for match in re.finditer(pattern, content):
            start, end = match.span()
            start_index = self.content_text.index(f"1.0 + {start} chars")
            end_index = self.content_text.index(f"1.0 + {end} chars")
            self.content_text.tag_add("link", start_index, end_index)

    def open_link(self, event):
        index = self.content_text.index("@%s,%s" % (event.x, event.y))
        ranges = self.content_text.tag_prevrange("link", index)
        if ranges:
            url = self.content_text.get(ranges[0], ranges[1])
            webbrowser.open(url)

    def auto_save_note(self):
        if not self.is_auto_saving:
            return
        title = self.title_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        if title and self.current_category and self.current_note_title_with_date:
            date_str = self.current_note_title_with_date.rsplit(' (', 1)[1].strip(')')
            title_with_date = f"{title} ({date_str})"
            del self.notes[self.current_category][self.current_note_title_with_date]
            self.notes[self.current_category][title_with_date] = {'content': content, 'date': date_str}
            if title_with_date not in self.listbox.get(0, tk.END):
                self.listbox.insert(tk.END, title_with_date)
            self.current_note_title_with_date = title_with_date
            self.save_notes_to_file()

    def start_auto_save(self):
        self.is_auto_saving = True
        self.auto_save_note()
        self.root.after(60000, self.start_auto_save)  # Save every 60 seconds

    def sort_notes_alphabetically(self):
        if self.current_category in self.notes:
            sorted_titles = sorted(self.notes[self.current_category].keys())
            self.listbox.delete(0, tk.END)
            for title in sorted_titles:
                self.listbox.insert(tk.END, title)

    def sort_notes_by_date(self):
        if self.current_category in self.notes:
            sorted_titles = sorted(self.notes[self.current_category].items(), key=lambda item: datetime.strptime(item[1]['date'], "%Y-%m-%d %H:%M:%S"), reverse=True)
            self.listbox.delete(0, tk.END)
            for title, _ in sorted_titles:
                self.listbox.insert(tk.END, title)

if __name__ == "__main__":
    root = tk.Tk()
    app = NotePad(root)
    root.mainloop()
