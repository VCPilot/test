#!/usr/bin/env python3
"""
Analyze feedback.jsonl to identify patterns and generate query improvement recommendations.

Minimum thresholds:
- 20 ratings total (10 relevant + 10 not relevant) for basic analysis
- 50 ratings for reliable patterns
- 100+ ratings for high confidence recommendations
"""

import json
import os
from collections import Counter
from typing import Dict, List, Tuple
import re


# Minimum thresholds
MIN_RATINGS_BASIC = 20
MIN_RATINGS_RELIABLE = 50
MIN_RATINGS_CONFIDENT = 100

# Word frequency thresholds
MIN_WORD_FREQUENCY = 3  # Word must appear at least 3 times to be significant


def load_feedback(filepath: str = "feedback.jsonl") -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict], List[Dict]]:
	"""Load and categorize feedback by 1-5 rating scale."""
	rating_1 = []  # Not relevant
	rating_2 = []  # Slightly relevant
	rating_3 = []  # Moderately relevant
	rating_4 = []  # Very relevant
	rating_5 = []  # Highly relevant
	
	if not os.path.exists(filepath):
		return rating_1, rating_2, rating_3, rating_4, rating_5
	
	with open(filepath, 'r') as f:
		for line in f:
			try:
				entry = json.loads(line)
				rating = entry.get('rating', '')
				
				# Handle new 1-5 scale
				if rating == 1:
					rating_1.append(entry)
				elif rating == 2:
					rating_2.append(entry)
				elif rating == 3:
					rating_3.append(entry)
				elif rating == 4:
					rating_4.append(entry)
				elif rating == 5:
					rating_5.append(entry)
				# Handle legacy binary ratings
				elif rating == 'not_relevant':
					rating_1.append(entry)
				elif rating == 'relevant':
					rating_4.append(entry)  # Treat legacy "relevant" as "very relevant"
			except:
				pass
	
	return rating_1, rating_2, rating_3, rating_4, rating_5


def extract_keywords(text: str) -> List[str]:
	"""Extract meaningful keywords from text."""
	# Convert to lowercase
	text = text.lower()
	
	# Remove URLs
	text = re.sub(r'http\S+', '', text)
	
	# Extract words (2+ chars)
	words = re.findall(r'\b[a-z]{2,}\b', text)
	
	# Common stop words to ignore
	stop_words = {
		'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one',
		'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old',
		'see', 'two', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use',
		'via', 'with', 'from', 'that', 'this', 'have', 'will', 'your', 'more', 'been',
		'some', 'than', 'into', 'very', 'when', 'which', 'their', 'would', 'about', 'after',
		'could', 'other', 'there', 'these', 'what', 'only', 'also', 'back', 'good', 'just',
		'most', 'over', 'such', 'take', 'them', 'then', 'well', 'where', 'year'
	}
	
	# Filter out stop words and short words
	keywords = [w for w in words if w not in stop_words and len(w) > 2]
	
	return keywords


def extract_phrases(text: str) -> List[str]:
	"""Extract 2-3 word phrases."""
	text = text.lower()
	words = re.findall(r'\b[a-z]+\b', text)
	
	phrases = []
	# 2-word phrases
	for i in range(len(words) - 1):
		phrase = f"{words[i]} {words[i+1]}"
		phrases.append(phrase)
	
	# 3-word phrases
	for i in range(len(words) - 2):
		phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
		phrases.append(phrase)
	
	return phrases


