#!/usr/bin/env python3
"""
Helper Google Sheets — lecture / écriture de cellules par clé de ligne.

Configuration via variables d'environnement (ou fichier .env) :
    GOOGLE_SHEET_ID   ID du spreadsheet (dans l'URL entre /d/ et /edit)
    SHEET_TAB         Nom de l'onglet (défaut : "Feuille 1")
    KEY_COLUMN        En-tête de la colonne clé unique (défaut : 1re colonne)

Exemples :
    python gsheet.py                       # affiche colonnes + nb de lignes
    python gsheet.py "@exemple_user" "Statut message" "Envoyé"   # met à jour une cellule
"""
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = os.path.dirname(os.path.abspath(__file__))
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
TAB = os.environ.get("SHEET_TAB", "Feuille 1")
KEY_COLUMN = os.environ.get("KEY_COLUMN", "")  # vide -> première colonne


def service():
    token = os.path.join(ROOT, "token.json")
    if not os.path.exists(token):
        raise SystemExit("token.json manquant — lance d'abord `python gsheet_auth.py`.")
    creds = Credentials.from_authorized_user_file(token, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        open(token, "w").write(creds.to_json())
    return build("sheets", "v4", credentials=creds)


def _require_sheet_id():
    if not SHEET_ID:
        raise SystemExit("GOOGLE_SHEET_ID non défini (voir .env.example).")


def read_all(svc=None):
    """Renvoie (headers, rows) — rows = lignes non vides sous l'en-tête."""
    _require_sheet_id()
    svc = svc or service()
    rows = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=SHEET_ID, range=f"'{TAB}'!A1:Z100000")
        .execute()
        .get("values", [])
    )
    if not rows:
        return [], []
    header = rows[0]
    return header, [r for r in rows[1:] if r and r[0].strip()]


def _col_letter(i):  # 0-based -> A, B, ..., Z, AA...
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def update_cell(key_value, column_name, value, svc=None):
    """Met à jour la cellule (ligne dont la colonne clé == key_value) / colonne `column_name`."""
    _require_sheet_id()
    svc = svc or service()
    header, rows = read_all(svc)
    key_idx = header.index(KEY_COLUMN) if KEY_COLUMN else 0
    col_idx = header.index(column_name)
    for i, row in enumerate(rows):
        cell_key = row[key_idx] if key_idx < len(row) else ""
        if cell_key.strip().lower() == str(key_value).strip().lower():
            cell = f"{_col_letter(col_idx)}{i + 2}"  # +2 : en-tête + index 1-based
            svc.spreadsheets().values().update(
                spreadsheetId=SHEET_ID,
                range=f"'{TAB}'!{cell}",
                valueInputOption="USER_ENTERED",
                body={"values": [[value]]},
            ).execute()
            return cell
    return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        cell = update_cell(sys.argv[1], sys.argv[2], sys.argv[3])
        print(f"✅ MAJ {cell}" if cell else "⚠️ ligne introuvable")
    else:
        hdr, rows = read_all()
        print("Onglet :", TAB)
        print("Colonnes :", hdr)
        print("Lignes :", len(rows))
