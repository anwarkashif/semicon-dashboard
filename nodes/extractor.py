import os
import re
import random
import requests
import warnings
from bs4 import BeautifulSoup
import trafilatura
from typing import Dict, Any, List

warnings.filterwarnings("ignore")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

class ExtractorNode:
    def __init__(self):
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive"
        }

    def clean_urls_from_text(self, text: str) -> List[str]:
        raw_urls = re.findall(r'https?://[^\s<>"]+', text)
        cleaned_urls = []
        for url in raw_urls:
            cleaned = url.rstrip(')\]}.,;')
            if cleaned not in cleaned_urls:
                cleaned_urls.append(cleaned)
        return cleaned_urls

    def _extract_search_query(self, prompt: str) -> str:
        title_match = re.search(r'(?:Title|TARGET DEVELOPMENT DETAILS):\s*\*?\s*\[?([^\]\n\r]+)\]?', prompt, re.IGNORECASE)
        if title_match: return title_match.group(1).strip()
        clean_text = re.sub(r'(?i)conduct a rigorous.*assessment|review the provided context.*synthesized|your response must follow.*words:', '', prompt)
        clean_text = re.sub(r'[\[\]\(\)\-\*]', ' ', clean_text)
        return " ".join(clean_text.split()[:12]).strip()

    def _fetch_live_search_urls(self, query: str) -> List[str]:
        print(f"[Node 2] Initiating Free Search Engine bypass for: '{query}'")
        found_urls = []
        try:
            # Native DDGS direct call execution block
            from ddgs import DDGS
            with DDGS() as ddgs_client:
                results = ddgs_client.text(query, max_results=3)
                if results:
                    for r in results:
                        link = r.get('href') or r.get('link')
                        if link: found_urls.append(link)
        except Exception as e:
            print(f"[Node 2] Search library fallback engaged: {e}")
        
        if not found_urls:
            try:
                url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
                res = self.session.get(url, headers=self._get_headers(), timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    links = soup.find_all("a", class_="result__url")
                    for link in links[:3]:
                        href = link.get("href")
                        if href:
                            if "/l/?" in href:
                                match = re.search(r'uddg=([^&]+)', href)
                                if match: href = requests.utils.unquote(match.group(1))
                            found_urls.append(href)
            except Exception as scrape_err:
                print(f"[Node 2] Direct HTML search scraper failed: {scrape_err}")
        return found_urls

    def clean_html_fallback(self, raw_html: str) -> str:
        soup = BeautifulSoup(raw_html, "html.parser")
        for element in soup(["script", "style", "nav", "header", "footer", "form", "aside", "noscript"]): element.extract()
        for class_signature in ["cookie", "consent", "privacy", "banner", "popup", "advertisement"]:
            for match in soup.find_all(class_=lambda x: x and class_signature in str(x).lower()): match.extract()
            for match in soup.find_all(id=lambda x: x and class_signature in str(x).lower()): match.extract()
        lines = (line.strip() for line in soup.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        urls: List[str] = state.get("current_target_urls", [])
        user_cmd: str = state.get("user_prompt", "")
        extracted_payloads = []

        if urls:
            print("[Node 2] Sanitizing incoming target URLs from state vector...")
            urls = [url.strip().rstrip(')\]}.,;') for url in urls]

        if not urls and user_cmd:
            urls = self.clean_urls_from_text(user_cmd)
            
        if not urls and user_cmd:
            search_query = self._extract_search_query(user_cmd)
            if search_query: urls = self._fetch_live_search_urls(search_query)

        state["current_target_urls"] = urls
        print(f"[Node 2] Extracting content from {len(urls)} localized target feeds...")

        for url in urls:
            if not url.startswith(("http://", "https://")): continue
            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    markdown_result = trafilatura.extract(
                        downloaded, output_format="markdown", include_links=True, include_images=False, no_fallback=False
                    )
                    if markdown_result and len(markdown_result.strip()) > 200:
                        extracted_payloads.append({"source_url": url, "content": markdown_result.strip(), "method": "trafilatura_direct"})
                        continue

                response = self.session.get(url, headers=self._get_headers(), timeout=15, allow_redirects=True)
                if response.status_code == 200:
                    clean_text = self.clean_html_fallback(response.text)
                    if len(clean_text) > 100:
                        extracted_payloads.append({"source_url": url, "content": f"### Source: {url}\n\n{clean_text}", "method": "hardened_fallback_soup"})
            except Exception as error:
                print(f"[Node 2] Direct pipeline error bypass on address {url}: {str(error)}")
                continue

        state["extracted_markdown_context"] = extracted_payloads
        return state