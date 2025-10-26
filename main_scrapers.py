#!/usr/bin/env python3
"""
Market Intelligence with curated site scrapers.
Scrapes specific, relevant news sites directly - no API needed.
"""

import argparse
from src.config import Settings, ensure_output_dir
from src.categories import CATEGORIES
from src.rss_client import RSSClient
from src.rss_feeds import RSS_FEEDS
from src.site_scrapers import SiteScrapers
from src.report import ReportBuilder
from src.deduplication import deduplicate_articles
from main_simple import is_relevant, classify_by_keywords, process_article


def parse_args():
	parser = argparse.ArgumentParser(description="AI Market Intelligence — Curated Site Scrapers")
	parser.add_argument("--since", required=True, help="Start date (YYYY-MM-DD)")
	parser.add_argument("--max-per-category", type=int, default=10, help="Max articles per category")
	return parser.parse_args()


def main():
	print("✅ Starting curated site scraper mode...")
	args = parse_args()
	settings = Settings()
	ensure_output_dir(settings.output_dir)

	max_per_category = args.max_per_category
	rss_client = RSSClient(feeds=RSS_FEEDS)
	site_scrapers = SiteScrapers()
	report = ReportBuilder(since=args.since)

	seen_links = set()
	categorized = {k: [] for k in CATEGORIES.keys()}

	# Step 1: RSS feeds (Privacy NZ)
	print("📡 Fetching RSS feeds...")
	rss_items = rss_client.fetch_since(args.since, max_items_per_feed=50)
	print(f"  Found {len(rss_items)} RSS items")
	
	rss_kept = 0
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
		rss_kept += 1
	print(f"  Kept {rss_kept} relevant RSS articles")

	# Step 2: Scrape curated news sites
	print("🌐 Scraping curated news sites...")
	scraped_articles = site_scrapers.scrape_all(args.since, max_per_site=15)
	print(f"  Collected {len(scraped_articles)} articles from web scraping")
	
	scraped_kept = 0
	for article in scraped_articles:
		link = article.get("url")
		if link and link in seen_links:
			continue
		result = process_article(article, "Competition")
		if result is None:
			continue
		cat = result["category"]
		if link:
			seen_links.add(link)
		categorized[cat].append(result)
		scraped_kept += 1
	print(f"  Kept {scraped_kept} relevant scraped articles")

	# Deduplicate within each category
	print("🔄 Deduplicating articles...")
	for cat_name in categorized.keys():
		if categorized[cat_name]:
			original_count = len(categorized[cat_name])
			categorized[cat_name] = deduplicate_articles(categorized[cat_name])
			deduped_count = len(categorized[cat_name])
			if original_count != deduped_count:
				print(f"  {cat_name}: {original_count} → {deduped_count}")
	
	# Add to report
	for cat_name, items in categorized.items():
		# Sort by importance score (descending)
		items_sorted = sorted(items, key=lambda x: x.get('importance_score', 0), reverse=True)
		report.add_category_results(cat_name, items_sorted[:max_per_category], since=args.since)

	output_path = report.write_markdown(output_dir=settings.output_dir)
	
	# Summary stats
	total_collected = rss_kept + scraped_kept
	total_in_report = sum(len(items[:max_per_category]) for items in categorized.values())
	
	print(f"\n{'='*60}")
	print(f"✅ Report saved to: {output_path}")
	print(f"📊 Collection summary:")
	print(f"   RSS feeds: {rss_kept} articles")
	print(f"   Web scrapers: {scraped_kept} articles")
	print(f"   Total collected: {total_collected}")
	print(f"   Total in report: {total_in_report} (after dedup & limits)")
	print(f"\n📁 Articles by category:")
	for cat, items in categorized.items():
		count = len(items[:max_per_category])
		if count > 0:
			print(f"   - {cat}: {count} articles")
	print(f"\n💡 Next steps:")
	print(f"   1. Open dashboard: streamlit run dashboard.py")
	print(f"   2. Review and rate articles")
	print(f"   3. Run: python analyze_feedback.py (after 20+ ratings)")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	main()


