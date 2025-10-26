"""
Smart deduplication: Remove duplicate articles by content similarity, not just URL.
Keep the best article for each topic.
"""

from typing import List, Dict
import re
from difflib import SequenceMatcher


def normalize_title(title: str) -> str:
	"""Normalize title for comparison."""
	# Remove tags
	title = re.sub(r'\[(RSS|Legislation|News)\]\s*', '', title)
	# Lowercase
	title = title.lower()
	# Remove punctuation
	title = re.sub(r'[^\w\s]', ' ', title)
	# Remove extra whitespace
	title = ' '.join(title.split())
	return title


def titles_similar(title1: str, title2: str, threshold: float = 0.7) -> bool:
	"""Check if two titles are similar using sequence matching."""
	norm1 = normalize_title(title1)
	norm2 = normalize_title(title2)
	
	# Calculate similarity ratio
	ratio = SequenceMatcher(None, norm1, norm2).ratio()
	
	return ratio >= threshold


def extract_key_terms(title: str, description: str) -> set:
	"""Extract key terms for topic matching."""
	text = (title + " " + description).lower()
	# Remove common words
	text = re.sub(r'\b(the|and|for|are|but|not|with|from|this|that)\b', '', text)
	# Extract words
	words = set(re.findall(r'\b[a-z]{4,}\b', text))  # 4+ char words only
	return words


def topics_similar(article1: Dict, article2: Dict, threshold: int = 3) -> bool:
	"""Check if two articles cover the same topic by comparing key terms."""
	terms1 = extract_key_terms(
		article1.get('title', ''),
		article1.get('summary', '') or article1.get('description', '')
	)
	terms2 = extract_key_terms(
		article2.get('title', ''),
		article2.get('summary', '') or article2.get('description', '')
	)
	
	# Count common terms
	common = terms1.intersection(terms2)
	
	# If 3+ common key terms, it's likely the same topic
	return len(common) >= threshold


def choose_best_article(articles: List[Dict]) -> Dict:
	"""Choose the best article from duplicates."""
	# Preference order:
	# 1. Higher importance score
	# 2. Longer/better summary
	# 3. Better source (AFR, Bloomberg, Reuters > ABC, SMH > Others)
	
	premium_sources = ['australian financial review', 'bloomberg', 'reuters', 'financial times']
	quality_sources = ['abc', 'sydney morning herald', 'the guardian', 'the age']
	
	def score_article(article: Dict) -> float:
		score = article.get('importance_score', 50)
		
		# Boost for better sources
		source = (article.get('source') or '').lower()
		if any(ps in source for ps in premium_sources):
			score += 20
		elif any(qs in source for qs in quality_sources):
			score += 10
		
		# Boost for longer summaries (more detail)
		summary_len = len(article.get('summary', '') or article.get('description', ''))
		score += min(summary_len / 50, 10)  # Up to +10 for long summaries
		
		# Boost for [RSS] or [Legislation] tags (direct from source)
		if article.get('title', '').startswith('['):
			score += 5
		
		return score
	
	return max(articles, key=score_article)


def deduplicate_articles(articles: List[Dict], similarity_threshold: float = 0.7) -> List[Dict]:
	"""
	Remove duplicate articles by content similarity.
	Keeps the best article for each topic.
	"""
	if not articles:
		return []
	
	unique_articles = []
	seen_topics = []
	
	for article in articles:
		# Check if this article is similar to any we've already added
		is_duplicate = False
		
		for i, existing in enumerate(seen_topics):
			# Check title similarity
			if titles_similar(article.get('title', ''), existing.get('title', ''), similarity_threshold):
				is_duplicate = True
				# Replace with better article if current one is better
				if choose_best_article([article, existing]) == article:
					unique_articles[i] = article
					seen_topics[i] = article
				break
			
			# Check topic similarity (same topic, different angle)
			if topics_similar(article, existing):
				is_duplicate = True
				# Keep the better one
				if choose_best_article([article, existing]) == article:
					unique_articles[i] = article
					seen_topics[i] = article
				break
		
		if not is_duplicate:
			unique_articles.append(article)
			seen_topics.append(article)
	
	print(f"    Deduplication: {len(articles)} → {len(unique_articles)} articles (removed {len(articles) - len(unique_articles)} duplicates)")
	
	return unique_articles


