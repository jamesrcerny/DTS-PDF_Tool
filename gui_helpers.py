"""Shared customtkinter styling and widgets used by pdf_tool_app.py and dts_tool_app.py."""
import os
import shutil

import customtkinter as ctk
from tkinterdnd2 import DND_FILES

LABEL_FONT = ("Arial", 14)
BUTTON_FONT = ("Arial", 16)
TITLE_FONT = ("Arial", 24, "bold")
SUBTITLE_FONT = ("Arial", 16)
TAB_FONT = ("Arial", 14, "bold")

SIDEBAR_FG = "#1f6aa5"
SIDEBAR_HOVER = "#144870"


def make_sidebar_button(parent, text, command):
    return ctk.CTkButton(parent, text=text, font=TAB_FONT, command=command,
                          fg_color=SIDEBAR_FG, hover_color=SIDEBAR_HOVER, anchor="w")


def show_status(parent, message, is_error=False):
    for widget in parent.winfo_children():
        if getattr(widget, "_is_status", False):
            widget.destroy()
    label = ctk.CTkLabel(parent, text=message, font=LABEL_FONT,
                          text_color="red" if is_error else "green")
    label._is_status = True
    label.pack(pady=10)


def make_drop_list(app, parent, filetypes_label, accept_exts):
    """Creates a drag-and-drop listbox-style frame and returns the tracked file list."""
    file_list = []

    drop_frame = ctk.CTkFrame(parent, height=180, fg_color="#e8e8e8",
                               border_width=2, border_color=SIDEBAR_FG)
    drop_frame.pack(fill="both", expand=True, padx=20, pady=10)
    drop_frame.pack_propagate(False)

    hint = ctk.CTkLabel(
        drop_frame,
        text=f"Drag and drop {filetypes_label} files here",
        font=LABEL_FONT, text_color="#555555",
    )
    hint.pack(pady=(15, 5))

    files_box = ctk.CTkTextbox(drop_frame, font=LABEL_FONT, height=120)
    files_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    files_box.configure(state="disabled")

    def refresh_box():
        files_box.configure(state="normal")
        files_box.delete("1.0", "end")
        for f in file_list:
            files_box.insert("end", os.path.basename(f) + "\n")
        files_box.configure(state="disabled")

    def on_drop(event):
        paths = app.tk.splitlist(event.data)
        for p in paths:
            if accept_exts is None or p.lower().endswith(accept_exts):
                if p not in file_list:
                    file_list.append(p)
        refresh_box()

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", on_drop)

    def clear_files():
        file_list.clear()
        refresh_box()

    clear_btn = ctk.CTkButton(parent, text="Clear Files", font=LABEL_FONT,
                               command=clear_files, fg_color="#888888",
                               hover_color="#666666", width=120)
    clear_btn.pack(pady=(0, 10))

    return file_list


def make_receipt_drop_zone(app, parent, label, dest_folder):
    """Creates a drag-and-drop frame that copies dropped files straight into dest_folder
    and lists the folder's current contents (reflects what's actually saved on disk)."""
    drop_frame = ctk.CTkFrame(parent, height=180, fg_color="#e8e8e8",
                               border_width=2, border_color=SIDEBAR_FG)
    drop_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    drop_frame.pack_propagate(False)

    ctk.CTkLabel(drop_frame, text=label, font=LABEL_FONT, text_color="#555555").pack(
        pady=(15, 5))

    files_box = ctk.CTkTextbox(drop_frame, font=LABEL_FONT, height=100)
    files_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    files_box.configure(state="disabled")

    def refresh_box():
        files_box.configure(state="normal")
        files_box.delete("1.0", "end")
        os.makedirs(dest_folder, exist_ok=True)
        for name in sorted(os.listdir(dest_folder)):
            files_box.insert("end", name + "\n")
        files_box.configure(state="disabled")

    def unique_dest_path(filename):
        base, ext = os.path.splitext(filename)
        candidate = os.path.join(dest_folder, filename)
        n = 1
        while os.path.exists(candidate):
            candidate = os.path.join(dest_folder, f"{base} ({n}){ext}")
            n += 1
        return candidate

    def on_drop(event):
        os.makedirs(dest_folder, exist_ok=True)
        paths = app.tk.splitlist(event.data)
        for p in paths:
            if os.path.isfile(p):
                shutil.copy2(p, unique_dest_path(os.path.basename(p)))
        refresh_box()

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", on_drop)

    refresh_box()
    return refresh_box