def analyze_patterns(rating_1: List[Dict], rating_2: List[Dict], rating_3: List[Dict], rating_4: List[Dict], rating_5: List[Dict]) -> Dict:
	"""Analyze keyword patterns across 1-5 rating scale."""
	
	# Group ratings: Low relevance (1-2) vs High relevance (4-5)
	low_relevance = rating_1 + rating_2  # Not relevant + Slightly relevant
	high_relevance = rating_4 + rating_5  # Very relevant + Highly relevant
	moderate_relevance = rating_3  # Moderately relevant
	
	# Extract text from each group
	def extract_text_from_ratings(ratings):
		texts = []
		for item in ratings:
			url = item.get('article_url', '')
			notes = item.get('notes', '')
			texts.append(url + ' ' + notes)
		return texts
	
	low_text = extract_text_from_ratings(low_relevance)
	high_text = extract_text_from_ratings(high_relevance)
	moderate_text = extract_text_from_ratings(moderate_relevance)
	
	# Extract keywords
	def extract_keywords_from_texts(texts):
		all_keywords = []
		for text in texts:
			all_keywords.extend(extract_keywords(text))
		return all_keywords
	
	low_keywords = extract_keywords_from_texts(low_text)
	high_keywords = extract_keywords_from_texts(high_text)
	moderate_keywords = extract_keywords_from_texts(moderate_text)
	
	# Count frequencies
	low_freq = Counter(low_keywords)
	high_freq = Counter(high_keywords)
	moderate_freq = Counter(moderate_keywords)
	
	# Find false positive signals (appear more in low-relevance ratings)
	false_positives = {}
	for word, count in low_freq.most_common(30):
		if count >= MIN_WORD_FREQUENCY:
			high_count = high_freq.get(word, 0)
			ratio = count / (high_count + 1)
			
			# If word appears much more in low-relevance (ratio > 2), it's a false positive
			if ratio > 2:
				false_positives[word] = {
					'low_count': count,
					'high_count': high_count,
					'ratio': ratio
				}
	
	# Find true positive signals (appear more in high-relevance ratings)
	true_positives = {}
	for word, count in high_freq.most_common(30):
		if count >= MIN_WORD_FREQUENCY:
			low_count = low_freq.get(word, 0)
			ratio = count / (low_count + 1)
			
			# If word appears much more in high-relevance (ratio > 2), it's a true positive
			if ratio > 2:
				true_positives[word] = {
					'high_count': count,
					'low_count': low_count,
					'ratio': ratio
				}
	
	# Find moderate signals (appear mainly in rating 3)
	moderate_signals = {}
	for word, count in moderate_freq.most_common(20):
		if count >= MIN_WORD_FREQUENCY:
			total_other = low_freq.get(word, 0) + high_freq.get(word, 0)
			if count > total_other:
				moderate_signals[word] = {
					'moderate_count': count,
					'other_count': total_other
				}
	
	return {
		'false_positives': false_positives,
		'true_positives': true_positives,
		'moderate_signals': moderate_signals,
		'rating_counts': {
			'rating_1': len(rating_1),
			'rating_2': len(rating_2),
			'rating_3': len(rating_3),
			'rating_4': len(rating_4),
			'rating_5': len(rating_5)
		},
		'low_relevance_total': len(low_relevance),
		'high_relevance_total': len(high_relevance),
		'moderate_relevance_total': len(moderate_relevance)
	}


def generate_recommendations(analysis: Dict) -> List[str]:
	"""Generate actionable recommendations."""
	recommendations = []
	
	false_positives = analysis['false_positives']
	true_positives = analysis['true_positives']
	
	# Negative keywords to exclude
	if false_positives:
		top_false = sorted(false_positives.items(), key=lambda x: x[1]['ratio'], reverse=True)[:10]
		if top_false:
			neg_keywords = [word for word, _ in top_false]
			recommendations.append({
				'type': 'EXCLUDE',
				'action': f"Add to queries: NOT ({' OR '.join(neg_keywords)})",
				'impact': 'Filters out common false positives',
				'keywords': neg_keywords
			})
	
	# Positive keywords to boost
	if true_positives:
		top_true = sorted(true_positives.items(), key=lambda x: x[1]['ratio'], reverse=True)[:10]
		if top_true:
			pos_keywords = [word for word, _ in top_true]
			recommendations.append({
				'type': 'BOOST',
				'action': f"Consider adding to queries: {' OR '.join(pos_keywords)}",
				'impact': 'Captures more relevant articles',
				'keywords': pos_keywords
			})
	
	# Importance score adjustments
	if true_positives:
		recommendations.append({
			'type': 'SCORE_BOOST',
			'action': 'Boost importance score by +10-15 for articles containing high-value keywords',
			'impact': 'Prioritizes relevant articles in reports',
			'keywords': [word for word, _ in sorted(true_positives.items(), key=lambda x: x[1]['ratio'], reverse=True)[:5]]
		})
	
	return recommendations


