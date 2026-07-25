#!/usr/bin/env python3
"""
OAuth Google Sheets — flux loopback localhost.
Génère un token.json réutilisable (avec refresh automatique).

Usage:
    python gsheet_auth.py

Le script imprime une URL d'autorisation Google, démarre un petit serveur
local sur http://localhost:8765 pour récupérer le code, puis sauvegarde
token.json à la racine du projet.
"""
import glob
import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.path.join(ROOT, "token.json")
PORT = int(os.environ.get("OAUTH_PORT", "8765"))


def main():
    secrets = glob.glob(os.path.join(ROOT, "client_secret_*.json"))
    if not secrets:
        raise SystemExit(
            "Aucun fichier client_secret_*.json trouvé.\n"
            "→ Télécharge tes identifiants OAuth (type « Desktop app ») depuis "
            "Google Cloud Console et place le .json à la racine du projet."
        )

    flow = InstalledAppFlow.from_client_secrets_file(secrets[0], SCOPES)
    creds = flow.run_local_server(
        host="localhost",
        port=PORT,
        open_browser=False,
        prompt="consent",
        access_type="offline",
        authorization_prompt_message="\n👉 Ouvre cette URL et autorise :\n\n{url}\n",
        success_message="✅ Autorisation reçue. Tu peux fermer cet onglet.",
    )
    with open(TOKEN, "w") as f:
        f.write(creds.to_json())
    print(f"\n✅ Token sauvegardé : {TOKEN}")


if __name__ == "__main__":
    main()
