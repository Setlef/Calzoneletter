import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from tinydb import TinyDB

def ddg_search(query, num_results=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    resp = requests.post(search_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    # DuckDuckGo result links are in <a class="result__a">
    for a in soup.find_all('a', class_='result__a', href=True):
        href = a['href']
        if href.startswith('http'):
            results.append(href)
        if len(results) >= num_results:
            break
    return results

def find_articles_for_user(user, articles_per_interest=3):
    all_results = []
    for interest in user['interests']:
        print(f"Searching for: {interest}")
        query = f"{interest} news"
        links = ddg_search(query, num_results=articles_per_interest)
        all_results.append({
            "interest": interest,
            "articles": links
        })
        time.sleep(1)  # Be polite to DuckDuckGo!
    return all_results

if __name__ == "__main__":
    db = TinyDB('db.json')
    users = db.all()

    for user in users:
        print(f"-----\nUser: {user['name']}")
        results = find_articles_for_user(user)
        for topic in results:
            print(f"\nInterest: {topic['interest']}")
            for url in topic['articles']:
                print(f"  {url}")
# This script finds articles for each user's interests by searching Google News.
# It uses the TinyDB database to retrieve user data and prints the results.