def print_report(rating_1: List[Dict], rating_2: List[Dict], rating_3: List[Dict], rating_4: List[Dict], rating_5: List[Dict], analysis: Dict, recommendations: List[Dict]):
	"""Print formatted analysis report."""
	total = len(rating_1) + len(rating_2) + len(rating_3) + len(rating_4) + len(rating_5)
	
	print("\n" + "="*80)
	print("📊 FEEDBACK ANALYSIS REPORT (1-5 Scale)")
	print("="*80 + "\n")
	
	# Summary stats
	print("📈 RATING DISTRIBUTION")
	print(f"  Total rated: {total} articles")
	print(f"  ❌ Rating 1 (Not Relevant): {len(rating_1)} ({len(rating_1)/total*100 if total > 0 else 0:.0f}%)")
	print(f"  📝 Rating 2 (Slightly Relevant): {len(rating_2)} ({len(rating_2)/total*100 if total > 0 else 0:.0f}%)")
	print(f"  📋 Rating 3 (Moderately Relevant): {len(rating_3)} ({len(rating_3)/total*100 if total > 0 else 0:.0f}%)")
	print(f"  ⚡ Rating 4 (Very Relevant): {len(rating_4)} ({len(rating_4)/total*100 if total > 0 else 0:.0f}%)")
	print(f"  🔥 Rating 5 (Highly Relevant): {len(rating_5)} ({len(rating_5)/total*100 if total > 0 else 0:.0f}%)")
	
	# Grouped stats
	low_relevance = len(rating_1) + len(rating_2)
	high_relevance = len(rating_4) + len(rating_5)
	print(f"\n📊 GROUPED ANALYSIS")
	print(f"  Low Relevance (1-2): {low_relevance} ({low_relevance/total*100 if total > 0 else 0:.0f}%)")
	print(f"  Moderate Relevance (3): {len(rating_3)} ({len(rating_3)/total*100 if total > 0 else 0:.0f}%)")
	print(f"  High Relevance (4-5): {high_relevance} ({high_relevance/total*100 if total > 0 else 0:.0f}%)")
	
	# Data sufficiency check
	print(f"\n📊 DATA SUFFICIENCY")
	if total < MIN_RATINGS_BASIC:
		print(f"  ⚠️  INSUFFICIENT DATA ({total}/{MIN_RATINGS_BASIC} minimum)")
		print(f"  Need {MIN_RATINGS_BASIC - total} more ratings for basic analysis")
		print(f"  Status: 🔴 Not ready for recommendations")
	elif total < MIN_RATINGS_RELIABLE:
		print(f"  ⚠️  BASIC DATA ({total}/{MIN_RATINGS_RELIABLE} for reliable patterns)")
		print(f"  Recommendations available but may not be fully reliable")
		print(f"  Status: 🟡 Basic recommendations available")
		print(f"  Tip: Add {MIN_RATINGS_RELIABLE - total} more ratings for better confidence")
	elif total < MIN_RATINGS_CONFIDENT:
		print(f"  ✅ RELIABLE DATA ({total}/{MIN_RATINGS_CONFIDENT} for high confidence)")
		print(f"  Status: 🟢 Reliable recommendations available")
		print(f"  Tip: Add {MIN_RATINGS_CONFIDENT - total} more ratings for highest confidence")
	else:
		print(f"  ✅ HIGH CONFIDENCE DATA ({total} ratings)")
		print(f"  Status: 🟢 High confidence recommendations")
	
	# False positives
	if analysis['false_positives']:
		print(f"\n🔴 FALSE POSITIVE SIGNALS (appearing in low-relevance ratings 1-2)")
		for word, data in sorted(analysis['false_positives'].items(), key=lambda x: x[1]['ratio'], reverse=True)[:10]:
			print(f"  - '{word}': appeared {data['low_count']}x in low-relevance, {data['high_count']}x in high-relevance (ratio: {data['ratio']:.1f}x)")
	
	# True positives
	if analysis['true_positives']:
		print(f"\n✅ TRUE POSITIVE SIGNALS (appearing in high-relevance ratings 4-5)")
		for word, data in sorted(analysis['true_positives'].items(), key=lambda x: x[1]['ratio'], reverse=True)[:10]:
			print(f"  - '{word}': appeared {data['high_count']}x in high-relevance, {data['low_count']}x in low-relevance (ratio: {data['ratio']:.1f}x)")
	
	# Moderate signals
	if analysis.get('moderate_signals'):
		print(f"\n📋 MODERATE SIGNALS (appearing mainly in rating 3)")
		for word, data in sorted(analysis['moderate_signals'].items(), key=lambda x: x[1]['moderate_count'], reverse=True)[:5]:
			print(f"  - '{word}': appeared {data['moderate_count']}x in moderate, {data['other_count']}x in other ratings")
	
	# Recommendations
	if recommendations and total >= MIN_RATINGS_BASIC:
		print(f"\n💡 RECOMMENDATIONS")
		for i, rec in enumerate(recommendations, 1):
			print(f"\n{i}. {rec['type']} - {rec['impact']}")
			print(f"   Action: {rec['action']}")
			if rec.get('keywords'):
				print(f"   Keywords: {', '.join(rec['keywords'][:5])}")
	elif total < MIN_RATINGS_BASIC:
		print(f"\n💡 RECOMMENDATIONS")
		print(f"  ⏳ Not enough data yet. Please rate at least {MIN_RATINGS_BASIC} articles.")
		print(f"  Current: {total}/{MIN_RATINGS_BASIC}")
		print(f"\n  How to get more ratings:")
		print(f"  1. Run: python main.py --since 2024-12-01 --max-per-category 3")
		print(f"  2. Open: streamlit run dashboard.py")
		print(f"  3. Rate articles with 👍/👎 buttons")
	
	print("\n" + "="*80)
	print("📝 Next Steps:")
	if total < MIN_RATINGS_BASIC:
		print(f"  1. Rate {MIN_RATINGS_BASIC - total} more articles")
		print(f"  2. Run this script again: python analyze_feedback.py")
	elif total < MIN_RATINGS_RELIABLE:
		print(f"  1. Review recommendations above")
		print(f"  2. Update src/categories.py with negative keywords")
		print(f"  3. Rate {MIN_RATINGS_RELIABLE - total} more articles for better confidence")
		print(f"  4. Re-run analysis after more ratings")
	else:
		print(f"  1. Apply recommendations to src/categories.py")
		print(f"  2. Run agent again and test improvements")
		print(f"  3. Continue rating new articles")
		print(f"  4. Re-analyze weekly to refine further")
	print("="*80 + "\n")


