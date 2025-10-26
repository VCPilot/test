"""
Load feedback and filter out articles the user has rated as not relevant.
This prevents showing the same irrelevant articles multiple times.
"""

import json
import os
from typing import Set


FEEDBACK_FILE = "feedback.jsonl"


def normalize_url(url: str) -> str:
	"""Normalize URL by removing tracking parameters."""
	# For Biometric Update tracking links, extract the base article slug
	if 'biometricupdate.com' in url and '/202' in url:
		# Extract the article slug from the encoded URL
		import re
		match = re.search(r'/\d{6}/([^;]+)', url)
		if match:
			return match.group(1)  # Return just the article slug
	return url


def load_not_relevant_urls() -> Set[str]:
	"""Load URLs of articles user rated as 'not_relevant', low ratings (1-2 stars), or already rated."""
	not_relevant = set()
	normalized_urls = set()  # Store normalized versions for better matching
	
	if not os.path.exists(FEEDBACK_FILE):
		return not_relevant
	
	with open(FEEDBACK_FILE, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				rating = entry.get('rating')
				url = entry.get('article_url')
				if not url:
					continue
				
				# Filter out: 'not_relevant', numeric ratings 1-2, or promo-flagged
				if (rating == 'not_relevant' or 
				    rating == 1 or 
				    rating == 2 or 
				    entry.get('is_promo') == True):
					not_relevant.add(url)
					# Also store normalized version for tracking URL variants
					normalized_urls.add(normalize_url(url))
				
				# Also block ANY article that's already been rated (to prevent RSS duplicates)
				# Only if it's from an RSS feed (title starts with [RSS])
				elif rating is not None and entry.get('article_title', '').startswith('[RSS]'):
					not_relevant.add(url)
			except:
				pass
	
	# Store both raw and normalized URLs for checking
	not_relevant.update(normalized_urls)
	return not_relevant


def should_skip_article(url: str) -> bool:
	"""Check if article should be skipped based on user feedback."""
	not_relevant_urls = load_not_relevant_urls()
	return url in not_relevant_urls
