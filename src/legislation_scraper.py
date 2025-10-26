from typing import Dict, List
import requests
from datetime import datetime, timezone
from dateutil import parser as dateparser
from bs4 import BeautifulSoup


class LegislationScraper:
	def __init__(self) -> None:
		self.base_url = "https://www.legislation.gov.au"
		
	def fetch_whats_new(self, since: str, max_items: int = 50) -> List[Dict]:
		"""
		Scrape Federal Register of Legislation "What's new" page.
		Returns items published after the given date.
		"""
		since_dt = dateparser.parse(since)
		if not since_dt.tzinfo:
			since_dt = since_dt.replace(tzinfo=timezone.utc)
		
		results: List[Dict] = []
		
		# Categories to scrape
		categories = [
			"/whats-new/acts",
			"/whats-new/legislative-instruments",
			"/whats-new/notifiable-instruments",
			"/whats-new/gazettes",
		]
		
		for category in categories:
			url = f"{self.base_url}{category}"
			print(f"    Fetching legislation: {url}")
			
			try:
				resp = requests.get(url, timeout=15, headers={
					"User-Agent": "Mozilla/5.0 (compatible; AI Market Intelligence Bot)"
				})
				resp.raise_for_status()
				soup = BeautifulSoup(resp.text, 'html.parser')
				
				# Find all legislation items (typical structure: div.item or li with links)
				items = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and ('item' in x.lower() or 'result' in x.lower()))[:max_items]
				
				for item in items:
					# Extract title and link
					link_tag = item.find('a')
					if not link_tag:
						continue
					
					title = link_tag.get_text(strip=True)
					href = link_tag.get('href', '')
					if href and not href.startswith('http'):
						href = f"{self.base_url}{href}"
					
					# Try to extract date
					date_tag = item.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower() if x else False)
					pub_date = None
					if date_tag:
						date_str = date_tag.get('datetime') or date_tag.get_text(strip=True)
						try:
							pub_date = dateparser.parse(date_str)
							if not pub_date.tzinfo:
								pub_date = pub_date.replace(tzinfo=timezone.utc)
						except:
							pass
					
					# Filter by date if available
					if pub_date and pub_date <= since_dt:
						continue
					
					# Extract description if available
					desc_tag = item.find(['p', 'div'], class_=lambda x: x and ('desc' in x.lower() or 'summary' in x.lower()) if x else False)
					description = desc_tag.get_text(strip=True) if desc_tag else title
					
					results.append({
						"title": title,
						"description": description,
						"content": description,
						"url": href,
						"source": "Federal Register of Legislation",
						"publishedAt": pub_date.isoformat() if pub_date else None,
						"_source_type": "Legislation",
					})
					
					if len(results) >= max_items:
						break
				
			except Exception as e:
				print(f"    Error fetching {url}: {e}")
				continue
		
		print(f"    Found {len(results)} legislation items")
		return results
