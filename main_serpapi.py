#!/usr/bin/env python3
"""
Market Intelligence with SerpAPI (Google News scraping).
Best free-tier option with proper date filtering and site: operators.
"""

import argparse
from src.config import Settings, ensure_output_dir
from src.categories import CATEGORIES
from src.serpapi_client import SerpAPIClient
from src.rss_client import RSSClient
from src.rss_feeds import RSS_FEEDS
from src.report import ReportBuilder
from src.deduplication import deduplicate_articles
from main_simple import is_relevant, classify_by_keywords, process_article


def parse_args():
	parser = argparse.ArgumentParser(description="AI Market Intelligence — SerpAPI Mode")
	parser.add_argument("--since", required=True, help="Start date (YYYY-MM-DD)")
	parser.add_argument("--max-per-category", type=int, default=10, help="Max articles per category")
	return parser.parse_args()


def main():
	print("✅ Starting SerpAPI collection mode...")
	args = parse_args()
	settings = Settings()
	ensure_output_dir(settings.output_dir)

	max_per_category = args.max_per_category
	serpapi_client = SerpAPIClient(api_key=settings.serpapi_key)
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
		if result is None:
			continue
		cat = result["category"]
		if link:
			seen_links.add(link)
		categorized[cat].append(result)
	print(f"  Kept {sum(len(v) for v in categorized.values())} relevant articles")

	# Step 2: SerpAPI Google News searches
	print("🔍 Searching Google News (SerpAPI)...")
	
	# Define queries with site: operators for each category
	search_queries = {
		"Competition": [
			"Experian OR Illion OR Equifax site:com.au",
			"FICO OR 'Creditor Watch' OR Centrix site:co.nz",
			"'credit bureau' OR 'credit reporting' Australia",
		],
		"Regulation": [
			"ASIC enforcement OR investigation site:com.au",
			"APRA compliance OR regulation site:gov.au",
			"privacy OR 'data breach' site:gov.au site:co.nz",
			"AML OR 'anti-money laundering' Australia",
		],
		"Disruptive Trends and Technological Advancements": [
			"'digital identity' OR 'open banking' Australia",
			"fintech OR regtech Australia New Zealand",
			"'consumer data right' OR CDR site:gov.au",
		],
		"Consumer Behaviour and Insights": [
			"'consumer credit' OR 'household debt' Australia",
			"borrower OR lending Australia site:com.au",
		],
		"Market Trends": [
			"fintech funding OR investment Australia",
			"'financial services' merger OR acquisition site:com.au",
		],
	}
	
	for category_name, queries in search_queries.items():
		print(f"  Searching '{category_name}' ({len(queries)} queries)...")
		
		for query in queries:
			try:
				articles = serpapi_client.search_news(query=query, since=args.since, page_size=5)
				print(f"    Query: '{query[:50]}...' → {len(articles)} results")
				
				for article in articles:
					link = article.get("url")
					if link and link in seen_links:
						continue
					result = process_article(article, category_name)
					if result is None:
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
		if items[:max_per_category]:
			print(f"   - {cat}: {len(items[:max_per_category])}")
	print(f"\n💡 Open dashboard: streamlit run dashboard.py")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	main()


