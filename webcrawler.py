import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse
import re

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.to_visit_urls = [base_url]

    def fetch_page(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url}: Status code {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def parse_links(self, soup, current_url):
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            if href.startswith('/'):
                href = urljoin(current_url, href)
            elif not bool(urlparse(href).netloc):
                href = urljoin(current_url, href)
            if self.base_url in href:
                links.add(href)
        return links

    def extract_text(self, soup):
        texts = soup.find_all(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    @staticmethod
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def crawl(self, max_pages=10):
        crawled_pages = 0

        while self.to_visit_urls and crawled_pages < max_pages:
            current_url = self.to_visit_urls.pop(0)
            if current_url in self.visited_urls:
                continue

            page_content = self.fetch_page(current_url)
            if page_content is None:
                continue

            soup = BeautifulSoup(page_content, 'html.parser')
            text = self.extract_text(soup)
            print(f"Scraped text from {current_url}:\n{text[:1000]}\n") 

            links = self.parse_links(soup, current_url)
            self.to_visit_urls.extend(links - self.visited_urls)
            self.visited_urls.add(current_url)
            crawled_pages += 1

if __name__ == "__main__":
    base_url = 'https://www.theodinproject.com/lessons/foundations-introduction-to-web-development' 
    crawler = WebCrawler(base_url)
    crawler.crawl(max_pages=3) 
