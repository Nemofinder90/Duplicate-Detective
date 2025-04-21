import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import os
import hashlib
import threading
import time
# --- For Icon ---
from PIL import Image # Make sure Pillow is installed: pip install Pillow

# --- Main Application Class ---
class DuplicateDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Detective")
        self.root.geometry("1050x700")

        # --- Core Variables ---
        self.folders_to_scan = []
        self.duplicates_data = {}

        # --- Font Setup ---
        self._setup_fonts() # Call the font setup method

        # --- Style Setup (for ttk Treeview) ---
        self.style = ttk.Style()
        self.style.theme_use("default")

        # --- Build UI ---
        self._setup_ui() # Call the UI setup method

        # --- Initialize Theme and Styles ---
        self._apply_initial_theme() # Call the theme setup method

    def _setup_fonts(self):
        """Sets up application fonts."""
        app_font_family = "sans-serif"
        try:
            available_fonts = ctk.utility.font.families()
            if "Segoe UI" in available_fonts: app_font_family = "Segoe UI"
            elif "Roboto" in available_fonts: app_font_family = "Roboto"
        except Exception as e: print(f"Error getting font families: {e}")
        print(f"Using font family: {app_font_family}")

        self.sidebar_header_font = ctk.CTkFont(family=app_font_family, size=16, weight="bold")
        self.sidebar_button_font = ctk.CTkFont(family=app_font_family, size=14)
        self.main_title_font = ctk.CTkFont(family=app_font_family, size=24, weight="bold")
        self.subtitle_font = ctk.CTkFont(family=app_font_family, size=13)
        self.scan_button_font = ctk.CTkFont(family=app_font_family, size=14, weight="bold")
        self.tree_heading_font = ctk.CTkFont(family=app_font_family, size=13, weight="bold")
        self.tree_body_font = ctk.CTkFont(family=app_font_family, size=12)
        self.switch_font = ctk.CTkFont(family=app_font_family, size=12)
        self.folder_list_font = ctk.CTkFont(family=app_font_family, size=11)

    def _load_icon(self, icon_path="add_folder_icon.png", size=(20,20)):
        """Loads icon safely."""
        if os.path.exists(icon_path):
            try:
                pil_image = Image.open(icon_path)
                return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            except Exception as e: print(f"Error loading icon '{icon_path}': {e}")
        else: print(f"Icon file not found: {icon_path}")
        return None

    def _setup_ui(self):
        """Creates and places all GUI widgets."""
        self.root.grid_columnconfigure(0, weight=0, minsize=250)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        sidebar_frame = ctk.CTkFrame(master=self.root, corner_radius=0)
        sidebar_frame.grid(row=0, column=0, sticky="nsew")
        sidebar_frame.grid_columnconfigure(0, weight=1)
        sidebar_frame.grid_rowconfigure(3, weight=1)

        folders_label = ctk.CTkLabel(master=sidebar_frame, text="Selected Folder", font=self.sidebar_header_font, anchor="w")
        folders_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="new")
        icon_image = self._load_icon()
        add_folder_btn = ctk.CTkButton(master=sidebar_frame, text="Select Folder", image=icon_image, compound="left", command=self.add_folder_clicked, font=self.sidebar_button_font, corner_radius=6, anchor="w", border_spacing=10)
        add_folder_btn.grid(row=1, column=0, padx=15, pady=(5,10), sticky="new")
        folder_list_frame = ctk.CTkFrame(master=sidebar_frame, corner_radius=4)
        folder_list_frame.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.folder_list_textbox = ctk.CTkTextbox(master=folder_list_frame, font=self.folder_list_font, wrap="none", activate_scrollbars=True, border_width=0, fg_color="transparent")
        self.folder_list_textbox.pack(expand=True, fill="both", padx=5, pady=5)
        self.folder_list_textbox.insert("0.0", "No folder selected...")
        self.folder_list_textbox.configure(state="disabled")
        self.theme_switch = ctk.CTkSwitch(master=sidebar_frame, text="Dark Mode", command=self.toggle_theme, font=self.switch_font)
        self.theme_switch.grid(row=4, column=0, padx=20, pady=20, sticky="sw")

        main_frame = ctk.CTkFrame(master=self.root, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, padx=25, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

        top_main_frame = ctk.CTkFrame(master=main_frame, fg_color="transparent")
        top_main_frame.grid(row=0, column=0, sticky="nsew")
        top_main_frame.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(master=top_main_frame, text="Duplicate Detective", font=self.main_title_font, anchor="w")
        title_label.grid(row=0, column=0, sticky="nw")
        subtitle_label = ctk.CTkLabel(master=top_main_frame, text="Scan the selected folder for duplicate files and delete them.", font=self.subtitle_font, text_color="gray50", anchor="w")
        subtitle_label.grid(row=1, column=0, pady=(2, 15), sticky="nw")
        self.scan_btn = ctk.CTkButton(master=top_main_frame, text="Scan Selected Folder", command=self.scan_folders_clicked, font=self.scan_button_font, corner_radius=8)
        self.scan_btn.grid(row=2, column=0, pady=10, sticky="nw")
        self.progress_bar = ctk.CTkProgressBar(master=top_main_frame, orientation="horizontal", mode="indeterminate", height=8, corner_radius=4)

        tree_frame = ctk.CTkFrame(master=main_frame, fg_color="transparent")
        tree_frame.grid(row=2, column=0, pady=(15, 10), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        columns = ('folder_path', 'size', 'full_path')
        self.results_tree = ttk.Treeview(master=tree_frame, columns=columns, displaycolumns=('folder_path', 'size'), show='tree headings', style="Treeview")
        self.results_tree.heading('#0', text='📄 File Name', anchor='w'); self.results_tree.heading('folder_path', text='📁 Folder Path', anchor='w'); self.results_tree.heading('size', text='⚖️ Size', anchor='e')
        self.results_tree.column('#0', stretch=tk.YES, minwidth=200, width=250, anchor='w'); self.results_tree.column('folder_path', stretch=tk.YES, minwidth=300, width=400, anchor='w'); self.results_tree.column('size', stretch=tk.NO, minwidth=80, width=100, anchor='e')
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar = ctk.CTkScrollbar(master=tree_frame, command=self.results_tree.yview, corner_radius=6); tree_scrollbar.grid(row=0, column=1, sticky='ns'); self.results_tree.configure(yscrollcommand=tree_scrollbar.set)

        bottom_frame = ctk.CTkFrame(master=main_frame, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        select_dupes_btn = ctk.CTkButton(master=bottom_frame, text="Select Dupes (Keep First)", command=self.select_all_but_first, font=self.sidebar_button_font, corner_radius=6); select_dupes_btn.grid(row=0, column=0, padx=(0,10), pady=10, sticky="se")
        delete_btn = ctk.CTkButton(master=bottom_frame, text="Delete Selected", command=self.delete_selected_clicked, font=self.sidebar_button_font, corner_radius=6, fg_color="#D32F2F", hover_color="#B71C1C"); delete_btn.grid(row=0, column=1, padx=0, pady=10, sticky="se")

    # --- Theme and Style Methods ---
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "dark" if current_mode == "Light" else "light"
        ctk.set_appearance_mode(new_mode)
        print(f"Switched theme to: {new_mode}")
        self._apply_ttk_style(new_mode)

    def _apply_ttk_style(self, mode):
        if mode.lower()=="light": tree_bg,tree_fg,heading_bg,heading_fg,selected_bg=("#FFFFFF","#101010","#F1F3F5","#404040","#0078D7")
        else: tree_bg,tree_fg,heading_bg,heading_fg,selected_bg=("#2B2B2B","#DCE4EE","#303030","#DCE4EE","#005A9E")
        self.style.configure("Treeview", background=tree_bg, foreground=tree_fg, fieldbackground=tree_bg, font=self.tree_body_font, rowheight=25, borderwidth=0); self.style.map('Treeview', background=[('selected', selected_bg)])
        self.style.configure("Treeview.Heading", background=heading_bg, foreground=heading_fg, font=self.tree_heading_font, padding=(8, 5), relief="flat", borderwidth=0); self.style.map("Treeview.Heading", background=[('active', heading_bg)], relief=[('active','flat'),('!active','flat')])
        print(f"Applied ttk Treeview style for {mode} theme.")

    def _apply_initial_theme(self):
        initial_mode = ctk.get_appearance_mode()
        print(f"Initial appearance mode: {initial_mode}")
        if initial_mode == "Dark": self.theme_switch.select()
        else: self.theme_switch.deselect()
        self._apply_ttk_style(initial_mode)

    # --- Backend Logic Methods ---
    def get_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error hashing {file_path}: {e}")
            return None

    def get_file_size(self, file_path):
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024: return f"{size_bytes} B"
            elif size_bytes < 1024**2: return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3: return f"{size_bytes/1024**2:.1f} MB"
            else: return f"{size_bytes/1024**3:.1f} GB"
        except Exception as e:
            print(f"Error getting size for {file_path}: {e}")
            return "N/A"

    def _run_scan_logic(self):
        print("Scan thread started...")
        if not self.folders_to_scan: print("No folder selected..."); self.root.after(0, lambda: messagebox.showerror("Error", "No folder selected...")); self.root.after(0, self.progress_bar.stop); self.root.after(0, lambda: self.progress_bar.grid_forget()); self.root.after(0, lambda: self.scan_btn.configure(state="normal")); return

        first_path_map = {}; duplicates_found = {}; total_files_scanned = 0
        try:
            print(f"Scanning folder: {self.folders_to_scan[0]}")
            folder = self.folders_to_scan[0]
            if not os.path.isdir(folder): print(f"Invalid folder selected: {folder}"); raise ValueError("Invalid folder selected")
            normalized_folder = os.path.realpath(os.path.normpath(folder)); print(f"Processing: {normalized_folder}")
            for dirpath, _, filenames in os.walk(normalized_folder):
                for fname in filenames:
                    fpath = os.path.join(dirpath, fname); normalized_fpath = os.path.normpath(fpath)
                    if not os.path.isfile(normalized_fpath) or os.path.islink(normalized_fpath): continue
                    file_hash = self.get_file_hash(normalized_fpath); total_files_scanned += 1
                    if not file_hash: print(f"Skip hash error: {normalized_fpath}"); continue
                    if file_hash in first_path_map:
                        original_path = first_path_map[file_hash]
                        if normalized_fpath == os.path.normpath(original_path): continue
                        if file_hash not in duplicates_found:
                            duplicates_found[file_hash] = [original_path]; # print(f" New set: {os.path.basename(original_path)}")
                        if normalized_fpath not in duplicates_found[file_hash]:
                            duplicates_found[file_hash].append(normalized_fpath); # print(f"  +Dupe: {os.path.basename(normalized_fpath)}")
                    else: first_path_map[file_hash] = normalized_fpath
            self.duplicates_data = duplicates_found
            num_duplicate_files = sum(len(paths) - 1 for paths in self.duplicates_data.values()); num_sets = len(self.duplicates_data)
            print(f"Scan complete. Found {num_sets} sets ({num_duplicate_files} extra files). Scanned: {total_files_scanned}")
            self.root.after(0, self._update_treeview)
            if num_sets > 0: self.root.after(100, lambda: messagebox.showinfo("Scan Complete", f"Found {num_sets} sets ({num_duplicate_files} duplicate files)."))
            else: self.root.after(100, lambda: messagebox.showinfo("Scan Complete", "No duplicate files found."))
        except Exception as e: print(f"Error during scan: {e}"); self.root.after(0, lambda: messagebox.showerror("Scan Error", f"Error during scan:\n{e}"))
        finally:
            if self.root: self.root.after(0, self.progress_bar.stop); self.root.after(0, lambda: self.progress_bar.grid_forget()); self.root.after(0, lambda: self.scan_btn.configure(state="normal"))
            print("Scan thread finished.")

    def _update_treeview(self):
        for item in self.results_tree.get_children(): self.results_tree.delete(item)
        if not self.duplicates_data: print("No duplicates to display."); return
        for file_hash, paths in self.duplicates_data.items():
            if paths and len(paths) > 1:
                first_path = paths[0]; filename = os.path.basename(first_path); folder = os.path.dirname(first_path); size = self.get_file_size(first_path)
                parent_id = self.results_tree.insert("", tk.END, text=f" {filename}", values=(folder, size, first_path), open=True)
                for duplicate_path in paths[1:]:
                    filename = os.path.basename(duplicate_path); folder = os.path.dirname(duplicate_path); size = self.get_file_size(duplicate_path)
                    self.results_tree.insert(parent_id, tk.END, text=f" {filename}", values=(folder, size, duplicate_path))
        print("Treeview updated with scan results.")

    # --- Button Action Methods ---
    def add_folder_clicked(self):
        folder = filedialog.askdirectory();
        if folder:
            self.folders_to_scan = [folder] # Replace list
            print(f"Selected folder: {folder}")
            self.folder_list_textbox.configure(state="normal"); self.folder_list_textbox.delete("1.0", tk.END)
            self.folder_list_textbox.insert("1.0", folder); self.folder_list_textbox.configure(state="disabled")
            print("Clearing previous results...")
            for item in self.results_tree.get_children(): self.results_tree.delete(item) # Clear results
            self.duplicates_data.clear()

    def scan_folders_clicked(self):
        print("Scan Folders button clicked"); self.scan_btn.configure(state="disabled")
        self.progress_bar.grid(row=3, column=0, padx=0, pady=(10, 0), sticky="ew"); self.progress_bar.start()
        print("Progress bar started."); scan_thread=threading.Thread(target=self._run_scan_logic,daemon=True); scan_thread.start()

    # --- CORRECTED delete_selected_clicked ---
    def delete_selected_clicked(self):
        """Deletes files selected in the Treeview."""
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select files to delete from the list.")
            return

        paths_to_delete = []
        print(f"Attempting to get paths for {len(selected_items)} selected items...")
        for item_id in selected_items:
            # CORRECTED try...except block for getting item data
            try:  # <--- Start try for this item_id
                item_data = self.results_tree.item(item_id)
                print(f"Processing item {item_id}: Data = {item_data}") # Debugging print

                if item_data and 'values' in item_data and isinstance(item_data['values'], (list, tuple)):
                    if len(item_data['values']) > 2:
                        full_path = item_data['values'][2] # Index 2 holds the full path
                        print(f"  Extracted full_path: {full_path}") # Debugging print

                        if isinstance(full_path, str) and full_path and os.path.exists(full_path):
                            paths_to_delete.append((item_id, full_path))
                            print(f"  Added valid path to delete list: {full_path}") # Debugging print
                        else:
                            print(f"  Warning: Invalid or non-existent path for item {item_id}. Path: '{full_path}'")
                    else:
                        print(f"  Warning: 'values' tuple too short for item {item_id}. Values: {item_data['values']}")
                else:
                    print(f"  Warning: Invalid or missing 'values' for item {item_id}. Item data: {item_data}")

            except Exception as e: # <--- CORRECTLY INDENTED except block for getting item data
                print(f"  Error processing item {item_id}: {e}")
        # End of loop for getting paths

        if not paths_to_delete:
             messagebox.showwarning("No Valid Paths", "Could not retrieve valid file paths for any selected items. Nothing will be deleted.")
             return

        print(f"Collected {len(paths_to_delete)} valid paths to potentially delete.")
        confirm_msg = f"Are you sure you want to permanently delete {len(paths_to_delete)} selected file(s)?"
        confirm = messagebox.askyesno("Confirm Delete", confirm_msg)
        if not confirm:
            print("Deletion cancelled by user.")
            return

        deleted_count = 0
        errors = []
        for item_id, path in paths_to_delete:
            try: # Separate try block for the actual deletion
                os.remove(path)
                print(f"Deleted: {path}")
                # Safely delete from Treeview only if os.remove succeeded
                if self.results_tree.exists(item_id): # Check if item still exists before deleting
                     self.results_tree.delete(item_id)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {path}: {e}")
                errors.append(f"{os.path.basename(path)}: {e}")

        result_message = f"{deleted_count} file(s) deleted."
        if errors:
            result_message += f"\n\nErrors occurred for:\n" + "\n".join(errors)
            messagebox.showerror("Deletion Errors", result_message)
        else:
            messagebox.showinfo("Deleted", result_message)
        print("Deletion process finished.")


    def select_all_but_first(self):
        """Selects all child items (duplicates) in the Treeview."""
        print("Selecting duplicates (keeping first in each group)..."); self.results_tree.selection_set();
        top_level_items=self.results_tree.get_children(""); items_to_select=[];
        for parent_id in top_level_items:
            child_items=self.results_tree.get_children(parent_id);
            if child_items: items_to_select.extend(child_items)
        if items_to_select: self.results_tree.selection_add(items_to_select); print(f"Selected {len(items_to_select)} duplicate items.")
        else: print("No duplicate items found to select.")

    def run(self):
         """Apply initial theme and start the main loop."""
         self._apply_initial_theme()
         self.root.mainloop()


# --- Main Execution Block ---
if __name__ == "__main__":
    # Ensure PIL is installed: pip install Pillow
    # Ensure you have an icon file named "add_folder_icon.png" or change path
    root = ctk.CTk()
    app = DuplicateDetectorApp(root)
    app.run()