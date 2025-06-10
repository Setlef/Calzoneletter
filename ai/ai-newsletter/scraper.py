import requests
from bs4 import BeautifulSoup

def get_news():
    url = "https://www.techradar.com/news"  # Example target site
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.find_all("h3")  # Adjust the tag as needed for the site

    results = []
    for h in headlines:
        text = h.get_text(strip=True)
        if text:
            results.append(text)

    return results

if __name__ == "__main__":
    articles = get_news()
    for article in articles:
        print(article)
