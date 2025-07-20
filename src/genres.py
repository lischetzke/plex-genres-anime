from manual_match import manuals
from time import sleep

debug_list = [
    #"Fruits Basket",
    #"Akuma Kun",
    #"Magic Kaito: Kid the Phantom Thief",
]

def normalize_string(str):
    if str == None:
        return str
    result = str.lower()
    result = ''.join(char for char in result if (ord(char) >= 97 and ord(char) <= 122) or (ord(char) >= 65 and ord(char) <= 90))
    if result == None or result == "":
        # jp, only remove whitespaces
        result = str.lower()
        result = ''.join(char for char in result if ord(char) != 32)
    return result

def prep_jikan(jikan_anime, type="TV"):
    data = jikan_anime["data"]
    data = [d for d in data if d["type"] == type]
    results = data[:5]
    return results

def filter_jikan_time(jikan_data, year, deviation):
    results = []
    year_filtering = list(range(year-deviation, year+deviation+1))
    
    for data in jikan_data:
        year = data["year"]
        if year == None and data["aired"]["from"] != None:
            # Check using airing date
            year_aired = data["aired"]
            if year_aired != None:
                year_aired = year_aired["from"]
            if year_aired != None:
                year = year_aired[0:4]
            year = int(year)
        
        if year not in year_filtering:
            continue
        results += [data]
    return results

def filter_jikan_name(jikan_data, anime_names, normalize=True):
    # titles[i]["title"]
    results = []
    
    def sub(jd):
        jikan_names = jd["titles"]
        for jn in jikan_names:
            title = jn["title"]
            if normalize:
                title = normalize_string(title)
            
            for name in anime_names:
                if title != name:
                    continue
                return [jd]
        return None
    
    for jd in jikan_data:
        res = sub(jd)
        if res != None:
            results += res
    
    return results

async def get_mal(jikan, anime):
    title_t1 = None
    if anime.originalTitle != None:
        title_t1 = anime.originalTitle.split(":")[0]
    anime_titles = list(set(filter(None, [anime.title, anime.originalTitle, title_t1])))
    anime_titles_norm = list(set(filter(None, [normalize_string(anime.title), normalize_string(anime.originalTitle), normalize_string(title_t1)])))
    
    jikan_anime_1 = await jikan.search(anime.title).anime()
    jikan_anime_2 = await jikan.search(anime.originalTitle).anime()
    
    def find_anime(type="TV"):
        a1_filtered1 = prep_jikan(jikan_anime_1, type)
        a1_filtered2 = filter_jikan_time(a1_filtered1, anime.year, 1)
        a1_found_norm = filter_jikan_name(a1_filtered2, anime_titles_norm)
        a1_found = filter_jikan_name(a1_filtered2, anime_titles, False)
        
        a2_filtered1 = prep_jikan(jikan_anime_2, type)
        a2_filtered2 = filter_jikan_time(a2_filtered1, anime.year, 1)
        a2_found_norm = filter_jikan_name(a2_filtered2, anime_titles_norm)
        a2_found = filter_jikan_name(a2_filtered2, anime_titles, False)
        
        if anime.title in debug_list:
            print("BREAKPOINT")
        
        return (a1_found, a1_found_norm, a2_found, a2_found_norm)
    
    flags = {
        "used_ona": False,
        "used_ova": False,
        "used_tvspecial": False,
        "used_manual": False,
    }
    
    (a1_found, a1_found_norm, a2_found, a2_found_norm) = find_anime("TV")
    if (len(a1_found)+len(a1_found_norm)+len(a2_found)+len(a2_found_norm)) == 0:
        (a1_found, a1_found_norm, a2_found, a2_found_norm) = find_anime("ONA")
        flags["used_ona"] = True
    if (len(a1_found)+len(a1_found_norm)+len(a2_found)+len(a2_found_norm)) == 0:
        (a1_found, a1_found_norm, a2_found, a2_found_norm) = find_anime("OVA")
        flags["used_ova"] = True
    if (len(a1_found)+len(a1_found_norm)+len(a2_found)+len(a2_found_norm)) == 0:
        (a1_found, a1_found_norm, a2_found, a2_found_norm) = find_anime("TV Special")
        flags["used_tvspecial"] = True

    id = -1
    if id == -1 and anime.originalTitle in manuals:
        id = manuals[anime.originalTitle]
    if id == -1 and anime.title in manuals:
        id = manuals[anime.title]
    if id != -1:
        try:
            manual_found = await jikan.get(id).anime()
            if manual_found != None:
                manual_found = manual_found["data"]
            if manual_found != None:
                a2_found = [manual_found]
                flags["used_manual"] = True
        except:
            pass

    print(f'  Found {len(a1_found)}/{len(a1_found_norm)}/{len(a2_found)}/{len(a2_found_norm)} results')
    result = None
    if result == None and len(a2_found) == 1:
        result = a2_found[0]
    if result == None and len(a1_found) == 1:
        result = a1_found[0]
    if result == None and len(a1_found_norm) > 0:
        result = a1_found_norm[0]
    if result == None:
        print('  Could not match')
        # Check if title already exists in anime_issues.txt
        try:
            with open('anime_issues.txt', 'r', encoding='utf-8') as file:
                existing_titles = file.read().splitlines()
                if anime.title not in existing_titles:
                    with open('anime_issues.txt', 'a', encoding='utf-8') as file:
                        file.write(f'{anime.title}\n')
        except FileNotFoundError:
            # If file doesn't exist, create it and add the title
            with open('anime_issues.txt', 'w', encoding='utf-8') as file:
                file.write(f'{anime.title}\n')
        return
    print(f'  Using "[{result["mal_id"]}] {result["title"]}" - {result["url"]}')
    return result

def mark_as_finished(anime):
    try:
        with open('finished.txt', 'r', encoding='utf-8') as file:
            existing_titles = file.read().splitlines()
            if anime.title not in existing_titles:
                with open('finished.txt', 'a', encoding='utf-8') as file:
                    file.write(f'{anime.title}\n')
    except FileNotFoundError:
        # If file doesn't exist, create it and add the title
        with open('finished.txt', 'w', encoding='utf-8') as file:
            file.write(f'{anime.title}\n')


async def process(plex, jikan, library, anime):
    # Plex: Reload information
    anime.reload()
    sleep(1)
    
    # Check for autotag label
    for lb in anime.labels:
        tag = lb.tag.lower()
        if tag in ["autotag", "manual"]:
            # skip
            print(f'  Already processed, skipping')
            mark_as_finished(anime)
            return
    
    # Get information
    mal = await get_mal(jikan, anime)
    if mal == None:
        return
    
    # Plex: Reload information
    anime.reload()
    sleep(3)
    
    # Plex: Update genres and label
    print(f'  Remove old genres: {[g.tag for g in anime.genres]}')
    
    new_genres = [m["name"] for m in mal["genres"]]
    new_themes = [m["name"] for m in mal["themes"]]
    print(f'  Add new genres: {new_genres}')
    print(f'  Add themes as genres: {new_themes}')
    anime.removeGenre(anime.genres).reload().addLabel("autotag").addGenre(new_genres + new_themes).reload()
    
    mark_as_finished(anime)
    
    sleep(5)

