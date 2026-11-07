# DTS Tool & PDF Tool

> A Windows desktop app for keeping Defense Travel System (DTS) expense receipts organized by trip, with built-in PDF tools for merging, converting, and compressing documents.

![screenshot](docs/screenshot.png)
<!-- Add a screenshot or GIF of the app running and save it as docs/screenshot.png. -->

---

## Overview

Travel vouchers mean tracking many small receipts across different payment types. This app keeps each trip's expenses, totals, and receipts together in one folder instead of scattered across downloads and email. It also includes a set of everyday PDF tools for preparing the paperwork.

## Features

- **Trip tracking:** create an authorization (training name and date). The app builds a folder with separate receipt subfolders for government travel card (GTCC) and personal expenses.
- **Expense log:** add expenses with a description, amount, date, and type, with running totals for each payment type and overall.
- **Drag-and-drop receipts:** drop files straight into the right folder and see what is saved.
- **Email import:** pull travel-card receipt PDFs from Outlook using Microsoft Graph, with a browser sign-in (device code flow). It downloads PDF attachments from the invoice sender received within 15 days of the training date.
- **PDF tools:** merge PDFs, combine images into one PDF, export PDF pages to JPG, and compress PDFs.

## Tech Stack

- **Language:** Python 3.12
- **Framework / UI:** customtkinter, tkinterdnd2 (drag and drop)
- **Key libraries:** pypdf, PyMuPDF, Pillow, msal and requests (Microsoft Graph), pywin32
- **Other tools:** Ghostscript (PDF compression), PyInstaller (Windows executable)
- **Platform:** Windows 10/11 desktop application

## Getting Started

### Option A — Run the app (for users)
1. Download the latest release from the [Releases](../../releases) page.
2. Requires Windows 10 or 11.
3. Run `DTSTool.exe`.
   *(Only run executables you trust.)*

### Option B — Build from source (for developers)
```bash
# clone the repo
git clone https://github.com/jamesrcerny/pdftool.git
cd pdftool

# install dependencies
pip install customtkinter tkinterdnd2 pypdf pymupdf pillow msal requests pywin32

# run the DTS Tool (includes the PDF tools)
python dts_tool_app.py

# or run the standalone PDF Tool
python pdf_tool_app.py
```

**Configuration before first run:**
- In `dts_storage.py`, set `BASE_DIR` to the folder where you want authorization folders stored.
- For email import, register an app in Azure (personal Microsoft accounts) and set `CLIENT_ID` in `email_import.py`. The `Mail.Read` permission is the only one requested.
- PDF compression requires [Ghostscript](https://www.ghostscript.com/) (`gswin64c`) on your PATH.

## Why I Built This

Keeping travel receipts straight across a card and personal spending is tedious and easy to get wrong. I built this to put each trip's receipts and totals in one place, and to turn the PDF steps I kept repeating into a few clicks.

## Roadmap / Known Limitations

- Windows only (uses pywin32 and Windows paths).
- Storage folder, email sender, and Azure client ID are set in code and should move to a settings file.
- No automated tests yet.

## License

[Choose a license, for example MIT. See the LICENSE file.]

---

*Built by James Cerny — [github.com/jamesrcerny](https://github.com/jamesrcerny)*
