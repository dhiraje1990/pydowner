import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core import DownloadManager

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenDownloader")
        self.root.geometry("800x500")
        self.manager = DownloadManager()

        # UI Setup
        header = tk.Frame(root, pady=10)
        header.pack(fill=tk.X)
        self.url_var = tk.StringVar()
        tk.Entry(header, textvariable=self.url_var, width=60).pack(side=tk.LEFT, padx=10)
        tk.Button(header, text="Add Download", command=self.add_dl).pack(side=tk.LEFT)
        tk.Button(header, text="Settings", command=self.open_settings).pack(side=tk.RIGHT, padx=10)

        # Table
        self.tree = ttk.Treeview(root, columns=("id", "file", "size", "progress", "status", "speed"), show="headings")
        self.tree.heading("file", text="Filename")
        self.tree.heading("size", text="Size")
        self.tree.heading("progress", text="Downloaded")
        self.tree.heading("status", text="Status")
        self.tree.heading("speed", text="Speed")
        self.tree.column("id", width=0, stretch=False)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Context Menu
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Resume (Continue)", command=self.resume_dl)
        self.menu.add_command(label="Restart (From 0%)", command=self.restart_dl)
        self.menu.add_command(label="Pause", command=self.pause_dl)
        self.menu.add_separator()
        self.menu.add_command(label="Delete from List", command=lambda: self.delete_dl(False))
        self.menu.add_command(label="Delete from List & Disk", command=lambda: self.delete_dl(True))

        # FIX: Bindings
        self.tree.bind("<Button-3>", self.show_menu) # Right click
        # The magic fix: Clicking anywhere on the root window or tree hides the menu
        self.root.bind("<Button-1>", self.hide_menu) 
        
        self.refresh_ui()
        self.load_existing()

    def hide_menu(self, event=None):
        self.menu.unpost()

    def show_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
            return "break" # Prevents system focus issues

    def add_dl(self):
        url = self.url_var.get().strip()
        if url:
            self.manager.add_download(url)
            self.url_var.set("")
            self.load_existing()

    def resume_dl(self):
        sel = self.tree.selection()
        if sel: self.manager.start_download(sel[0], restart=False)

    def restart_dl(self):
        sel = self.tree.selection()
        if sel: 
            if messagebox.askyesno("Restart", "This will delete the partial file and start over. Continue?"):
                self.manager.start_download(sel[0], restart=True)

    def pause_dl(self):
        sel = self.tree.selection()
        if sel: self.manager.pause_download(sel[0])

    def delete_dl(self, from_disk):
        sel = self.tree.selection()
        if sel:
            self.manager.delete_download(sel[0], delete_file=from_disk)
            self.tree.delete(sel[0])

    def open_settings(self):
        path = filedialog.askdirectory()
        if path:
            self.manager.settings["default_folder"] = path
            self.manager.save_settings()

    def load_existing(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for id, info in self.manager.downloads.items():
            self.tree.insert("", tk.END, iid=id, values=(id, info["filename"], info["size"], info["downloaded"], info["status"], info["speed"]))

    def refresh_ui(self):
        for id, info in self.manager.downloads.items():
            if self.tree.exists(id):
                self.tree.item(id, values=(id, info["filename"], info["size"], info["downloaded"], info["status"], info["speed"]))
        self.root.after(1000, self.refresh_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()