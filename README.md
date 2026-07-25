# claude-sheets-sync

Connecte un script (ou un agent comme **Claude Code**) à un **Google Sheet** en lecture/écriture, via OAuth. Léger, sans dépendance à un service tiers, token réutilisable.

Deux fichiers suffisent :

| Fichier | Rôle |
|---|---|
| `gsheet_auth.py` | Fait le login Google **une seule fois** et sauvegarde `token.json` |
| `gsheet.py` | Lit le sheet et met à jour n'importe quelle cellule par clé de ligne |

---

## Comment marche la synchro (le principe)

Google n'accepte pas un simple mot de passe pour ses API : il faut un **jeton OAuth**. Pour une app locale (« Desktop app »), on utilise le **flux loopback** :

```
1. Le script génère une URL d'autorisation Google et démarre
   un mini-serveur local sur http://localhost:8765
        │
2. Tu ouvres l'URL → tu choisis ton compte Google → « Autoriser »
        │
3. Google redirige vers http://localhost:8765/?code=...
   → le mini-serveur capte le code, l'échange contre un jeton
        │
4. Le jeton est écrit dans token.json (avec un refresh_token)
        │
5. Tous les appels suivants réutilisent token.json.
   Quand il expire, il se renouvelle tout seul → plus jamais de login.
```

Aucun secret ne transite par le navigateur : le code d'autorisation revient sur `localhost`, et l'échange code→jeton se fait en local. Le scope demandé est `spreadsheets` (lecture **et** écriture).

Ensuite, `gsheet.py` mappe **une valeur clé → une ligne** (par défaut la 1re colonne, ex. un identifiant unique) et écrit dans la colonne voulue grâce à l'API `values().update`. Un agent peut donc dire *« passe le statut de @exemple_user à Envoyé »* et la bonne cellule est mise à jour.

---

## Installation express (2 min)

```bash
git clone https://github.com/<toi>/claude-sheets-sync.git
cd claude-sheets-sync
pip install -r requirements.txt
```

### 1. Créer un identifiant OAuth Google (une fois)

1. [Google Cloud Console](https://console.cloud.google.com/) → nouveau projet
2. **APIs & Services → Library** → active **Google Sheets API**
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**
4. Type d'application : **Desktop app**
5. Télécharge le `.json` et pose-le à la racine (il s'appelle `client_secret_*.json`)

> `client_secret_*.json` et `token.json` sont déjà dans `.gitignore` — ils ne partiront jamais sur GitHub.

### 2. Configurer le sheet

```bash
cp .env.example .env
# renseigne GOOGLE_SHEET_ID et SHEET_TAB dans .env, puis :
set -a && . ./.env && set +a
```

### 3. S'authentifier (une fois)

```bash
python gsheet_auth.py
```

Ouvre l'URL affichée, autorise, c'est fini. `token.json` est créé.
> Écran « app non vérifiée » ? C'est ton propre client OAuth → **Paramètres avancés → Continuer**.

---

## Utilisation

```bash
# Voir les colonnes et le nombre de lignes
python gsheet.py

# Mettre à jour une cellule : <clé de ligne> <nom de colonne> <valeur>
python gsheet.py "@exemple_user" "Statut message" "Envoyé"
```

En Python :

```python
from gsheet import read_all, update_cell

header, rows = read_all()
update_cell("@exemple_user", "Statut appel", "RDV pris")
```

---

## Sécurité

- Les secrets (`client_secret_*.json`, `token.json`, `.env`) sont **git-ignorés**.
- Le token ne donne accès qu'au scope Sheets, révocable à tout moment sur [myaccount.google.com/permissions](https://myaccount.google.com/permissions).

## Licence

MIT
