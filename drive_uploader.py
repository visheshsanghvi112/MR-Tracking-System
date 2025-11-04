"""
Google Drive uploader

Two modes:
1) Service Account (default) - raw HTTP multipart upload
2) OAuth user (if DRIVE_OAUTH_ENABLED=true) - uses google-api-python-client with token.json
"""
import json
import os
from typing import Tuple

import requests
from google.oauth2.service_account import Credentials as SACredentials
from google.auth.transport.requests import Request

from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io


def _get_access_token(creds_path: str) -> str:
    scopes = [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
    ]
    credentials = SACredentials.from_service_account_file(creds_path, scopes=scopes)
    request = Request()
    credentials.refresh(request)
    return credentials.token


def upload_bytes_to_drive(
    data: bytes,
    filename: str,
    folder_id: str,
    creds_path: str = "pharmagiftapp-60fb5a6a3ca9.json",
    make_public: bool = True,
) -> Tuple[str, str]:
    """Upload bytes to Drive folder and optionally make it link-readable.

    Returns: (file_id, web_view_url)
    """
    # OAuth user mode
    if os.getenv('DRIVE_OAUTH_ENABLED', 'false').lower() == 'true':
        token_file = os.getenv('DRIVE_OAUTH_TOKEN_FILE', 'token.json')
        scopes = ["https://www.googleapis.com/auth/drive.file"]
        creds = UserCredentials.from_authorized_user_file(token_file, scopes)
        drive = build('drive', 'v3', credentials=creds)
        media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream', resumable=False)
        created = drive.files().create(
            body={"name": filename, "parents": [folder_id]},
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        file_id = created.get('id')
        url = created.get('webViewLink')
        return file_id, url

    # Service account mode (raw HTTP)
    token = _get_access_token(creds_path)
    metadata = {"name": filename, "parents": [folder_id]}

    files = {
        "metadata": ("metadata", json.dumps(metadata), "application/json; charset=UTF-8"),
        "file": ("media", data, "application/octet-stream"),
    }

    resp = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        timeout=60,
    )
    resp.raise_for_status()
    file_id = resp.json().get("id")

    if make_public:
        perm_resp = requests.post(
            f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions?supportsAllDrives=true",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            data=json.dumps({"role": "reader", "type": "anyone"}),
            timeout=30,
        )
        if perm_resp.status_code not in (200, 204):
            pass

    web_view_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    return file_id, web_view_url


