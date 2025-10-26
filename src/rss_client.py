from typing import Dict, List, Set, Optional
from datetime import datetime, timezone
from dateutil import parser as dateparser
import feedparser


class RSSClient:
	def __init__(self, feeds: List[str]) -> None:
		self.feeds = feeds

	def _parse_date(self, entry) -> Optional[datetime]:
		# Try multiple fields commonly present in RSS/Atom
		for key in ("published", "updated", "created", "pubDate"):
			value = entry.get(key)
			if value:
				try:
					dt = dateparser.parse(value)
					if not dt.tzinfo:
						dt = dt.replace(tzinfo=timezone.utc)
					return dt
				except Exception:
					continue
		return None

	def fetch_since(self, since_iso_date: str, max_items_per_feed: int = 100) -> List[Dict]:
		"""Fetch and normalize entries newer than since_iso_date across all feeds."""
		since_dt = dateparser.parse(since_iso_date)
		if not since_dt.tzinfo:
			since_dt = since_dt.replace(tzinfo=timezone.utc)

		seen: Set[str] = set()
		results: List[Dict] = []
		for i, url in enumerate(self.feeds):
			print(f"    Fetching RSS feed {i+1}/{len(self.feeds)}: {url}")
			try:
				# Add timeout to prevent hanging
				import socket
				socket.setdefaulttimeout(10)
				parsed = feedparser.parse(url)
				print(f"    Found {len(parsed.entries)} entries in feed")
			except Exception as e:
				print(f"    Error fetching {url}: {e}")
				continue
			for entry in parsed.entries[:max_items_per_feed]:
				link = entry.get("link") or entry.get("id") or entry.get("guid")
				if not link or link in seen:
					continue
				pub_dt = self._parse_date(entry)
				if pub_dt and pub_dt <= since_dt:
					continue

				seen.add(link)
				normalized = {
					"title": entry.get("title"),
					"description": entry.get("summary") or entry.get("description"),
					"content": entry.get("summary") or entry.get("description"),
					"url": link,
					"source": parsed.feed.get("title") if parsed and parsed.get("feed") else None,
					"publishedAt": pub_dt.isoformat() if pub_dt else None,
					"_source_type": "RSS",
				}
				results.append(normalized)

		return results
