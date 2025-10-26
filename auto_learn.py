#!/usr/bin/env python3
"""
Auto-learning system: Analyzes feedback and updates filters automatically.
Run weekly to improve relevance based on your ratings and notes.
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
MIN_OCCURRENCES = 3  # Keyword must appear 3+ times to be added


def load_feedback_by_rating():
	"""Load feedback grouped by rating level."""
	low_relevance = []  # Ratings 1-2
	high_relevance = []  # Ratings 4-5
	
	if not os.path.exists(FEEDBACK_FILE):
		return low_relevance, high_relevance
	
	with open(FEEDBACK_FILE, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				rating = entry.get('rating')
				
				# Handle different rating formats
				if isinstance(rating, str):
					if rating == 'not_relevant':
						rating = 1
					elif rating == 'relevant':
						rating = 4
				
				if isinstance(rating, int):
					if 1 <= rating <= 2:
						low_relevance.append(entry)
					elif 4 <= rating <= 5:
						high_relevance.append(entry)
			except:
				pass
	
	return low_relevance, high_relevance


def extract_keywords_from_notes(entries: List[dict]) -> List[str]:
	"""Extract meaningful keywords from user notes ONLY (not URLs)."""
	all_text = []
	for entry in entries:
		notes = entry.get('notes', '').lower()
		# Only use notes, NOT URLs
		if notes and len(notes) > 5:  # Skip empty or very short notes
			all_text.append(notes)
	
	# Combine all text
	combined = ' '.join(all_text)
	
	# Extract words (3+ chars)
	words = re.findall(r'\b[a-z]{3,}\b', combined)
	
	# Stop words and URL fragments to ignore
	stop_words = {
		'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
		'was', 'with', 'from', 'that', 'this', 'have', 'been', 'very',
		'rating', 'relevance', 'relevant', 'irrelevant',  # Meta words
		'https', 'http', 'www', 'com', 'org', 'gov', 'url', 'link',  # URL fragments
		'article', 'news', 'read', 'more',  # Generic article words
	}
	
	words = [w for w in words if w not in stop_words and len(w) >= 4]  # 4+ chars only
	
	return words


def find_new_exclusion_keywords(low_relevance: List[dict], current_exclusions: Set[str]) -> List[str]:
	"""Find new keywords that appear frequently in not-relevant articles."""
	keywords = extract_keywords_from_notes(low_relevance)
	freq = Counter(keywords)
	
	new_keywords = []
	for word, count in freq.most_common(20):
		if count >= MIN_OCCURRENCES and word not in current_exclusions:
			new_keywords.append(word)
	
	return new_keywords


def find_new_inclusion_keywords(high_relevance: List[dict], current_inclusions: Set[str]) -> List[str]:
	"""Find new keywords that appear frequently in relevant articles."""
	keywords = extract_keywords_from_notes(high_relevance)
	freq = Counter(keywords)
	
	new_keywords = []
	for word, count in freq.most_common(20):
		if count >= MIN_OCCURRENCES and word not in current_inclusions:
			new_keywords.append(word)
	
	return new_keywords


def read_current_filters(filepath: str) -> Tuple[Set[str], Set[str]]:
	"""Read current irrelevant and relevant keyword lists from main_simple.py."""
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


def update_filters(filepath: str, new_exclusions: List[str], new_inclusions: List[str]) -> bool:
	"""Update main_simple.py with new keywords."""
	if not new_exclusions and not new_inclusions:
		return False
	
	with open(filepath, 'r') as f:
		content = f.read()
	
	# Add new exclusions
	if new_exclusions:
		# Find the irrelevant_keywords list
		match = re.search(r"(irrelevant_keywords\s*=\s*\[.*?)(\n\t])", content, re.DOTALL)
		if match:
			additions = ',\n\t\t'.join([f"'{kw}'" for kw in new_exclusions])
			updated = match.group(1) + f",\n\t\t# Auto-learned from feedback:\n\t\t{additions}" + match.group(2)
			content = content[:match.start()] + updated + content[match.end():]
	
	# Add new inclusions
	if new_inclusions:
		# Find the relevant_keywords list  
		match = re.search(r"(relevant_keywords\s*=\s*\[.*?)(\n\t])", content, re.DOTALL)
		if match:
			additions = ',\n\t\t'.join([f"'{kw}'" for kw in new_inclusions])
			updated = match.group(1) + f",\n\t\t# Auto-learned from feedback:\n\t\t{additions}" + match.group(2)
			content = content[:match.start()] + updated + content[match.end():]
	
	# Write back
	with open(filepath, 'w') as f:
		f.write(content)
	
	return True


def log_learning(new_exclusions: List[str], new_inclusions: List[str]):
	"""Log what was learned for audit trail."""
	entry = {
		'timestamp': datetime.now().isoformat(),
		'new_exclusions': new_exclusions,
		'new_inclusions': new_inclusions,
	}
	
	with open(LEARNING_LOG, 'a') as f:
		f.write(json.dumps(entry) + '\n')


def main():
	print("🧠 Auto-Learning System")
	print("="*60)
	
	# Load feedback
	print("\n📊 Loading feedback...")
	low_rel, high_rel = load_feedback_by_rating()
	
	if len(low_rel) + len(high_rel) < 20:
		print(f"⚠️  Not enough feedback data ({len(low_rel) + len(high_rel)} ratings)")
		print("   Need at least 20 ratings for learning")
		print("   Continue rating articles and run again later")
		return
	
	print(f"   Low relevance (1-2): {len(low_rel)}")
	print(f"   High relevance (4-5): {len(high_rel)}")
	
	# Read current filters
	print("\n🔍 Analyzing current filters...")
	current_excl, current_incl = read_current_filters(FILTERS_FILE)
	print(f"   Current exclusions: {len(current_excl)} keywords")
	print(f"   Current inclusions: {len(current_incl)} keywords")
	
	# Find new keywords
	print("\n🔎 Discovering new patterns from your feedback...")
	new_excl = find_new_exclusion_keywords(low_rel, current_excl)
	new_incl = find_new_inclusion_keywords(high_rel, current_incl)
	
	if not new_excl and not new_incl:
		print("   ✅ No new patterns found - filters are up to date!")
		return
	
	print(f"\n💡 New patterns discovered:")
	if new_excl:
		print(f"   🔴 Exclusions to add ({len(new_excl)}):")
		for kw in new_excl[:10]:
			print(f"      - '{kw}'")
	if new_incl:
		print(f"   ✅ Inclusions to add ({len(new_incl)}):")
		for kw in new_incl[:10]:
			print(f"      - '{kw}'")
	
	# Confirm update
	print(f"\n📝 Ready to update filters automatically?")
	confirm = input("   Apply these changes? (y/n): ")
	
	if confirm.lower() != 'y':
		print("   ❌ Cancelled - no changes made")
		return
	
	# Update filters
	print("\n🔧 Updating filters...")
	success = update_filters(FILTERS_FILE, new_excl, new_incl)
	
	if success:
		print("   ✅ Filters updated successfully!")
		log_learning(new_excl, new_incl)
		print(f"   📝 Changes logged to {LEARNING_LOG}")
		print(f"\n💡 Next steps:")
		print(f"   1. Run: python main_newsletters.py --since-days 3")
		print(f"   2. Check if relevance improved")
		print(f"   3. Continue rating articles")
		print(f"   4. Run auto_learn.py again next week")
	else:
		print("   ⚠️  No changes made")
	
	print("\n" + "="*60)


if __name__ == "__main__":
	main()
