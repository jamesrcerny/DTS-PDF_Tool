"""Data layer for DTS authorization folders: creation, expenses, totals, receipts."""
import json
import os
import re

BASE_DIR = r"C:\Users\Bob\OneDrive\Documents\Marines\DTSApplication"

GTCC = "GTCC"
PERSONAL = "Personal"

_ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_name(text):
    cleaned = _ILLEGAL_CHARS.sub("_", text).strip().strip(".")
    return cleaned or "Untitled"


def authorization_folder_path(training, date):
    folder_name = f"{sanitize_name(training)}_{sanitize_name(date)}"
    return os.path.join(BASE_DIR, folder_name)


def create_authorization(training, date):
    """Creates the authorization folder, gtcc/personal subfolders, and expenses.json.
    Raises FileExistsError if an authorization with this training+date already exists."""
    folder_path = authorization_folder_path(training, date)
    if os.path.exists(folder_path):
        raise FileExistsError(f"An authorization already exists at {folder_path}")

    os.makedirs(folder_path)
    os.makedirs(os.path.join(folder_path, "gtcc"))
    os.makedirs(os.path.join(folder_path, "personal"))

    data = {"training": training, "date": date, "expenses": []}
    save_authorization(folder_path, data)
    return folder_path


def list_authorizations():
    """Returns a list of {training, date, folder_path, gtcc_total, personal_total, grand_total}."""
    results = []
    if not os.path.isdir(BASE_DIR):
        return results
    for name in sorted(os.listdir(BASE_DIR)):
        folder_path = os.path.join(BASE_DIR, name)
        if os.path.isfile(os.path.join(folder_path, "expenses.json")):
            data = load_authorization(folder_path)
            gtcc_total, personal_total, grand_total = compute_totals(data)
            results.append({
                "training": data["training"],
                "date": data["date"],
                "folder_path": folder_path,
                "gtcc_total": gtcc_total,
                "personal_total": personal_total,
                "grand_total": grand_total,
            })
    return results


def load_authorization(folder_path):
    with open(os.path.join(folder_path, "expenses.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def save_authorization(folder_path, data):
    with open(os.path.join(folder_path, "expenses.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_expense(folder_path, description, amount, date, expense_type):
    data = load_authorization(folder_path)
    data["expenses"].append({
        "description": description,
        "amount": amount,
        "date": date,
        "type": expense_type,
    })
    save_authorization(folder_path, data)
    return data


def compute_totals(data):
    gtcc_total = sum(e["amount"] for e in data["expenses"] if e["type"] == GTCC)
    personal_total = sum(e["amount"] for e in data["expenses"] if e["type"] == PERSONAL)
    return gtcc_total, personal_total, gtcc_total + personal_total


def receipt_folder(folder_path, expense_type):
    subfolder = "gtcc" if expense_type == GTCC else "personal"
    return os.path.join(folder_path, subfolder)
