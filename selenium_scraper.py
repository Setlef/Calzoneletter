from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def search_and_scrape(query, num_results=5):
    # Set up Chrome in headless mode
    options = Options()
    options.add_argument("--headless")  # Add headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    # Start ChromeDriver
    driver = webdriver.Chrome(options=options)

    # Go to DuckDuckGo Search
    driver.get(f"https://duckduckgo.com/?q={query}&t=h_&ia=web")
    time.sleep(2)  # sleppy for page to load

    # Wait for results to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.result__a"))
        )
    except Exception as e:
        print("Timeout waiting for results:", e)
        driver.quit()
        return []

    links = []
    # DuckDuckGo result links have class "result__a"
    results = driver.find_elements(By.CSS_SELECTOR, "a.result__a")
    for elem in results:
        print(elem.get_attribute("outerHTML"))
        href = elem.get_attribute("href")
        if href and href.startswith("http"):
            links.append(href)
        if len(links) >= num_results:
            break

    print(driver.page_source)

    driver.quit()
    return links

def scrape_page(url):
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string if soup.title else "No Title"
    paragraph = soup.find('p')
    summary = paragraph.get_text().strip() if paragraph else "No summary available."
    return {"url": url, "title": title, "summary": summary}

if __name__ == "__main__":
    interests = ["AI news", "FPV drone reviews"]
    for topic in interests:
        print(f"Searching for: {topic}")
        links = search_and_scrape(topic, num_results=3)
        for url in links:
            print(f"  {url}")
            article = scrape_page(url)
            print(f"    Title: {article['title']}")
            print(f"    Preview: {article['summary']}")
        print("-" * 30)
# This script uses Selenium to search DuckDuckGo for articles related to user interests.
# It scrapes the page titles and summaries for each link found.