# plex-genres-anime

Tested with a collection of 657 Animes running this script on Windows. The script utilizes Jikan to get information from MyAnimeList to set the correct genres. During that it will delete all genres set by Plex.

## How-To

Rename `src/settings.py.template` to `src/settings.py` and edit the file. Token can be retrieved using the following method: [Plex Support Article](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```

## Contribute

Feel free to fork and add your own matches to `manual_match.py` and create a PR. Open for every change.
