import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from core import DownloadManager

class DownloadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenDownloader - Modular Download Manager")
        self.root.geometry("850x450")
        
        self.manager = DownloadManager()
        
        self.setup_ui()
        self.populate_existing_downloads()
        
        # Start UI Polling Loop
        self.update_ui()
        
        # Ensure clean exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Top Frame (URL Entry & Buttons)
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)
        
        tk.Label(top_frame, text="URL:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top_frame, width=60)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Add Download", command=self.add_download).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Settings", command=self.open_settings).pack(side=tk.RIGHT)

        # Middle Frame (Treeview)
        tree_frame = tk.Frame(self.root, padx=10, pady=5)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "filename", "size", "downloaded", "status", "speed")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=0, stretch=tk.NO) # Hide ID column
        
        self.tree.heading("filename", text="File Name")
        self.tree.column("filename", width=250)
        
        self.tree.heading("size", text="Total Size")
        self.tree.column("size", width=100)
        
        self.tree.heading("downloaded", text="Downloaded")
        self.tree.column("downloaded", width=100)
        
        self.tree.heading("status", text="Status")
        self.tree.column("status", width=100)
        
        self.tree.heading("speed", text="Speed")
        self.tree.column("speed", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Right Click Context Menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Resume / Restart", command=self.resume_selected)
        self.context_menu.add_command(label="Pause", command=self.pause_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

    def format_size(self, bytes_size):
        if bytes_size == 0: return "Unknown"
        for unit in['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0

    def add_download(self):
        url = self.url_entry.get().strip()
        if url:
            dl_id = self.manager.add_download(url)
            self.tree.insert("", tk.END, iid=dl_id, values=(dl_id, "Resolving...", "0", "0", "Queued", "0 KB/s"))
            self.url_entry.delete(0, tk.END)

    def populate_existing_downloads(self):
        for dl_id, info in self.manager.downloads.items():
            f_size = self.format_size(info['size'])
            f_down = self.format_size(info['downloaded'])
            self.tree.insert("", tk.END, iid=dl_id, values=(dl_id, info['filename'], f_size, f_down, info['status'], info['speed']))

    def update_ui(self):
        """Polls the DownloadManager for state changes and updates Treeview"""
        for dl_id, info in self.manager.downloads.items():
            if self.tree.exists(dl_id):
                f_size = self.format_size(info['size'])
                f_down = self.format_size(info['downloaded'])
                self.tree.item(dl_id, values=(dl_id, info['filename'], f_size, f_down, info['status'], info['speed']))
        
        self.root.after(1000, self.update_ui) # Poll every 1 second

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_id(self):
        selected = self.tree.selection()
        if selected:
            return selected[0] # Returns the iid (which is dl_id)
        return None

    def resume_selected(self):
        dl_id = self.get_selected_id()
        if dl_id:
            self.manager.start_download(dl_id)

    def pause_selected(self):
        dl_id = self.get_selected_id()
        if dl_id:
            self.manager.pause_download(dl_id)

    def delete_selected(self):
        dl_id = self.get_selected_id()
        if dl_id:
            if messagebox.askyesno("Delete", "Delete file from disk as well?"):
                self.manager.delete_download(dl_id, delete_file=True)
            else:
                self.manager.delete_download(dl_id, delete_file=False)
            self.tree.delete(dl_id)

    def open_settings(self):
        # Very basic settings dialog
        new_dir = filedialog.askdirectory(initialdir=self.manager.settings["default_folder"], title="Select Default Download Folder")
        if new_dir:
            self.manager.settings["default_folder"] = new_dir
            self.manager.save_settings()
            messagebox.showinfo("Settings", f"Default folder updated to:\n{new_dir}")

    def on_close(self):
        self.manager.save_downloads()
        self.manager.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloadApp(root)
    root.mainloop()