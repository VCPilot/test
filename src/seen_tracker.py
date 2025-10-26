"""
Track articles that have already been reported to avoid duplicates across runs.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Set


SEEN_FILE = "seen_articles.jsonl"


def load_seen_urls(days_to_keep: int = 30) -> Set[str]:
	"""Load URLs of articles we've already reported in the last N days."""
	if not os.path.exists(SEEN_FILE):
		return set()
	
	cutoff_date = datetime.now() - timedelta(days=days_to_keep)
	seen = set()
	
	with open(SEEN_FILE, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				url = entry.get('url')
				timestamp = entry.get('timestamp')
				
				# Only keep recent entries
				if url and timestamp:
					entry_date = datetime.fromisoformat(timestamp)
					if entry_date >= cutoff_date:
						seen.add(url)
			except:
				pass
	
	return seen


def mark_as_seen(urls: list):
	"""Mark URLs as seen by appending to the tracking file."""
	timestamp = datetime.now().isoformat()
	
	with open(SEEN_FILE, 'a') as f:
		for url in urls:
			entry = {
				'url': url,
				'timestamp': timestamp
			}
			f.write(json.dumps(entry) + '\n')


def cleanup_old_entries(days_to_keep: int = 30):
	"""Remove entries older than N days to keep the file manageable."""
	if not os.path.exists(SEEN_FILE):
		return
	
	cutoff_date = datetime.now() - timedelta(days=days_to_keep)
	kept_entries = []
	
	with open(SEEN_FILE, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				timestamp = entry.get('timestamp')
				if timestamp:
					entry_date = datetime.fromisoformat(timestamp)
					if entry_date >= cutoff_date:
						kept_entries.append(line)
			except:
				pass
	
	# Rewrite file with only recent entries
	with open(SEEN_FILE, 'w') as f:
		for entry in kept_entries:
			f.write(entry)

