from typing import Dict, List, Optional
import requests
from datetime import datetime


class GNewsClient:
	def __init__(self, api_key: str) -> None:
		self.api_key = api_key
		self.search_url = "https://gnews.io/api/v4/search"
		self.headlines_url = "https://gnews.io/api/v4/top-headlines"

	def search(self, query: str, since: str = None, page_size: int = 10, domains: List[str] = None) -> List[Dict]:
		"""
		Search GNews. Free tier limitations:
		- top-headlines endpoint works best
		- 'from' date parameter not supported on free tier
		- Boolean operators may be limited
		"""
		# Try search endpoint first (may not work on free tier with date)
		params = {
			"q": query,
			"lang": "en",
			"country": "au",
			"max": min(max(1, page_size), 100),
			"apikey": self.api_key,
		}
		
		# Remove date filter - not supported on free tier
		# if since:
		#     params["from"] = f"{since}T00:00:00Z"
		
		try:
			resp = requests.get(self.search_url, params=params, timeout=30)
			resp.raise_for_status()
			data = resp.json() or {}
			
			# Check for errors
			if "errors" in data:
				print(f"    GNews error: {data['errors']}")
				return []
			
			articles = data.get("articles", [])
			
			# If search returned no results, fallback to top-headlines
			if not articles:
				print(f"    Search returned 0 results, trying top-headlines...")
				return self.get_top_headlines(category="business", page_size=page_size)
			
		except requests.exceptions.HTTPError as e:
			print(f"    GNews HTTP error: {e}")
			# Fallback to top-headlines
			return self.get_top_headlines(category="business", page_size=page_size)
		except Exception as e:
			print(f"    GNews error: {e}")
			return []
		
		# Normalize response
		normalized: List[Dict] = []
		for a in articles:
			normalized.append({
				"title": a.get("title"),
				"description": a.get("description"),
				"content": a.get("content"),
				"url": a.get("url"),
				"source": (a.get("source") or {}).get("name"),
				"publishedAt": a.get("publishedAt"),
			})
		return normalized
	
	def get_top_headlines(self, category: str = "business", page_size: int = 10) -> List[Dict]:
		"""Get top headlines from GNews (works well on free tier)."""
		params = {
			"category": category,
			"lang": "en",
			"country": "au",
			"max": min(max(1, page_size), 100),
			"apikey": self.api_key,
		}
		
		try:
			resp = requests.get(self.headlines_url, params=params, timeout=30)
			resp.raise_for_status()
			data = resp.json() or {}
			
			if "errors" in data:
				print(f"    GNews error: {data['errors']}")
				return []
			
			articles = data.get("articles", [])
		except Exception as e:
			print(f"    GNews error: {e}")
			return []
		
		# Normalize
		normalized: List[Dict] = []
		for a in articles:
			normalized.append({
				"title": a.get("title"),
				"description": a.get("description"),
				"content": a.get("content"),
				"url": a.get("url"),
				"source": (a.get("source") or {}).get("name"),
				"publishedAt": a.get("publishedAt"),
			})
		return normalized