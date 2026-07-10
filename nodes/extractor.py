import os
import random
import requests
from bs4 import BeautifulSoup
import trafilatura
from typing import Dict, Any, List

# Target list of modern browser user-agents to bypass initial scraping signatures
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

class ExtractorNode:
    """
    Node 2: The Extractor Component
    Optimized to bypass Cloudflare barriers and output standardized markdown.
    """
    def __init__(self):
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Generates authentic browser headers dynamically."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

    def clean_html_fallback(self, raw_html: str) -> str:
        """
        Fallback extraction engine that aggressively strips HTML cookie walls, 
        scripts, style layers, and headers to secure pure contextual text.
        """
        soup = BeautifulSoup(raw_html, "html.parser")
        
        # Eliminate non-content noise fields
        for element in soup(["script", "style", "nav", "header", "footer", "form", "aside", "noscript"]):
            element.extract()
            
        # Target common cookie/privacy consent banner signatures
        for class_signature in ["cookie", "consent", "privacy", "banner", "popup", "advertisement"]:
            for match in soup.find_all(class_=lambda x: x and class_signature in str(x).lower()):
                match.extract()
            for match in soup.find_all(id=lambda x: x and class_signature in str(x).lower()):
                match.extract()

        # Extract textual strings cleanly
        lines = (line.strip() for line in soup.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph Node execution logic step.
        Consumes: state["current_target_urls"]
        Produces: state["extracted_markdown_context"]
        """
        urls: List[str] = state.get("current_target_urls", [])
        extracted_payloads = []

        print(f"[Node 2] Extracting content from {len(urls)} localized target feeds...")

        for url in urls:
            if not url.startswith(("http://", "https://")):
                print(f"[Node 2] Skipping invalid target payload scheme: {url}")
                continue
                
            try:
                # Execution Pass 1: Attempt native Trafilatura fetch
                downloaded = trafilatura.fetch_url(url)
                
                if downloaded:
                    # Parse out clean layout via Trafilatura
                    markdown_result = trafilatura.extract(
                        downloaded, 
                        output_format="markdown",
                        include_links=True,
                        include_images=False,
                        no_fallback=False
                    )
                    
                    if markdown_result and len(markdown_result.strip()) > 200:
                        extracted_payloads.append({
                            "source_url": url,
                            "content": markdown_result.strip(),
                            "method": "trafilatura_direct"
                        })
                        continue

                # Execution Pass 2: Hardened Request Fallback with Browser Mimicry
                response = self.session.get(
                    url, 
                    headers=self._get_headers(), 
                    timeout=15, 
                    allow_redirects=True
                )
                
                # Check for direct Cloudflare block signatures (403/503 browser checks)
                if response.status_code in [403, 503] and "cloudflare" in response.text.lower():
                    print(f"[Node 2] Warning: Cloudflare challenge triggered at {url}. Initiating sanitization routing.")
                
                if response.status_code == 200:
                    clean_text = self.clean_html_fallback(response.text)
                    if len(clean_text) > 100:
                        extracted_payloads.append({
                            "source_url": url,
                            "content": f"### Source: {url}\n\n{clean_text}",
                            "method": "hardened_fallback_soup"
                        })
                    else:
                        print(f"[Node 2] Empty extraction footprint returned from {url}")
                else:
                    print(f"[Node 2] Failed connection status {response.status_code} for target: {url}")

            except Exception as error:
                print(f"[Node 2] Direct pipeline error bypass on address {url}: {str(error)}")
                continue

        # Update LangGraph structural state architecture smoothly
        state["extracted_markdown_context"] = extracted_payloads
        return state