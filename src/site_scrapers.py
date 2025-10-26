"""
Direct web scrapers for curated news sites.
Each scraper is tailored to the specific site's HTML structure.
"""

from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as dateparser
import time


class SiteScrapers:
	def __init__(self):
		self.timeout = 15
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
		}
	
	def _parse_date(self, date_str: str) -> datetime:
		"""Try to parse various date formats."""
		try:
			dt = dateparser.parse(date_str)
			if dt and not dt.tzinfo:
				dt = dt.replace(tzinfo=timezone.utc)
			return dt
		except:
			return None
	
	def scrape_afr_financial_services(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape Australian Financial Review - Financial Services section."""
		since_dt = self._parse_date(since)
		results = []
		
		urls_to_scrape = [
			"https://www.afr.com/companies/financial-services",
			"https://www.afr.com/technology/fintech",
		]
		
		for url in urls_to_scrape:
			try:
				print(f"    Scraping AFR: {url}")
				resp = requests.get(url, timeout=self.timeout, headers=self.headers)
				resp.raise_for_status()
				soup = BeautifulSoup(resp.text, 'html.parser')
				
				# AFR uses article tags with specific classes
				articles = soup.find_all('article', limit=max_items)
				
				for article in articles:
					# Find link
					link_tag = article.find('a', href=True)
					if not link_tag:
						continue
					
					title = link_tag.get_text(strip=True) or article.find('h3')
					if isinstance(title, str):
						title_text = title
					else:
						title_text = title.get_text(strip=True) if title else "Untitled"
					
					href = link_tag['href']
					if href.startswith('/'):
						href = f"https://www.afr.com{href}"
					
					# Try to find description
					desc_tag = article.find(['p', 'div'], class_=lambda x: x and 'summary' in x.lower() if x else False)
					description = desc_tag.get_text(strip=True) if desc_tag else title_text
					
					results.append({
						"title": title_text,
						"description": description,
						"content": description,
						"url": href,
						"source": "Australian Financial Review",
						"publishedAt": None,
						"_source_type": "Scraper",
					})
				
				print(f"    Found {len(articles)} AFR articles")
				time.sleep(1)  # Be polite
				
			except Exception as e:
				print(f"    Error scraping AFR: {e}")
		
		return results[:max_items]
	
	def scrape_asic_media_releases(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape ASIC media releases."""
		since_dt = self._parse_date(since)
		results = []
		url = "https://asic.gov.au/about-asic/news-centre/find-a-media-release/"
		
		try:
			print(f"    Scraping ASIC: {url}")
			resp = requests.get(url, timeout=self.timeout, headers=self.headers)
			resp.raise_for_status()
			soup = BeautifulSoup(resp.text, 'html.parser')
			
			# Find all links in the results area
			links = soup.find_all('a', href=lambda x: x and '/media-releases/' in x)
			
			for link in links[:max_items]:
				title = link.get_text(strip=True)
				href = link.get('href', '')
				
				if href.startswith('/'):
					href = f"https://asic.gov.au{href}"
				
				# Extract date from URL or text if possible
				# ASIC URLs often contain date: /media-releases/2024/
				
				results.append({
					"title": title,
					"description": title,
					"content": title,
					"url": href,
					"source": "ASIC",
					"publishedAt": None,
					"_source_type": "Scraper",
				})
			
			print(f"    Found {len(results)} ASIC articles")
			
		except Exception as e:
			print(f"    Error scraping ASIC: {e}")
		
		return results
	
	def scrape_innovationaus(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape InnovationAus fintech and regtech sections."""
		since_dt = self._parse_date(since)
		results = []
		
		categories = [
			"https://www.innovationaus.com/category/fintech/",
			"https://www.innovationaus.com/category/regulation/",
		]
		
		for url in categories:
			try:
				print(f"    Scraping InnovationAus: {url}")
				resp = requests.get(url, timeout=self.timeout, headers=self.headers)
				resp.raise_for_status()
				soup = BeautifulSoup(resp.text, 'html.parser')
				
				# Find article links
				articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'post' in x.lower() if x else False, limit=max_items//2)
				
				for article in articles:
					link_tag = article.find('a', href=True)
					if not link_tag:
						continue
					
					title_tag = article.find(['h2', 'h3'])
					title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
					
					href = link_tag['href']
					if not href.startswith('http'):
						href = f"https://www.innovationaus.com{href}"
					
					results.append({
						"title": title,
						"description": title,
						"content": title,
						"url": href,
						"source": "InnovationAus",
						"publishedAt": None,
						"_source_type": "Scraper",
					})
				
				print(f"    Found {len(articles)} InnovationAus articles from {url}")
				time.sleep(1)
				
			except Exception as e:
				print(f"    Error scraping InnovationAus: {e}")
		
		return results[:max_items]
	
	def scrape_interest_nz(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape Interest.co.nz banking section."""
		since_dt = self._parse_date(since)
		results = []
		url = "https://www.interest.co.nz/banking"
		
		try:
			print(f"    Scraping Interest.co.nz: {url}")
			resp = requests.get(url, timeout=self.timeout, headers=self.headers)
			resp.raise_for_status()
			soup = BeautifulSoup(resp.text, 'html.parser')
			
			# Find article headlines
			articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('article' in x.lower() or 'story' in x.lower()) if x else False, limit=max_items)
			
			for article in articles:
				link_tag = article.find('a', href=True)
				if not link_tag:
					continue
				
				title = link_tag.get_text(strip=True)
				href = link_tag['href']
				
				if href.startswith('/'):
					href = f"https://www.interest.co.nz{href}"
				
				results.append({
					"title": title,
					"description": title,
					"content": title,
					"url": href,
					"source": "Interest.co.nz",
					"publishedAt": None,
					"_source_type": "Scraper",
				})
			
			print(f"    Found {len(results)} Interest.co.nz articles")
			
		except Exception as e:
			print(f"    Error scraping Interest.co.nz: {e}")
		
		return results
	
	def scrape_itnews(self, since: str, max_items: int = 20) -> List[Dict]:
		"""Scrape ITnews.com.au for identity, security, fintech topics."""
		since_dt = self._parse_date(since)
		results = []
		
		topics = [
			"https://www.itnews.com.au/topic/financial-services",
			"https://www.itnews.com.au/topic/security",
		]
		
		for url in topics:
			try:
				print(f"    Scraping ITnews: {url}")
				resp = requests.get(url, timeout=self.timeout, headers=self.headers)
				resp.raise_for_status()
				soup = BeautifulSoup(resp.text, 'html.parser')
				
				# Find articles
				articles = soup.find_all(['article', 'div'], class_=lambda x: x and 'story' in x.lower() if x else False, limit=max_items//2)
				
				for article in articles:
					link_tag = article.find('a', href=True)
					if not link_tag:
						continue
					
					title = link_tag.get_text(strip=True)
					href = link_tag['href']
					
					if href.startswith('/'):
						href = f"https://www.itnews.com.au{href}"
					
					results.append({
						"title": title,
						"description": title,
						"content": title,
						"url": href,
						"source": "ITnews",
						"publishedAt": None,
						"_source_type": "Scraper",
					})
				
				print(f"    Found {len(articles)} ITnews articles from {url}")
				time.sleep(1)
				
			except Exception as e:
				print(f"    Error scraping ITnews: {e}")
		
		return results[:max_items]
	
	def scrape_all(self, since: str, max_per_site: int = 10) -> List[Dict]:
		"""Scrape all curated sites."""
		all_articles = []
		
		print("  Scraping curated news sites...")
		all_articles.extend(self.scrape_afr_financial_services(since, max_per_site))
		all_articles.extend(self.scrape_asic_media_releases(since, max_per_site))
		all_articles.extend(self.scrape_innovationaus(since, max_per_site))
		all_articles.extend(self.scrape_interest_nz(since, max_per_site))
		all_articles.extend(self.scrape_itnews(since, max_per_site))
		
		print(f"  Total scraped: {len(all_articles)} articles from curated sites")
		return all_articles


