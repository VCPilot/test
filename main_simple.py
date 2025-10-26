#!/usr/bin/env python3
"""
Simplified version: Just collect RSS + GNews articles without GPT processing.
Fast collection, manual review in dashboard.
"""

import argparse
from src.config import Settings, ensure_output_dir
from src.categories import CATEGORIES
from src.gnews_client import GNewsClient
from src.rss_client import RSSClient
from src.rss_feeds import RSS_FEEDS
from src.report import ReportBuilder
from src.deduplication import deduplicate_articles


AU_GOV_DOMAINS = [
	"asic.gov.au", "accc.gov.au", "oaic.gov.au", "austrac.gov.au",
	"apra.gov.au", "rba.gov.au", "treasury.gov.au",
]


def parse_args():
	parser = argparse.ArgumentParser(description="AI Market Intelligence — Simple Collection Mode")
	parser.add_argument("--since", required=True, help="Start date (YYYY-MM-DD)")
	parser.add_argument("--max-per-category", type=int, default=10, help="Max articles per category")
	return parser.parse_args()


def is_relevant(title: str, description: str) -> bool:
	"""Filter out clearly irrelevant articles."""
	text = (title + " " + description).lower()
	
	# Irrelevant topics (noise) - Updated based on user feedback
	irrelevant_keywords = [
		'sunscreen', 'spf', 'beauty', 'cosmetics',
		'airline', 'flight', 'travel',
		'iron ore', 'mining', 'bhp', 'lithium',
		'health target', 'hospital', 'physiotherapist', 'nurse', 'medical',
		'sport', 'rugby', 'cricket', 'athlete',
		'fishing', 'orange roughy', 'blue cod',
		'conservation', 'biodiversity', 'wilding',
		'chatham islands', 'ship',
		'homeschool', 'education',
		'housing supply', 'housing crisis',
		# Added from user feedback analysis - promotional/event content:
		'webinar', 'promo', 'promotion', 'promotional',
		'register now', 'join us', 'rsvp', 'event invitation',
		'congress', 'conference', 'forum', 'summit', 'symposium',
		'side events', 'networking event', 'panel discussion',
		'whitepaper', 'white paper', 'download now', 'free report',
		'podcast', 'bu podcast', 'enroll', 'enrollment', 'last day',
		'deadline to register', 'market overview', 'industry overview',
		'free guide', 'ebook', 'e-book', 'report download',
		# Generic consumer tech (not financial services related):
		'i tested', 'i tried', 'roku', 'sora 2', 'linux distro', 'ai video',
		'streaming', 'tv streaming', 'zdnet', 'consumer tech', 'gadget',
		# Geopolitical (not ANZ/financial specific):
		'robert fico', 'slovakia', 'vetoes eu sanctions', 'russia sanctions',
		'slovak pm', 'would-be assassin', '21-year sentence', 'shooting slovak',
		# Auto-learned keywords disabled until learning algorithm is fixed
		# (Previous auto-learning incorrectly blocked core relevant terms like 'banking', 'identity', 'australia')
	]
	
	if any(keyword in text for keyword in irrelevant_keywords):
		return False
	
	# Relevant topics (signal) - Based on original brief
	relevant_keywords = [
		# Regulators and compliance
		'asic', 'apra', 'accc', 'oaic', 'austrac', 'rbnz', 'fma', 'mbie',
		'regulation', 'regulatory', 'compliance', 'enforcement', 'legislation',
		'financial stability', 'monetary policy', 'reserve bank', 'central bank',
		
		# Financial services & Credit
		'credit', 'lending', 'loan', 'debt', 'mortgage', 'borrower',
		'bank', 'banking', 'financial services', 'credit union',
		
		# Competitors (from original brief)
		'illion', 'experian', 'equifax', 'fico', 'gbg', 'creditor watch', 'centrix',
		'bureau van dijk', 'dye & durham', 'dye and durham',
		'credit bureau', 'credit reporting agency',
		
		# Credit & Risk (key topics from brief)
		'credit reporting', 'credit score', 'credit bureau', 'credit check',
		'risk management', 'risk assessment', 'credit risk',
		'fraud prevention', 'fraud detection', 'anti-fraud',
		'identity verification', 'identity check', 'digital identity',
		'kyc', 'know your customer',
		
		# Data & Analytics (from brief)
		'data analytics', 'data analysis', 'big data',
		'data breach', 'privacy', 'data protection', 'gdpr', 'personal information',
		'data sharing', 'data governance',
		
		# Technology & Emerging (from brief)
		'open banking', 'cdr', 'consumer data right',
		'fintech', 'regtech', 'ai', 'artificial intelligence', 'machine learning',
		'blockchain', 'biometric', 'facial recognition',
		
		# AML/CTF (mentioned in brief)
		'aml', 'anti-money laundering', 'ctf', 'counter-terrorism financing',
		'sanctions', 'financial crime', 'money laundering',
		
		# Market activity
		'acquisition', 'merger', 'm&a', 'takeover', 'ipo', 'funding', 'investment',
		'partnership', 'collaboration', 'venture capital',
		
		# Consumer insights
		'consumer behavior', 'consumer behaviour', 'consumer trend',
		'affordability', 'cost of living', 'household finances',
		
		# Technology platforms
		'api', 'platform', 'software', 'saas', 'cloud',
		'integration', 'automation',
	]
	
	if any(keyword in text for keyword in relevant_keywords):
		return True
	
	# Default: not relevant
	return False


