"""
Web scrapers for Australian and NZ financial regulators.
Targets media releases and news pages directly since RSS feeds are broken.
"""

from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as dateparser


class RegulatorScrapers:
	def __init__(self):
		self.timeout = 15
		self.headers = {"User-Agent": "Mozilla/5.0 (compatible; AI Market Intelligence Bot)"}
	
	def scrape_asic(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape ASIC media releases."""
		since_dt = dateparser.parse(since)
		if not since_dt.tzinfo:
			since_dt = since_dt.replace(tzinfo=timezone.utc)
		
		results = []
		url = "https://asic.gov.au/about-asic/news-centre/find-a-media-release/"
		
		try:
			print(f"    Scraping ASIC: {url}")
			resp = requests.get(url, timeout=self.timeout, headers=self.headers)
			resp.raise_for_status()
			soup = BeautifulSoup(resp.text, 'html.parser')
			
			# Find media release items (typical structure)
			items = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and ('release' in x.lower() or 'item' in x.lower() or 'result' in x.lower()) if x else False)
			
			for item in items[:max_items]:
				link_tag = item.find('a')
				if not link_tag:
					continue
				
				title = link_tag.get_text(strip=True)
				href = link_tag.get('href', '')
				if href and not href.startswith('http'):
					href = f"https://asic.gov.au{href}"
				
				# Try to extract date
				date_tag = item.find(['time', 'span'], class_=lambda x: x and 'date' in x.lower() if x else False)
				pub_date = None
				if date_tag:
					date_str = date_tag.get('datetime') or date_tag.get_text(strip=True)
					try:
						pub_date = dateparser.parse(date_str)
						if pub_date and not pub_date.tzinfo:
							pub_date = pub_date.replace(tzinfo=timezone.utc)
					except:
						pass
				
				# Filter by date
				if pub_date and pub_date <= since_dt:
					continue
				
				results.append({
					"title": title,
					"description": title,  # No description from listing page
					"content": title,
					"url": href,
					"source": "ASIC",
					"publishedAt": pub_date.isoformat() if pub_date else None,
					"_source_type": "Regulator",
				})
			
			print(f"    Found {len(results)} ASIC items")
		except Exception as e:
			print(f"    Error scraping ASIC: {e}")
		
		return results
	
	def scrape_apra(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape APRA news and publications."""
		since_dt = dateparser.parse(since)
		if not since_dt.tzinfo:
			since_dt = since_dt.replace(tzinfo=timezone.utc)
		
		results = []
		url = "https://www.apra.gov.au/news-and-publications"
		
		try:
			print(f"    Scraping APRA: {url}")
			resp = requests.get(url, timeout=self.timeout, headers=self.headers)
			resp.raise_for_status()
			soup = BeautifulSoup(resp.text, 'html.parser')
			
			items = soup.find_all(['article', 'div', 'li'], class_=lambda x: x and ('news' in x.lower() or 'item' in x.lower()) if x else False)
			
			for item in items[:max_items]:
				link_tag = item.find('a')
				if not link_tag:
					continue
				
				title = link_tag.get_text(strip=True)
				href = link_tag.get('href', '')
				if href and not href.startswith('http'):
					href = f"https://www.apra.gov.au{href}"
				
				results.append({
					"title": title,
					"description": title,
					"content": title,
					"url": href,
					"source": "APRA",
					"publishedAt": None,
					"_source_type": "Regulator",
				})
			
			print(f"    Found {len(results)} APRA items")
		except Exception as e:
			print(f"    Error scraping APRA: {e}")
		
		return results
	
	def scrape_all(self, since: str, max_per_source: int = 20) -> List[Dict]:
		"""Scrape all regulators."""
		all_items = []
		all_items.extend(self.scrape_asic(since, max_per_source))
		all_items.extend(self.scrape_apra(since, max_per_source))
		return all_items


