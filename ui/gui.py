#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from core.queue_manager import QueueManager
from core.plugin_manager import PluginManager
from core.download_engine import download_file

class PyDownerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyDowner - GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.qm = QueueManager()
        self.pm = PluginManager()
        self.pm.load_all()
        
        self.setup_ui()
        self.url_to_iid = {}
        self.tree_status = {}
        self.tree.bind('<Button-3>', self.right_click_menu)

        self.refresh_loop()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="PyDowner - Downloader", 
                        font=("Arial", 18, "bold"), bg="#ecf0f1", pady=15)
        title.pack(fill=tk.X)
        
        # Input row
        input_frame = tk.Frame(self.root, bg="#ecf0f1", pady=10)
        input_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(input_frame, text="MediaFire URL:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', pady=12)
        self.url_entry = tk.Entry(input_frame, font=("Arial", 11), relief=tk.FLAT)
        self.url_entry.grid(row=0, column=1, sticky='ew', padx=(10,10), pady=12)
        self.url_entry.bind('<Return>', lambda e: self.add_url())
        
        tk.Label(input_frame, text="Folder:", font=("Arial", 11, "bold")).grid(row=0, column=2, sticky='w', padx=(0,5), pady=12)
        self.folder_var = tk.StringVar(value="downloads")
        folder_entry = tk.Entry(input_frame, textvariable=self.folder_var, width=25, relief=tk.FLAT)
        folder_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=12)
        
        self.browse_btn = tk.Button(input_frame, text="BROWSE", width=8,
                                   command=self.browse_folder, relief=tk.FLAT, bg="#95a5a6", fg="white")
        self.browse_btn.grid(row=0, column=4, padx=5, pady=12)
        
        self.add_btn = tk.Button(input_frame, text="ADD TO QUEUE", 
                                command=self.add_url, bg="#3498db", fg="white",
                                font=("Arial", 11, "bold"), relief=tk.FLAT, padx=20)
        self.add_btn.grid(row=0, column=5, padx=10, pady=12)
        
        input_frame.columnconfigure(1, weight=2)
        input_frame.columnconfigure(3, weight=1)
        
        # Control buttons
        btn_frame = tk.Frame(self.root, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0,10))
        
        self.start_btn = tk.Button(btn_frame, text="START QUEUE", 
                                  command=self.start_queue, bg="#27ae60", fg="white",
                                  font=("Arial", 13, "bold"), width=14, height=2, relief=tk.FLAT)
        self.start_btn.pack(side=tk.LEFT, padx=15)
        
        self.clear_btn = tk.Button(btn_frame, text="CLEAR COMPLETED", 
                                  command=self.clear_done, bg="#e74c3c", fg="white",
                                  font=("Arial", 13, "bold"), width=16, height=2, relief=tk.FLAT)
        self.clear_btn.pack(side=tk.LEFT, padx=15)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready - Add MediaFire URLs above", 
                                   font=("Arial", 12), bg="#ecf0f1", fg="#7f8c8d")
        self.status_label.pack(pady=8)

        # Add ACTUAL progress bar after status_label
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, 
                                        orient='horizontal', length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=20, pady=(0,10))

        
        # Queue table
        tk.Label(
            self.root, text="Download Queue:",
            font=("Arial", 13, "bold")
        ).pack(
                anchor='w', padx=20, pady=(20,5)
            )

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))

        columns = ('Status', 'File', 'Folder', 'Progress')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=16)

        self.tree.heading('Status', text='Status')
        self.tree.heading('File', text='File') 
        self.tree.heading('Folder', text='Folder')
        self.tree.heading('Progress', text='Progress')

        self.tree.column('Status', width=100, anchor='center')
        self.tree.column('File', width=320)
        self.tree.column('Folder', width=220)
        self.tree.column('Progress', width=100, anchor='center')

        # RIGHT CLICK DELETE
        self.tree.bind('<Button-3>', self.right_click_menu)  # Right click

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_status = {}

    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get() or "downloads")
        if folder:
            self.folder_var.set(folder)
    
    def add_url(self):
        url = self.url_entry.get().strip()
        folder = self.folder_var.get().strip()
        
        if not url or not folder:
            messagebox.showwarning("Input Error", "Enter URL and folder")
            return
        
        plugin = self.pm.find_plugin(url)
        if not plugin or plugin.name != "MediaFire":
            messagebox.showerror("Plugin Error", "Only MediaFire URLs supported")
            return
        
        try:
            info = plugin.resolve(url)
            result = self.qm.add(url)
            if "Added" in result:
                self.url_entry.delete(0, tk.END)
                self.refresh_list()
                self.status_label.config(text=f"Added: {info.filename} → {folder}")
            else:
                messagebox.showerror("Add Failed", result)
        except Exception as e:
            messagebox.showerror("Resolve Error", str(e))
    
    def start_queue(self):
        pending = [item for item in self.qm.items.values() if item.status == "pending"]
        if not pending:
            messagebox.showwarning("Queue Empty", "No pending downloads")
            return
        
        self.start_btn.config(state='disabled')
        self.status_label.config(text="Starting downloads...")
        threading.Thread(target=self.download_loop, daemon=True).start()
    
    def download_loop(self):
        for url in list(self.qm.items.keys()):
            item = self.qm.items[url]
            if item.status != "pending":
                continue
            
            item.status = "downloading"
            self.root.after(0, self.refresh_list)
            
            def progress_cb(pct, filename):
                self.root.after(0, lambda: self.update_progress(url, pct, filename))
            
            try:
                success = download_file(item.info, on_progress=progress_cb)
                item.status = "completed" if success else "failed"
            except:
                item.status = "failed"
            
            self.root.after(0, self.refresh_list)


    def update_progress(self, url, pct, filename):
        self.tree_status[url] = f"{pct:.0f}%"
        self.progress_var.set(pct / 100)  # ACTUAL progress bar!
        self.status_label.config(text=f"{filename} {pct:.0f}%")
        self.root.update()  # Force GUI update [web:56]
        self.refresh_list()

    
    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        self.url_to_iid.clear()
        
        for url, item in self.qm.items.items():
            status = item.status.replace('pending', 'Waiting').replace('downloading', 'Active').replace('completed', 'Done').replace('failed', 'Error')
            progress = self.tree_status.get(url, '0%')
            folder = "downloads"
            iid = self.tree.insert('', 'end', values=(status, item.info.filename, folder, progress))
            self.url_to_iid[url] = iid
    
    def refresh_loop(self):
        self.refresh_list()
        self.root.after(1500, self.refresh_loop)
    
    def clear_done(self):
        self.qm.items = {k: v for k, v in self.qm.items.items() if v.status != "completed"}
        self.qm.save()
        self.refresh_list()
        self.status_label.config(text="Cleared completed downloads")
    
    def right_click_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Delete", command=lambda i=item: self.action_delete(i))
            menu.add_command(label="Pause", command=lambda i=item: self.action_pause(i))
            menu.add_command(label="Restart", command=lambda i=item: self.action_restart(i))
            menu.tk_popup(event.x_root, event.y_root)

    def action_delete(self, iid):
        for url, tree_iid in list(self.url_to_iid.items()):
            if tree_iid == iid:
                del self.qm.items[url]
                self.qm.save()
                self.refresh_list()
                self.status_label.config(text="Deleted")
                break

    def action_pause(self, iid):
        for url, tree_iid in list(self.url_to_iid.items()):
            if tree_iid == iid:
                self.qm.items[url].status = "paused"
                self.qm.save()
                self.refresh_list()
                self.status_label.config(text="Paused")
                break

    def action_restart(self, iid):
        for url, tree_iid in list(self.url_to_iid.items()):
            if tree_iid == iid:
                self.qm.items[url].status = "pending"
                self.tree_status.pop(url, None)
                self.qm.save()
                self.refresh_list()
                self.status_label.config(text="Restarted")
                break


def main():
    root = tk.Tk()
    app = PyDownerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
