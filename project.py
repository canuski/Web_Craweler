import aiohttp
import asyncio
import re
import json
import sys
from collections import Counter
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def haal_uurl(url):
    async with aiohttp.ClientSession() as sessie:
        async with sessie.get(url) as res:
            return await res.text()

async def haal_woorden_en_links(url, base_url):
    html = await haal_uurl(url)
    
    # Html parsen met beautifulsoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # alle text wordt gevonden met regex
    test_elemente = soup.find_all(text=True)
    woorden = re.findall(r'\b\w+\b', ' '.join(test_elemente).lower())
    
    # tellen hoeveel keer een woord voorkomt
    word_counts = Counter(woorden)
    
    # vind allle links en zet ze om naar relatieve urls
    links = [urljoin(base_url, a.get('href')) for a in soup.find_all('a', href=True)]
    
    return word_counts, links

async def crawl_page(url, base_url, geweest, max_diepete, current_diepte=0):
    if url in geweest or current_diepte > max_diepete:
        return {}

    geweest.add(url)
    print(f"Crawling: {url}")


    #hier ondervond ik veel problemen, zeker zeggen in verslag. slechte urls
    try:
        word_counts, links = await haal_woorden_en_links(url, base_url)
    except aiohttp.client_exceptions.InvalidURL:
        print(f"Skipping invalid URL: {url}")
        return {}

    res = {url: word_counts}

    # elke link recursief crawlen
    for link in links:
        res.update(await crawl_page(link, base_url, geweest, max_diepete, current_diepte + 1))

    return res

async def main(start_url, output_json, max_diepete=2):
    res = await crawl_page(start_url, start_url, set(), max_diepete)

    # tel totaal woorden op
    totalword_counts = Counter()
    for word_counts in res.values():
        totalword_counts.update(word_counts)

    # voeg total property toe aan dict
    res["total"] = dict(totalword_counts)

    # opslagen in json
    with open(output_json, 'w') as json_file:
        json.dump(res, json_file, indent=2)


start_url = sys.argv[1]
output_json = sys.argv[2]

asyncio.run(main(start_url, output_json))
