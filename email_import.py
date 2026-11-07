"""Fetches GTCC receipt PDFs from Outlook via Microsoft Graph (OAuth device code flow)."""
import base64
import os
from datetime import timedelta

import msal
import requests
import win32crypt

# Paste the Application (client) ID from your Azure app registration here.
# See the plan / setup notes for the one-time registration steps.
CLIENT_ID = "ac376a1b-b2ed-4f06-a337-71cef38d1aae"

AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = ["Mail.Read"]
GRAPH_ROOT = "https://graph.microsoft.com/v1.0"

TOKEN_CACHE_PATH = os.path.join(os.environ["LOCALAPPDATA"], "DTSTool", "token_cache.bin")
DEFAULT_SENDER = "Invoices@citravel.com"
WINDOW_DAYS = 15


def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_PATH):
        with open(TOKEN_CACHE_PATH, "rb") as f:
            encrypted = f.read()
        decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1]
        cache.deserialize(decrypted.decode("utf-8"))
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        os.makedirs(os.path.dirname(TOKEN_CACHE_PATH), exist_ok=True)
        encrypted = win32crypt.CryptProtectData(
            cache.serialize().encode("utf-8"), "DTS Tool token cache", None, None, None, 0)
        with open(TOKEN_CACHE_PATH, "wb") as f:
            f.write(encrypted)


def get_access_token(on_device_code=None):
    """Returns a valid access token, signing in via device code flow if needed.
    on_device_code(user_code, verification_uri), if given, is called before the
    blocking wait for the user to complete sign-in in a browser."""
    if CLIENT_ID == "PASTE-YOUR-AZURE-APP-CLIENT-ID-HERE":
        raise RuntimeError(
            "Email import isn't configured yet. Paste your Azure app's Client ID "
            "into CLIENT_ID at the top of email_import.py.")

    cache = _load_cache()
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(flow.get("error_description", "Failed to start sign-in."))
        if on_device_code:
            on_device_code(flow["user_code"], flow["verification_uri"])
        result = app.acquire_token_by_device_flow(flow)

    _save_cache(cache)

    if "access_token" not in result:
        raise RuntimeError(result.get("error_description", "Sign-in failed."))
    return result["access_token"]


def _unique_dest_path(dest_folder, filename):
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_folder, filename)
    n = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base} ({n}){ext}")
        n += 1
    return candidate


def fetch_gtcc_receipts(training_date, dest_folder, sender=DEFAULT_SENDER, on_device_code=None):
    """Downloads every PDF attachment from `sender`, received within WINDOW_DAYS of
    training_date, into dest_folder. Returns the list of filenames saved."""
    token = get_access_token(on_device_code)
    headers = {"Authorization": f"Bearer {token}"}

    since = (training_date - timedelta(days=WINDOW_DAYS)).isoformat() + "T00:00:00Z"
    until = (training_date + timedelta(days=WINDOW_DAYS)).isoformat() + "T23:59:59Z"
    filter_str = (
        f"from/emailAddress/address eq '{sender}' "
        f"and receivedDateTime ge {since} and receivedDateTime le {until}"
    )

    os.makedirs(dest_folder, exist_ok=True)
    saved = []

    url = f"{GRAPH_ROOT}/me/messages"
    params = {"$filter": filter_str, "$select": "id,hasAttachments"}
    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise RuntimeError(f"Email search failed: {response.text}")
        data = response.json()
        params = None  # only needed on the first request; nextLink carries its own params

        for message in data.get("value", []):
            if not message.get("hasAttachments"):
                continue
            attachments_resp = requests.get(
                f"{GRAPH_ROOT}/me/messages/{message['id']}/attachments", headers=headers)
            if attachments_resp.status_code != 200:
                continue
            for attachment in attachments_resp.json().get("value", []):
                name = attachment.get("name", "")
                content_type = attachment.get("contentType", "")
                if content_type != "application/pdf" and not name.lower().endswith(".pdf"):
                    continue
                content_bytes = attachment.get("contentBytes")
                if not content_bytes:
                    continue
                dest_path = _unique_dest_path(dest_folder, name)
                with open(dest_path, "wb") as f:
                    f.write(base64.b64decode(content_bytes))
                saved.append(os.path.basename(dest_path))

        url = data.get("@odata.nextLink")

    return saved