def classify_by_keywords(title: str, description: str) -> str:
	"""Simple keyword-based classification."""
	text = (title + " " + description).lower()
	
	# Check each category
	if any(word in text for word in ['illion', 'experian', 'equifax', 'fico', 'gbg', 'creditor', 'centrix', 'competitor', 'acquisition', 'merger', 'credit bureau', 'credit reporting']):
		return "Competition"
	
	if any(word in text for word in ['regulation', 'regulatory', 'compliance', 'law', 'legislation', 'privacy', 'apra', 'asic', 'oaic', 'enforcement', 'data protection', 'aml', 'austrac']):
		return "Regulation"
	
	if any(word in text for word in ['ai', 'artificial intelligence', 'blockchain', 'digital identity', 'open banking', 'fintech', 'technology', 'cdr', 'consumer data right']):
		return "Disruptive Trends and Technological Advancements"
	
	if any(word in text for word in ['consumer', 'customer', 'household', 'spending', 'sentiment', 'behavior', 'behaviour', 'borrower', 'affordability']):
		return "Consumer Behaviour and Insights"
	
	if any(word in text for word in ['market', 'industry', 'trend', 'growth', 'forecast', 'ipo', 'funding', 'investment']):
		return "Market Trends"
	
	# Default
	return "Regulation"


def is_corporate_pr(title: str, description: str, url: str) -> bool:
	"""Detect corporate PR/product announcements (low news value)."""
	text = (title + " " + description).lower()
	
	# Corporate PR patterns
	pr_patterns = [
		'launches', 'unveils', 'announces', 'introduces', 'releases',
		'adds', 'upgrades', 'secures funding', 'wins', 'reaches',
		'offers', 'provides', 'delivers', 'expands', 'partners with',
		'integrates', 'deploys', 'implements', 'rolls out'
	]
	
	# If from Biometric Update and contains PR language, it's likely corporate PR
	if 'biometricupdate.com' in url and any(pattern in text for pattern in pr_patterns):
		# Exception: If it mentions ANZ-specific locations/regulators, keep it
		anz_keywords = ['australia', 'new zealand', 'australian', 'apra', 'asic', 'rbnz']
		if any(kw in text for kw in anz_keywords):
			return False  # Keep ANZ-relevant PR
		return True  # Filter out global corporate PR
	
	return False


