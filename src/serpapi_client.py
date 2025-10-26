"""
SerpAPI client for Google News searches.
Supports date filtering, site: operators, and Boolean queries.
"""

from typing import Dict, List
import requests
from datetime import datetime, timedelta


class SerpAPIClient:
	def __init__(self, api_key: str) -> None:
		self.api_key = api_key
		self.base_url = "https://serpapi.com/search.json"

	def search_news(self, query: str, since: str, page_size: int = 10) -> List[Dict]:
		"""
		Search Google News via SerpAPI.
		
		Args:
			query: Search query (supports site: operators, Boolean, etc.)
			since: ISO date string (YYYY-MM-DD)
			page_size: Max results (1-100)
		"""
		# Calculate date range for Google News
		# Google News uses relative dates like "7d" (last 7 days)
		try:
			since_dt = datetime.fromisoformat(since)
			today = datetime.now()
			days_ago = (today - since_dt).days
			
			# Google News date filter
			if days_ago <= 1:
				date_filter = "qdr:d"  # Past day
			elif days_ago <= 7:
				date_filter = "qdr:w"  # Past week
			elif days_ago <= 30:
				date_filter = "qdr:m"  # Past month
			elif days_ago <= 365:
				date_filter = "qdr:y"  # Past year
			else:
				date_filter = None  # No filter for older dates
		except:
			date_filter = "qdr:m"  # Default: past month
		
		params = {
			"engine": "google",
			"q": query,
			"tbm": "nws",  # News search
			"api_key": self.api_key,
			"num": min(page_size, 100),
		}
		
		if date_filter:
			params["tbs"] = date_filter
		
		try:
			resp = requests.get(self.base_url, params=params, timeout=30)
			resp.raise_for_status()
			data = resp.json() or {}
		except Exception as e:
			print(f"    SerpAPI error: {e}")
			return []
		
		# Parse results
		news_results = data.get("news_results", [])
		
		normalized: List[Dict] = []
		for article in news_results:
			normalized.append({
				"title": article.get("title"),
				"description": article.get("snippet"),
				"content": article.get("snippet"),
				"url": article.get("link"),
				"source": article.get("source"),
				"publishedAt": article.get("date"),
			})
		
		return normalized


