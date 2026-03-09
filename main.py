import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# Internal Imports
from downloader.database import DatabaseManager
from downloader.settings import SettingsManager
from downloader.engine import DownloadEngine
from plugins.mediafire import MediafirePlugin

class PyDownerApp:
    """Main Application Class for PyDowner."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PyDowner")
        self.root.geometry("950x550")

        # 1. Initialize logic components
        self.settings = SettingsManager()
        self.db = DatabaseManager()
        
        # Initialize engine with the Mediafire plugin
        self.engine = DownloadEngine(
            db=self.db, 
            settings=self.settings, 
            plugins=[MediafirePlugin()]
        )

        # 2. Build the UI
        self._build_ui()
        
        # 3. Start the UI update loop (refreshes progress every second)
        self._tick()

    def _build_ui(self):
        """Creates all GUI widgets and layout."""
        
        # --- TOP BAR: Add Download ---
        top_frame = tk.Frame(self.root, pady=15)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="Download URL:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20, 5))
        self.url_input = tk.Entry(top_frame, width=65, font=("Arial", 10))
        self.url_input.pack(side=tk.LEFT, padx=5)
        
        add_btn = tk.Button(top_frame, text="Add Download", command=self.on_add, bg="#4caf50", fg="white", padx=10)
        add_btn.pack(side=tk.LEFT, padx=10)

        # --- SETTINGS BAR: Folder Path ---
        settings_bar = tk.Frame(self.root, bg="#f8f8f8", padx=20, pady=8)
        settings_bar.pack(fill=tk.X)
        
        self.path_lbl = tk.Label(
            settings_bar, 
            text=f"Saving to: {self.settings.get('default_folder')}", 
            bg="#f8f8f8", 
            font=("Arial", 8, "italic")
        )
        self.path_lbl.pack(side=tk.LEFT)
        
        change_btn = tk.Button(settings_bar, text="Change Folder", command=self.on_change_folder, font=("Arial", 8))
        change_btn.pack(side=tk.RIGHT)

        # --- MAIN TABLE: Treeview ---
        self.tree = ttk.Treeview(
            self.root, 
            columns=("file", "progress", "status", "speed"), 
            show="headings"
        )
        
        self.tree.heading("file", text="File Name")
        self.tree.heading("progress", text="Downloaded / Total")
        self.tree.heading("status", text="Status")
        self.tree.heading("speed", text="Speed")
        
        self.tree.column("file", width=350)
        self.tree.column("progress", width=180)
        self.tree.column("status", width=120)
        self.tree.column("speed", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- CONTEXT MENU (Right Click) ---
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Resume", command=self.on_resume)
        self.menu.add_command(label="Pause", command=self.on_pause)
        self.menu.add_command(label="Restart", command=self.on_restart)
        self.menu.add_separator()
        self.menu.add_command(label="Remove from List", command=lambda: self.on_delete(False))
        self.menu.add_command(label="Delete from List & Disk", command=lambda: self.on_delete(True))

        # --- EVENT BINDINGS ---
        # Right click to show menu
        self.tree.bind("<Button-3>", self.on_right_click)
        
        # GLOBAL CLICK: Hide menu when clicking anywhere else in the app
        self.root.bind("<Button-1>", lambda e: self.menu.unpost())

    # --- UI EVENT HANDLERS ---

    def on_right_click(self, event):
        """Displays the context menu at the mouse cursor position."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
            return "break"

    def on_add(self):
        """Adds a new URL to the queue."""
        url = self.url_input.get().strip()
        if url:
            self.engine.add_download(url)
            self.url_input.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a valid URL.")

    def on_change_folder(self):
        """Changes the default download location."""
        new_path = filedialog.askdirectory(initialdir=self.settings.get("default_folder"))
        if new_path:
            self.settings.set("default_folder", new_path)
            self.path_lbl.config(text=f"Saving to: {new_path}")

    def on_resume(self):
        """Resumes the selected download."""
        sel = self.tree.selection()
        if sel:
            self.engine.run_task(sel[0], restart=False)

    def on_pause(self):
        """Pauses the selected download."""
        sel = self.tree.selection()
        if sel:
            self.engine.pause_task(sel[0])

    def on_restart(self):
        """Wipes progress and restarts from 0%."""
        sel = self.tree.selection()
        if sel:
            if messagebox.askyesno("Restart", "Delete current file and start from 0%?"):
                self.engine.run_task(sel[0], restart=True)

    def on_delete(self, from_disk: bool):
        """Removes the task and optionally deletes the file from disk."""
        sel = self.tree.selection()
        if sel:
            tid = sel[0]
            msg = "Delete file from disk and remove from list?" if from_disk else "Remove task from list?"
            if messagebox.askyesno("Confirm Delete", msg):
                self.engine.delete_task(tid, delete_file=from_disk)
                self.tree.delete(tid)

    def _format_size(self, bytes_val: int) -> str:
        """Utility to convert bytes into human-readable MB."""
        return f"{bytes_val / (1024 * 1024):.1f} MB"

    def _tick(self):
        """Refreshes the Treeview table with latest data from the Engine."""
        for tid, task in self.engine.tasks.items():
            # Create a string for progress (e.g., 10MB / 50MB)
            total_str = self._format_size(task.total_size) if task.total_size > 0 else "?? MB"
            progress_str = f"{self._format_size(task.downloaded)} / {total_str}"
            
            vals = (task.filename, progress_str, task.status, task.speed)
            
            if self.tree.exists(tid):
                self.tree.item(tid, values=vals)
            else:
                self.tree.insert("", tk.END, iid=tid, values=vals)
        
        # Schedule the next update in 1000ms
        self.root.after(1000, self._tick)

if __name__ == "__main__":
    # Ensure any corrupted old database is not interfering
    # If you see SQL errors, delete 'downloads.db' manually.
    
    root = tk.Tk()
    app = PyDownerApp(root)
    root.mainloop()