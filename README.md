# plex-genres-anime

Tested with a collection of 516 Animes on Windows

## How-To

Rename `src/settings.py.template` to `src/settings.py` and edit the file. Token can be retrieved using the following method: [Plex Support Article](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/main.py
```
