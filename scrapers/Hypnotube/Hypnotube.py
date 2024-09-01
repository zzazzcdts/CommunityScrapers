import os
import sys
import json
import datetime

# to import from a parent directory we need to add that directory to the system path
csd = os.path.dirname(
    os.path.realpath(__file__))  # get current script directory
parent = os.path.dirname(csd)  # parent directory (should be the scrapers one)
sys.path.append(
    parent
)  # add parent dir to sys path so that we can import py_common from there

try:
    # Import Stash logging system from py_common
    from py_common import log
except ModuleNotFoundError:
    print(
        "You need to download the folder 'py_common' from the community repo. (CommunityScrapers/tree/master/scrapers/py_common)",
        file=sys.stderr)
    sys.exit()

try:
    # Import necessary modules.
    from lxml import html
    import requests
    from requests import utils
    from requests import cookies
    import re
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup

    # Set headers with user agent to avoid Cloudflare throwing a hissy fit.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.8",
        "Content-Type": "application/json"
    }
    # Establish session and implement headers.
    session = requests.Session()
    session.headers.update(headers)

# If one of these modules is not installed:
except ModuleNotFoundError:
    log.error(
        "You need to install the python modules mentioned in requirements.txt"
    )
    log.error(
        "If you have pip (normally installed with python), run this command in a terminal from the directory the scraper is located: pip install -r requirements.txt"
    )
    sys.exit()
    
def scrape_search(query):
    url = f"https://hypnotube.com/searchgate.php"
    # Create a POST request with our search query
    payload = {
        "q": query
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "sec-fetch-site": "same-origin"
    }

    # Send the POST request and get the response
    session = requests.Session()  # Ensure session is established if not already
    response = session.post(url, data=payload, headers=headers, allow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_cols = soup.find_all('div', class_='item-col col')
    refactored_json = []
    for item_col in item_cols:
        # Now find the item-inner-col inner-col within each item-col col
        card = item_col.find('div', class_='item-inner-col inner-col')
        if card:
            title_tag = card.find('a', href=True, title=True)
            title = title_tag.get('title')
            url = title_tag.get('href')
            if '/video/' not in url:
                continue

            image_tag = card.find('img', attrs={'data-mb': 'shuffle-thumbs'})
            image_src = image_tag['src']

            refactored_data = {
                "title": title,
                "url": url,
                "image": image_src
            }
            refactored_json.append(refactored_data)
        
    
    print(json.dumps(refactored_json, indent=4))
    

def main():
    fragment = json.loads(sys.stdin.read())
    url = fragment.get("url")
    title = fragment.get("title")
    name = fragment.get("name")
    # If nothing is passed to the script:
    if url is None and title is None and name is None:
        log.error("No URL/Title/Name provided")
        sys.exit(1)
    if name is not None:
        scrape_search(name)

if __name__ == "__main__":
    main()

# Last updated September 1, 2024
