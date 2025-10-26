#!/usr/bin/env python3
"""
Auto-learning V2: Analyzes ARTICLE CONTENT (not user notes) to find patterns.
Identifies what types of articles are relevant vs not relevant.
"""

import json
import os
import re
from collections import Counter
from typing import List, Set, Tuple
from datetime import datetime


FEEDBACK_FILE = "feedback.jsonl"
FILTERS_FILE = "main_simple.py"
LEARNING_LOG = "learning_log.jsonl"
MIN_OCCURRENCES = 5  # Keyword must appear 5+ times to be significant


def load_feedback_with_articles():
	"""Load feedback with article titles and descriptions."""
	low_relevance_articles = []  # Ratings 1-2
	high_relevance_articles = []  # Ratings 4-5
	
	if not os.path.exists(FEEDBACK_FILE):
		return low_relevance_articles, high_relevance_articles
	
	with open(FEEDBACK_FILE, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				
				# SKIP promotional content - don't use for topic learning
				if entry.get('is_promo', False):
					continue
				
				rating = entry.get('rating')
				
				# Get article content (stored by dashboard)
				title = entry.get('article_title', '')
				summary = entry.get('article_summary', '')
				
				# If no stored content, skip (old feedback format)
				if not title and not summary:
					continue
				
				# Convert rating
				if isinstance(rating, str):
					if rating == 'not_relevant':
						rating = 1
					elif rating == 'relevant':
						rating = 4
				
				# Combine title and summary for analysis
				article_text = (title + ' ' + summary).lower()
				
				item = {
					'title': title,
					'summary': summary,
					'text': article_text,
				}
				
				if isinstance(rating, int):
					if 1 <= rating <= 2:
						low_relevance_articles.append(item)
					elif 4 <= rating <= 5:
						high_relevance_articles.append(item)
			except:
				pass
	
	return low_relevance_articles, high_relevance_articles


def extract_topic_keywords(articles: List[dict]) -> Counter:
	"""Extract keywords from article titles and descriptions."""
	all_keywords = []
	
	for article in articles:
		title = article.get('title', '')
		summary = article.get('summary', '')
		text = (title + ' ' + summary).lower()
		
		# Extract words (4+ chars)
		words = re.findall(r'\b[a-z]{4,}\b', text)
		
		# Comprehensive stop words list
		stop_words = {
			# URL/HTML junk
			'https', 'http', 'www', 'com', 'org', 'gov', 'html', 'aspx', 'href',
			'track', 'admin', 'ajax', 'action', 'nltr', 'rct', 'url', 'usg', 'link',
			# Generic article words
			'article', 'news', 'story', 'read', 'more', 'click', 'view', 'here',
			'about', 'latest', 'update', 'release', 'media', 'press',
			# Common stop words
			'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'has',
			'was', 'were', 'with', 'from', 'that', 'this', 'have', 'been', 'very',
			'will', 'would', 'could', 'should', 'when', 'what', 'where', 'which',
			'their', 'there', 'these', 'those', 'they', 'them', 'then', 'than',
			'your', 'said', 'says', 'also', 'just', 'some', 'such', 'only',
			# Time/date words
			'year', 'years', 'month', 'months', 'week', 'weeks', 'today', 'tomorrow',
			'2024', '2025', 'october', 'september',
			# Already captured in filters
			'australia', 'australian', 'zealand',  # Too generic
		}
		
		# Extract meaningful keywords
		keywords = []
		for word in words:
			if word in stop_words or len(word) < 4:
				continue
			# Skip pure numbers
			if word.isdigit():
				continue
			keywords.append(word)
		
		all_keywords.extend(keywords)
	
	return Counter(all_keywords)


def find_distinctive_keywords(low_articles: List[dict], high_articles: List[dict], 
                               current_excl: Set[str], current_incl: Set[str]) -> Tuple[List[str], List[str]]:
	"""Find keywords that distinguish low vs high relevance articles."""
	
	low_keywords = extract_topic_keywords(low_articles)
	high_keywords = extract_topic_keywords(high_articles)
	
	# Find keywords that appear much more in low-relevance
	new_exclusions = []
	for word, count in low_keywords.most_common(30):
		if count < MIN_OCCURRENCES:
			continue
		if word in current_excl:
			continue
		
		# Calculate ratio: low / (high + 1)
		high_count = high_keywords.get(word, 0)
		ratio = count / (high_count + 1)
		
		# If appears 3x more in low-relevance, it's a false positive
		if ratio >= 3.0:
			new_exclusions.append((word, count, high_count, ratio))
	
	# Find keywords that appear much more in high-relevance
	new_inclusions = []
	for word, count in high_keywords.most_common(30):
		if count < MIN_OCCURRENCES:
			continue
		if word in current_incl:
			continue
		
		# Calculate ratio: high / (low + 1)
		low_count = low_keywords.get(word, 0)
		ratio = count / (low_count + 1)
		
		# If appears 3x more in high-relevance, it's a true positive
		if ratio >= 3.0:
			new_inclusions.append((word, count, low_count, ratio))
	
	# Sort by ratio (strongest patterns first)
	new_exclusions.sort(key=lambda x: x[3], reverse=True)
	new_inclusions.sort(key=lambda x: x[3], reverse=True)
	
	return new_exclusions[:10], new_inclusions[:10]


def read_current_filters(filepath: str) -> Tuple[Set[str], Set[str]]:
	"""Read current keyword lists from main_simple.py."""
	irrelevant = set()
	relevant = set()
	
	with open(filepath, 'r') as f:
		content = f.read()
	
	# Extract irrelevant_keywords list
	irrel_match = re.search(r"irrelevant_keywords\s*=\s*\[(.*?)\]", content, re.DOTALL)
	if irrel_match:
		items = re.findall(r"'([^']+)'", irrel_match.group(1))
		irrelevant = set(items)
	
	# Extract relevant_keywords list
	rel_match = re.search(r"relevant_keywords\s*=\s*\[(.*?)\]", content, re.DOTALL)
	if rel_match:
		items = re.findall(r"'([^']+)'", rel_match.group(1))
		relevant = set(items)
	
	return irrelevant, relevant


def update_filters(filepath: str, new_exclusions: List[Tuple], new_inclusions: List[Tuple]) -> bool:
	"""Update main_simple.py with new keywords."""
	if not new_exclusions and not new_inclusions:
		return False
	
	with open(filepath, 'r') as f:
		content = f.read()
	
	# Add new exclusions
	if new_exclusions:
		keywords_to_add = [item[0] for item in new_exclusions]
		match = re.search(r"(irrelevant_keywords\s*=\s*\[.*?)(\n\t])", content, re.DOTALL)
		if match:
			timestamp = datetime.now().strftime('%Y-%m-%d')
			additions = ',\n\t\t'.join([f"'{kw}'" for kw in keywords_to_add])
			updated = match.group(1) + f",\n\t\t# Auto-learned {timestamp} from article content analysis:\n\t\t{additions}" + match.group(2)
			content = content[:match.start()] + updated + content[match.end():]
	
	# Add new inclusions
	if new_inclusions:
		keywords_to_add = [item[0] for item in new_inclusions]
		match = re.search(r"(relevant_keywords\s*=\s*\[.*?)(\n\t])", content, re.DOTALL)
		if match:
			timestamp = datetime.now().strftime('%Y-%m-%d')
			additions = ',\n\t\t'.join([f"'{kw}'" for kw in keywords_to_add])
			updated = match.group(1) + f",\n\t\t# Auto-learned {timestamp} from article content analysis:\n\t\t{additions}" + match.group(2)
			content = content[:match.start()] + updated + content[match.end():]
	
	# Write back
	with open(filepath, 'w') as f:
		f.write(content)
	
	return True


def log_learning(new_exclusions: List[Tuple], new_inclusions: List[Tuple]):
	"""Log what was learned."""
	entry = {
		'timestamp': datetime.now().isoformat(),
		'new_exclusions': [{'keyword': kw, 'low_count': low, 'high_count': high, 'ratio': ratio} 
		                   for kw, low, high, ratio in new_exclusions],
		'new_inclusions': [{'keyword': kw, 'high_count': high, 'low_count': low, 'ratio': ratio}
		                   for kw, high, low, ratio in new_inclusions],
	}
	
	with open(LEARNING_LOG, 'a') as f:
		f.write(json.dumps(entry) + '\n')


def main():
	print("🧠 Auto-Learning V2: Article Content Analysis")
	print("="*60)
	
	# Load feedback
	print("\n📊 Loading feedback with article content...")
	low_rel, high_rel = load_feedback_with_articles()
	
	if len(low_rel) + len(high_rel) < 20:
		print(f"⚠️  Not enough feedback data ({len(low_rel) + len(high_rel)} ratings)")
		print("   Need at least 20 ratings for learning")
		return
	
	print(f"   Low relevance (1-2): {len(low_rel)} articles")
	print(f"   High relevance (4-5): {len(high_rel)} articles")
	
	# Read current filters
	print("\n🔍 Reading current filters...")
	current_excl, current_incl = read_current_filters(FILTERS_FILE)
	print(f"   Current exclusions: {len(current_excl)} keywords")
	print(f"   Current inclusions: {len(current_incl)} keywords")
	
	# Find distinctive patterns
	print("\n🔎 Analyzing article content patterns...")
	new_excl, new_incl = find_distinctive_keywords(low_rel, high_rel, current_excl, current_incl)
	
	if not new_excl and not new_incl:
		print("   ✅ No new patterns found - filters are up to date!")
		return
	
	print(f"\n💡 New patterns discovered from ARTICLE CONTENT:")
	if new_excl:
		print(f"\n   🔴 Topic patterns appearing in NOT-RELEVANT articles:")
		for word, low_count, high_count, ratio in new_excl[:10]:
			print(f"      - '{word}': {low_count}x in low-rated, {high_count}x in high-rated (ratio: {ratio:.1f}x)")
	
	if new_incl:
		print(f"\n   ✅ Topic patterns appearing in RELEVANT articles:")
		for word, high_count, low_count, ratio in new_incl[:10]:
			print(f"      - '{word}': {high_count}x in high-rated, {low_count}x in low-rated (ratio: {ratio:.1f}x)")
	
	# Show what will be added
	print(f"\n📝 Proposed filter updates:")
	if new_excl:
		excl_words = [item[0] for item in new_excl]
		print(f"   Exclude: {', '.join(excl_words[:5])}...")
	if new_incl:
		incl_words = [item[0] for item in new_incl]
		print(f"   Include: {', '.join(incl_words[:5])}...")
	
	# Confirm
	print(f"\n❓ Apply these changes to filters?")
	confirm = input("   (y/n): ")
	
	if confirm.lower() != 'y':
		print("   ❌ Cancelled")
		return
	
	# Apply updates
	print("\n🔧 Updating filters...")
	success = update_filters(FILTERS_FILE, new_excl, new_incl)
	
	if success:
		print("   ✅ Filters updated!")
		log_learning(new_excl, new_incl)
		print(f"   📝 Logged to {LEARNING_LOG}")
		print(f"\n💡 Next steps:")
		print(f"   1. Run: python main_newsletters.py --since-days 3")
		print(f"   2. Check if relevance improved")
		print(f"   3. Run auto_learn_v2.py weekly to continue learning")
	
	print("\n" + "="*60)


if __name__ == "__main__":
	main()
