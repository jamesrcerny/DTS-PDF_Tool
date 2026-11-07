"""PDF Tool App: merge PDFs, convert images to PDF, and convert PDF pages to JPG."""
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

import pdf_actions
from gui_helpers import (
    BUTTON_FONT, LABEL_FONT, TITLE_FONT, SUBTITLE_FONT,
    make_drop_list, make_sidebar_button, show_status,
)

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application window with drag-and-drop support."""

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("PDF Tool")
        self.geometry("720x540")

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.sidebar, text="PDF Tool", font=TITLE_FONT).pack(pady=(20, 30))

        self.tab_buttons = {}
        tabs = [
            ("Home", self.show_home),
            ("Merge PDFs", self.show_merge),
            ("Images to PDF", self.show_images_to_pdf),
            ("PDF to JPG", self.show_pdf_to_jpg),
            ("Compress PDF", self.show_compress),
        ]
        for name, command in tabs:
            btn = make_sidebar_button(self.sidebar, name, command)
            btn.pack(fill="x", padx=15, pady=6)
            self.tab_buttons[name] = btn

        self.show_home()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- Home ----------
    def show_home(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Welcome to PDF Tool", font=TITLE_FONT).pack(
            pady=(20, 10))
        ctk.CTkLabel(
            self.main_frame,
            text="Choose an option from the menu on the left to get started.",
            font=SUBTITLE_FONT,
        ).pack(pady=(0, 20))
        ctk.CTkLabel(
            self.main_frame,
            text="• Merge PDFs — combine multiple PDF files into one\n"
                 "• Images to PDF — convert pictures into a single PDF\n"
                 "• PDF to JPG — export each page of a PDF as a JPG\n"
                 "• Compress PDF — reduce the file size of a PDF",
            font=LABEL_FONT, justify="left",
        ).pack(pady=10, padx=20, anchor="w")

    # ---------- Merge PDFs ----------
    def show_merge(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Merge PDFs", font=TITLE_FONT).pack(pady=(10, 5))

        file_list = make_drop_list(self, self.main_frame, "PDF", (".pdf",))

        def merge_action():
            if len(file_list) < 2:
                show_status(self.main_frame, "Add at least two PDF files.", is_error=True)
                return
            try:
                output_path = pdf_actions.merge_pdfs(file_list)
                show_status(self.main_frame, f"Saved to {output_path}")
            except Exception as exc:
                show_status(self.main_frame, f"Error: {exc}", is_error=True)

        ctk.CTkButton(self.main_frame, text="Merge", font=BUTTON_FONT,
                      command=merge_action).pack(pady=10)

    # ---------- Images to PDF ----------
    def show_images_to_pdf(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Images to PDF", font=TITLE_FONT).pack(pady=(10, 5))

        file_list = make_drop_list(
            self, self.main_frame, "image", (".png", ".jpg", ".jpeg", ".bmp", ".gif"))

        def convert_action():
            if not file_list:
                show_status(self.main_frame, "Add at least one image file.", is_error=True)
                return
            try:
                output_path = pdf_actions.images_to_pdf(file_list)
                show_status(self.main_frame, f"Saved to {output_path}")
            except Exception as exc:
                show_status(self.main_frame, f"Error: {exc}", is_error=True)

        ctk.CTkButton(self.main_frame, text="Convert", font=BUTTON_FONT,
                      command=convert_action).pack(pady=10)

    # ---------- PDF to JPG ----------
    def show_pdf_to_jpg(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="PDF to JPG", font=TITLE_FONT).pack(pady=(10, 5))

        file_list = make_drop_list(self, self.main_frame, "PDF", (".pdf",))

        def convert_action():
            if not file_list:
                show_status(self.main_frame, "Add at least one PDF file.", is_error=True)
                return
            try:
                pdf_actions.pdf_to_jpg(file_list)
                show_status(self.main_frame, "Conversion complete.")
            except Exception as exc:
                show_status(self.main_frame, f"Error: {exc}", is_error=True)

        ctk.CTkButton(self.main_frame, text="Convert", font=BUTTON_FONT,
                      command=convert_action).pack(pady=10)

    # ---------- Compress PDF ----------
    def show_compress(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Compress PDF", font=TITLE_FONT).pack(pady=(10, 5))

        file_list = make_drop_list(self, self.main_frame, "PDF", (".pdf",))

        def compress_action():
            if not file_list:
                show_status(self.main_frame, "Add at least one PDF file.", is_error=True)
                return
            try:
                pdf_actions.compress_pdf(file_list)
                show_status(self.main_frame, "Compression complete.")
            except FileNotFoundError:
                show_status(
                    self.main_frame,
                    "Ghostscript (gswin64c) not found. Please install Ghostscript.",
                    is_error=True,
                )
            except Exception as exc:
                show_status(self.main_frame, f"Error: {exc}", is_error=True)

        ctk.CTkButton(self.main_frame, text="Compress", font=BUTTON_FONT,
                      command=compress_action).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
