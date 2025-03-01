from settings import *
from plexapi.server import PlexServer
from jikan4snek import Jikan4SNEK, dump
from genres import process
import sys
import asyncio

try:
    plex = PlexServer(plex_url, plex_token)
    print(f'Connected to {plex_url} ({plex.identity().machineIdentifier})')
except:
    print(f'Could not connect to {plex_url}')
    sys.exit()

try:
    jikan = Jikan4SNEK()
except:
    print(f'Error initializing Jikan')
    sys.exit()

all_libraries = plex.library.sections()
library = None
for lib in all_libraries:
    if lib.title != plex_library:
        continue
    library = lib
    break

if library == None:
    print(f'Found no matching library, possible libraries are: {[lib.title for lib in all_libraries]}')
    sys.exit()
else:
    print(f'Found library {library.title} of type {library.type}')

animes = library.all()

async def startProcessing():
    for anime in animes:
        print(f'Processing "{anime.title}":')
        await process(plex, jikan, library, anime)

loop = asyncio.get_event_loop()
loop.run_until_complete(startProcessing())