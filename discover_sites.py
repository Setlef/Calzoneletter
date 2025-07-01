import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def google_search(query, num_results=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    # Google search URL
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
    resp = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    # Google search results links
    results = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and "/url?q=" in href:
            url = href.split("/url?q=")[1].split("&")[0]
            if url.startswith("http") and "google.com" not in url:
                results.append(url)
    return results[:num_results]

def discover_sites_for_user_interests(interests):
    sites = set()
    for interest in interests:
        print(f"Searching for: {interest}")
        found = google_search(f"{interest} news", num_results=5)
        sites.update(found)
        time.sleep(1)  # Be polite to Google!
    return list(sites)

if __name__ == "__main__":
    # Example interests:
    interests = ["AI", "RPG games", "FPV drones"]
    links = discover_sites_for_user_interests(interests)
    print("\n".join(links))
