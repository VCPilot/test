from typing import Dict, List
import requests
from datetime import datetime


class NewsClient:
	def __init__(self, api_key: str) -> None:
		self.api_key = api_key
		self.base_url = "https://newsapi.org/v2/everything"

	def search(self, query: str, since: str, page_size: int = 10) -> List[Dict]:
		# Try everything endpoint first, fallback to top-headlines
		params = {
			"q": query,
			"from": since,
			"sortBy": "publishedAt",
			"language": "en",
			"pageSize": max(1, min(page_size, 100)),
		}
		headers = {"X-Api-Key": self.api_key}
		try:
			resp = requests.get(self.base_url, params=params, headers=headers, timeout=30)
			resp.raise_for_status()
		except requests.exceptions.HTTPError as e:
			if e.response.status_code == 426:  # Upgrade Required
				print(f"    Everything endpoint not available, trying top-headlines...")
				# Fallback to top-headlines endpoint
				top_headlines_url = "https://newsapi.org/v2/top-headlines"
				params = {
					"q": "Australia",  # Very simple query for testing
					"pageSize": max(1, min(page_size, 100)),
				}
				resp = requests.get(top_headlines_url, params=params, headers=headers, timeout=30)
				resp.raise_for_status()
			else:
				raise
		
		data = resp.json() or {}
		articles = data.get("articles", [])
		normalized: List[Dict] = []
		for a in articles:
			normalized.append(
				{
					"title": a.get("title"),
					"description": a.get("description"),
					"content": a.get("content"),
					"url": a.get("url"),
					"source": (a.get("source") or {}).get("name"),
					"publishedAt": a.get("publishedAt"),
				}
			)
		return normalized
