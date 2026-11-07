"""DTS Tool App: track expenses per DTS authorization, plus an embedded PDF Tool."""
import threading
from datetime import date

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

import dts_storage
import email_import
import pdf_actions
from gui_helpers import (
    BUTTON_FONT, LABEL_FONT, TITLE_FONT, SUBTITLE_FONT,
    make_drop_list, make_receipt_drop_zone, make_sidebar_button, show_status,
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

PDF_SECTIONS = ["Merge PDFs", "Images to PDF", "PDF to JPG", "Compress PDF"]


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application window with drag-and-drop support."""

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("DTS Tool")
        self.geometry("820x620")

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.sidebar, text="DTS Tool", font=TITLE_FONT).pack(pady=(20, 30))

        tabs = [
            ("Home", self.show_home),
            ("New Authorization", self.show_new_authorization),
            ("My Authorizations", self.show_my_authorizations),
            ("PDF Tool", lambda: self.show_pdf_tool()),
        ]
        for name, command in tabs:
            btn = make_sidebar_button(self.sidebar, name, command)
            btn.pack(fill="x", padx=15, pady=6)

        self.show_home()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- Home ----------
    def show_home(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Welcome to DTS Tool", font=TITLE_FONT).pack(
            pady=(20, 10))
        ctk.CTkLabel(
            self.main_frame,
            text="Choose an option from the menu on the left to get started.",
            font=SUBTITLE_FONT,
        ).pack(pady=(0, 20))
        ctk.CTkLabel(
            self.main_frame,
            text="• New Authorization — start tracking expenses for a training\n"
                 "• My Authorizations — open an authorization you've already started\n"
                 "• PDF Tool — merge, convert, and compress PDFs",
            font=LABEL_FONT, justify="left",
        ).pack(pady=10, padx=20, anchor="w")

    # ---------- New Authorization ----------
    def show_new_authorization(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="New Authorization", font=TITLE_FONT).pack(
            pady=(10, 15))

        ctk.CTkLabel(self.main_frame, text="Training Name", font=LABEL_FONT).pack(anchor="w")
        training_entry = ctk.CTkEntry(self.main_frame, font=LABEL_FONT, width=300)
        training_entry.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(self.main_frame, text="Training Date (YYYY-MM-DD)", font=LABEL_FONT).pack(
            anchor="w")
        date_entry = ctk.CTkEntry(self.main_frame, font=LABEL_FONT, width=300)
        date_entry.insert(0, date.today().isoformat())
        date_entry.pack(anchor="w", pady=(0, 10))

        def create_action():
            training = training_entry.get().strip()
            training_date = date_entry.get().strip()
            if not training:
                show_status(self.main_frame, "Enter a training name.", is_error=True)
                return
            try:
                date.fromisoformat(training_date)
            except ValueError:
                show_status(self.main_frame, "Date must be in YYYY-MM-DD format.", is_error=True)
                return
            try:
                folder_path = dts_storage.create_authorization(training, training_date)
                self.show_authorization_detail(folder_path)
            except FileExistsError:
                show_status(
                    self.main_frame,
                    "An authorization with this name and date already exists.",
                    is_error=True,
                )

        ctk.CTkButton(self.main_frame, text="Create", font=BUTTON_FONT,
                      command=create_action).pack(pady=10)

    # ---------- My Authorizations ----------
    def show_my_authorizations(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="My Authorizations", font=TITLE_FONT).pack(
            pady=(10, 15))

        authorizations = dts_storage.list_authorizations()
        if not authorizations:
            ctk.CTkLabel(self.main_frame, text="No authorizations yet.", font=LABEL_FONT).pack(
                pady=10)
            return

        list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True)

        for auth in authorizations:
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", pady=4)
            label_text = f"{auth['training']} — {auth['date']} (Total: ${auth['grand_total']:.2f})"
            ctk.CTkLabel(row, text=label_text, font=LABEL_FONT).pack(
                side="left", padx=10, pady=8)
            ctk.CTkButton(
                row, text="Open", font=LABEL_FONT, width=80,
                command=lambda fp=auth["folder_path"]: self.show_authorization_detail(fp),
            ).pack(side="right", padx=10, pady=8)

    # ---------- Authorization Detail ----------
    def show_authorization_detail(self, folder_path):
        self.clear_main()
        data = dts_storage.load_authorization(folder_path)
        gtcc_total, personal_total, grand_total = dts_storage.compute_totals(data)

        ctk.CTkButton(self.main_frame, text="< Back to Authorizations", font=LABEL_FONT,
                      width=180, fg_color="#888888", hover_color="#666666",
                      command=self.show_my_authorizations).pack(anchor="w")

        ctk.CTkLabel(self.main_frame, text=f"{data['training']} — {data['date']}",
                     font=TITLE_FONT).pack(pady=(10, 5), anchor="w")

        ctk.CTkLabel(
            self.main_frame,
            text=f"GTCC: ${gtcc_total:.2f}    Personal: ${personal_total:.2f}    "
                 f"Grand Total: ${grand_total:.2f}",
            font=SUBTITLE_FONT,
        ).pack(pady=(0, 10), anchor="w")

        expenses_box = ctk.CTkTextbox(self.main_frame, font=LABEL_FONT, height=100)
        expenses_box.pack(fill="x", pady=(0, 10))
        for expense in data["expenses"]:
            expenses_box.insert(
                "end",
                f"[{expense['type']}] {expense['date']} — {expense['description']} — "
                f"${expense['amount']:.2f}\n",
            )
        expenses_box.configure(state="disabled")

        # ---- Add expense form ----
        form = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form, text="Description", font=LABEL_FONT).grid(row=0, column=0, padx=5)
        description_entry = ctk.CTkEntry(form, font=LABEL_FONT, width=180)
        description_entry.grid(row=1, column=0, padx=5)

        ctk.CTkLabel(form, text="Amount", font=LABEL_FONT).grid(row=0, column=1, padx=5)
        amount_entry = ctk.CTkEntry(form, font=LABEL_FONT, width=100)
        amount_entry.grid(row=1, column=1, padx=5)

        ctk.CTkLabel(form, text="Date", font=LABEL_FONT).grid(row=0, column=2, padx=5)
        expense_date_entry = ctk.CTkEntry(form, font=LABEL_FONT, width=120)
        expense_date_entry.insert(0, data["date"])
        expense_date_entry.grid(row=1, column=2, padx=5)

        ctk.CTkLabel(form, text="Type", font=LABEL_FONT).grid(row=0, column=3, padx=5)
        type_selector = ctk.CTkSegmentedButton(
            form, values=[dts_storage.GTCC, dts_storage.PERSONAL])
        type_selector.set(dts_storage.GTCC)
        type_selector.grid(row=1, column=3, padx=5)

        def add_expense_action():
            description = description_entry.get().strip()
            amount_text = amount_entry.get().strip()
            expense_date = expense_date_entry.get().strip()
            if not description:
                show_status(self.main_frame, "Enter a description.", is_error=True)
                return
            try:
                amount = float(amount_text)
            except ValueError:
                show_status(self.main_frame, "Amount must be a number.", is_error=True)
                return
            try:
                date.fromisoformat(expense_date)
            except ValueError:
                show_status(self.main_frame, "Date must be in YYYY-MM-DD format.", is_error=True)
                return
            dts_storage.add_expense(
                folder_path, description, amount, expense_date, type_selector.get())
            self.show_authorization_detail(folder_path)

        ctk.CTkButton(form, text="Add Expense", font=LABEL_FONT,
                      command=add_expense_action).grid(row=2, column=0, columnspan=4, pady=(10, 0))

        # ---- Receipt drop zones ----
        ctk.CTkLabel(self.main_frame, text="Receipts", font=SUBTITLE_FONT).pack(
            pady=(10, 5), anchor="w")

        zones_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        zones_frame.pack(fill="both", expand=True)

        gtcc_folder = dts_storage.receipt_folder(folder_path, dts_storage.GTCC)
        personal_folder = dts_storage.receipt_folder(folder_path, dts_storage.PERSONAL)
        refresh_gtcc_zone = make_receipt_drop_zone(
            self, zones_frame, "Drag & drop GTCC receipts here", gtcc_folder)
        make_receipt_drop_zone(
            self, zones_frame, "Drag & drop personal receipts here", personal_folder)

        def import_email_action():
            try:
                training_date_obj = date.fromisoformat(data["date"])
            except ValueError:
                show_status(self.main_frame, "Authorization date is invalid.", is_error=True)
                return
            show_status(self.main_frame, "Importing receipts...")
            self._run_email_import_async(training_date_obj, gtcc_folder, refresh_gtcc_zone)

        ctk.CTkButton(self.main_frame, text="Import GTCC Receipts from Email", font=LABEL_FONT,
                      command=import_email_action).pack(pady=(10, 0))

    def _run_email_import_async(self, training_date_obj, gtcc_folder, refresh_gtcc_zone):
        device_code_dialog = {"dialog": None}

        def on_device_code(user_code, verification_uri):
            self.after(0, lambda: self._show_device_code_dialog(
                user_code, verification_uri, device_code_dialog))

        def worker():
            try:
                saved = email_import.fetch_gtcc_receipts(
                    training_date_obj, gtcc_folder, on_device_code=on_device_code)
                self.after(0, lambda: self._finish_email_import(
                    device_code_dialog, refresh_gtcc_zone, saved=saved))
            except Exception as exc:
                self.after(0, lambda: self._finish_email_import(
                    device_code_dialog, refresh_gtcc_zone, error=exc))

        threading.Thread(target=worker, daemon=True).start()

    def _show_device_code_dialog(self, user_code, verification_uri, holder):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sign in to Outlook")
        dialog.geometry("380x220")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Go to:\n{verification_uri}", font=LABEL_FONT,
                     justify="center").pack(pady=(15, 5))
        ctk.CTkLabel(dialog, text=f"Enter code: {user_code}", font=BUTTON_FONT).pack(
            pady=(0, 10))
        ctk.CTkButton(
            dialog, text="Copy Code", font=LABEL_FONT,
            command=lambda: (dialog.clipboard_clear(), dialog.clipboard_append(user_code)),
        ).pack(pady=(0, 10))
        ctk.CTkLabel(dialog, text="Waiting for sign-in...", font=LABEL_FONT,
                     text_color="#555555").pack()

        holder["dialog"] = dialog

    def _finish_email_import(self, device_code_dialog, refresh_gtcc_zone, saved=None, error=None):
        if device_code_dialog["dialog"] is not None:
            device_code_dialog["dialog"].destroy()
        if error is not None:
            show_status(self.main_frame, f"Error: {error}", is_error=True)
        else:
            refresh_gtcc_zone()
            show_status(self.main_frame, f"Imported {len(saved)} receipt(s).")

    # ---------- PDF Tool ----------
    def show_pdf_tool(self, section=PDF_SECTIONS[0]):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="PDF Tool", font=TITLE_FONT).pack(pady=(10, 5))

        nav = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        nav.pack(pady=(0, 10))
        for name in PDF_SECTIONS:
            ctk.CTkButton(
                nav, text=name, font=LABEL_FONT, width=140,
                fg_color="#1f6aa5" if name == section else "#888888",
                hover_color="#144870",
                command=lambda n=name: self.show_pdf_tool(n),
            ).pack(side="left", padx=5)

        section_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        section_frame.pack(fill="both", expand=True)

        if section == "Merge PDFs":
            self._build_pdf_section(
                section_frame, "PDF", (".pdf",), "Merge",
                pdf_actions.merge_pdfs,
                min_files=2, success_message=None)
        elif section == "Images to PDF":
            self._build_pdf_section(
                section_frame, "image", (".png", ".jpg", ".jpeg", ".bmp", ".gif"), "Convert",
                pdf_actions.images_to_pdf,
                min_files=1, success_message=None)
        elif section == "PDF to JPG":
            self._build_pdf_section(
                section_frame, "PDF", (".pdf",), "Convert",
                pdf_actions.pdf_to_jpg,
                min_files=1, success_message="Conversion complete.")
        elif section == "Compress PDF":
            self._build_pdf_section(
                section_frame, "PDF", (".pdf",), "Compress",
                pdf_actions.compress_pdf,
                min_files=1, success_message="Compression complete.")

    def _build_pdf_section(self, parent, filetypes_label, accept_exts, button_text,
                            action, min_files, success_message):
        file_list = make_drop_list(self, parent, filetypes_label, accept_exts)

        def run_action():
            if len(file_list) < min_files:
                noun = "file" if min_files == 1 else "files"
                show_status(parent, f"Add at least {min_files} {filetypes_label} {noun}.",
                            is_error=True)
                return
            try:
                result = action(file_list)
                message = success_message or f"Saved to {result}"
                show_status(parent, message)
            except FileNotFoundError:
                show_status(
                    parent,
                    "Ghostscript (gswin64c) not found. Please install Ghostscript.",
                    is_error=True,
                )
            except Exception as exc:
                show_status(parent, f"Error: {exc}", is_error=True)

        ctk.CTkButton(parent, text=button_text, font=BUTTON_FONT,
                      command=run_action).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