def main():
	print("Loading feedback data...")
	rating_1, rating_2, rating_3, rating_4, rating_5 = load_feedback()
	
	total = len(rating_1) + len(rating_2) + len(rating_3) + len(rating_4) + len(rating_5)
	
	if total == 0:
		print("\n❌ No feedback data found!")
		print("\nTo generate feedback:")
		print("  1. Run: python main_newsletters.py --since-days 3")
		print("  2. Open: streamlit run dashboard.py")
		print("  3. Rate articles with 1-5 scale buttons")
		print("  4. Run: python analyze_feedback.py")
		return
	
	print(f"Found {total} ratings:")
	print(f"  ❌ 1: {len(rating_1)}, 📝 2: {len(rating_2)}, 📋 3: {len(rating_3)}, ⚡ 4: {len(rating_4)}, 🔥 5: {len(rating_5)}")
	
	# Analyze patterns
	print("Analyzing patterns...")
	analysis = analyze_patterns(rating_1, rating_2, rating_3, rating_4, rating_5)
	
	# Generate recommendations
	print("Generating recommendations...")
	recommendations = generate_recommendations(analysis)
	
	# Print report
	print_report(rating_1, rating_2, rating_3, rating_4, rating_5, analysis, recommendations)


if __name__ == "__main__":
	main()


