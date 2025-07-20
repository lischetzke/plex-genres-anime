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
    finished = []
    try:
        with open('finished.txt', 'r', encoding='utf-8') as file:
            finished = file.read().splitlines()
    except FileNotFoundError:
        pass
    
    for anime in animes:
        if anime.title in finished:
            #print(f'Skipping "{anime.title}" as it was marked as processed in file.')
            continue
        
        print(f'Processing "{anime.title}":')
        await process(plex, jikan, library, anime)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(startProcessing())
    except KeyboardInterrupt:
        pass