def process_article(article: dict, default_category: str) -> dict:
	"""Simple processing without GPT."""
	title = article.get("title", "Untitled")
	description = article.get("description", "")
	url = article.get("url", "")
	
	# Filter out irrelevant articles
	if not is_relevant(title, description):
		return None
	
	# Filter out low-value corporate PR (unless ANZ-specific)
	if is_corporate_pr(title, description, url):
		return None
	
	# Add source tag
	source_type = article.get("_source_type")
	if source_type in ("RSS", "Legislation"):
		title = f"[{source_type}] {title}"
	
	# Simple keyword classification
	category = classify_by_keywords(title, description)
	
	# Simple importance scoring
	score = 50  # Default
	text = (title + " " + description).lower()
	
	# Boost for high-value keywords
	if any(word in text for word in ['financial stability', 'reserve bank', 'rba', 'central bank', 'monetary policy']):
		score += 30  # RBA/central bank content is very important
	if any(word in text for word in ['asic', 'apra', 'enforcement', 'fraud', 'breach', 'investigation']):
		score += 20
	if any(word in text for word in ['acquisition', 'merger', 'ipo']):
		score += 15
	if any(word in text for word in ['privacy', 'data protection', 'compliance']):
		score += 10
	
	# Cap at 100
	score = min(score, 100)
	
	# Label
	if score >= 91:
		label = "Very Important"
	elif score >= 75:
		label = "Important"
	elif score >= 50:
		label = "Moderately Important"
	elif score >= 25:
		label = "Less Important"
	else:
		label = "Not Important"
	
	return {
		"title": title,
		"summary": description[:300] if description else "No summary available",
		"importance_score": score,
		"importance_label": label,
		"category": category,
		"link": article.get("url", ""),
		"source": article.get("source", ""),
	}


def main():
	print("✅ Starting simple collection mode (no GPT)...")
	args = parse_args()
	settings = Settings()
	ensure_output_dir(settings.output_dir)

	max_per_category = args.max_per_category
	gnews_client = GNewsClient(api_key=settings.gnews_api_key)
	rss_client = RSSClient(feeds=RSS_FEEDS)
	report = ReportBuilder(since=args.since)

	seen_links = set()
	categorized = {k: [] for k in CATEGORIES.keys()}

	# Step 1: RSS feeds
	print("📡 Fetching RSS feeds...")
	rss_items = rss_client.fetch_since(args.since, max_items_per_feed=50)
	print(f"  Found {len(rss_items)} RSS items")
	
	for item in rss_items:
		link = item.get("url")
		if link and link in seen_links:
			continue
		result = process_article(item, "Regulation")
		if result is None:  # Filtered out as irrelevant
			continue
		cat = result["category"]
		if link:
			seen_links.add(link)
		categorized[cat].append(result)
	print(f"  Categorized: {sum(len(v) for v in categorized.values())} articles")

	# Step 2: GNews (simple queries)
	print("🔍 Fetching GNews articles...")
	for category_name in CATEGORIES.keys():
		# Simple queries (GNews free tier doesn't support OR operators well)
		simple_queries = {
			"Competition": "Experian Australia",
			"Regulation": "ASIC financial services",
			"Disruptive Trends and Technological Advancements": "fintech Australia",
			"Consumer Behaviour and Insights": "consumer credit Australia",
			"Market Trends": "financial services trends Australia"
		}
		
		query = simple_queries.get(category_name, "Australia news")
		print(f"  Searching '{category_name}'...")
		
		try:
			articles = gnews_client.search(query=query, since=args.since, page_size=max_per_category, domains=None)
			print(f"    Found {len(articles)} articles")
			
			for article in articles:
				link = article.get("url")
				if link and link in seen_links:
					continue
				result = process_article(article, category_name)
				if result is None:  # Filtered out as irrelevant
					continue
				if link:
					seen_links.add(link)
				categorized[category_name].append(result)
		except Exception as e:
			print(f"    Error: {e}")

	# Deduplicate within each category
	print("🔄 Deduplicating articles...")
	for cat_name in categorized.keys():
		if categorized[cat_name]:
			categorized[cat_name] = deduplicate_articles(categorized[cat_name])
	
	# Add to report
	for cat_name, items in categorized.items():
		report.add_category_results(cat_name, items[:max_per_category], since=args.since)

	output_path = report.write_markdown(output_dir=settings.output_dir)
	
	total = sum(len(items[:max_per_category]) for items in categorized.values())
	print(f"\n{'='*60}")
	print(f"✅ Report saved to: {output_path}")
	print(f"📊 Total articles in report: {total}")
	for cat, items in categorized.items():
		if items:
			print(f"   - {cat}: {len(items[:max_per_category])}")
	print(f"\n💡 Open dashboard: streamlit run dashboard.py")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	main()
