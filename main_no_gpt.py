import argparse
import os
from datetime import datetime

from src.config import Settings, ensure_output_dir
from src.categories import CATEGORIES
from src.gnews_client import GNewsClient
from src.rss_client import RSSClient
from src.rss_feeds import RSS_FEEDS
from src.legislation_scraper import LegislationScraper
from src.report import ReportBuilder


# Australian government domains for GNews site filtering
AU_GOV_DOMAINS = [
	"asic.gov.au", "accc.gov.au", "oaic.gov.au", "austrac.gov.au",
	"apra.gov.au", "rba.gov.au", "treasury.gov.au", "pmc.gov.au",
	"homeaffairs.gov.au", "industry.gov.au", "ag.gov.au",
]


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="AI Market Intelligence — No-GPT Mode (Fast Collection)")
	parser.add_argument("--since", required=True, help="Start date (YYYY-MM-DD). Only news after this date are considered.")
	parser.add_argument("--max-per-category", type=int, default=None, help="Max number of articles to collect per category.")
	parser.add_argument("--output-dir", type=str, default=None, help="Output directory for the Markdown report.")
	return parser.parse_args()


def simple_process_article(article: dict, default_category: str) -> dict:
	"""Process article without GPT - just use original data and assign default category."""
	title = article.get("title", "Untitled")
	description = article.get("description", "")
	summary = description or "No summary available"
	
	# Add source tag if present
	source_type = article.get("_source_type")
	if source_type in ("RSS", "Legislation"):
		title = f"[{source_type}] {title}"
	
	return {
		"title": title,
		"summary": summary[:300],  # Truncate long summaries
		"importance_score": 50,  # Default to "Moderately Important"
		"importance_label": "Moderately Important",
		"category": default_category,
		"link": article.get("url", ""),
	}


def main() -> None:
	print("✅ Script started (NO-GPT MODE - Fast Collection)...")
	args = parse_args()
	settings = Settings()
	if args.output_dir:
		settings.output_dir = args.output_dir
	ensure_output_dir(settings.output_dir)
	print("✅ Env loaded...")

	max_per_category = args.max_per_category or settings.max_articles_per_category
	print(f"Max per category: {max_per_category}")
	
	gnews_client = GNewsClient(api_key=settings.gnews_api_key)
	print("GNewsClient created")
	rss_client = RSSClient(feeds=RSS_FEEDS)
	print("RSSClient created")
	legislation_scraper = LegislationScraper()
	print("LegislationScraper created")
	report = ReportBuilder(since=args.since)
	print("Report builder created")

	seen_links = set()
	categorized: dict[str, list] = {k: [] for k in CATEGORIES.keys()}

	# Step 1: Federal Register of Legislation
	print("📜 Fetching Federal Register of Legislation...")
	legislation_items = legislation_scraper.fetch_whats_new(args.since, max_items=20)
	print(f"  Found {len(legislation_items)} legislation items")
	for i, item in enumerate(legislation_items):
		title = item.get("title", "No title")
		print(f"  Collecting legislation {i+1}/{len(legislation_items)}: {title[:50]}...")
		link = item.get("url")
		if link and link in seen_links:
			continue
		result = simple_process_article(item, default_category="Regulation")
		cat = result.get("category") or "Regulation"
		if link:
			seen_links.add(link)
		categorized.setdefault(cat, []).append(result)
	print("📜 Legislation done...")

	# Step 2: RSS feeds
	print("📡 Fetching RSS feeds...")
	rss_items = rss_client.fetch_since(args.since, max_items_per_feed=200)
	print(f"  Found {len(rss_items)} RSS items")
	for i, item in enumerate(rss_items):
		title = item.get("title", "No title")
		print(f"  Collecting RSS item {i+1}/{len(rss_items)}: {title[:50]}...")
		link = item.get("url")
		if link and link in seen_links:
			continue
		result = simple_process_article(item, default_category="Regulation")
		cat = result.get("category") or "Regulation"
		if link:
			seen_links.add(link)
		categorized.setdefault(cat, []).append(result)
	print("📡 RSS done...")

	# Step 3: GNews by category (with AU gov domain filtering)
	print("🔍 Fetching GNews articles...")
	for category_name, query in CATEGORIES.items():
		# 3a. Government sources (*.gov.au domains)
		print(f"  Searching '{category_name}' - Government sources...")
		gov_articles = gnews_client.search(
			query=query, 
			since=args.since, 
			page_size=max_per_category,
			domains=AU_GOV_DOMAINS
		)
		print(f"    Found {len(gov_articles)} government articles")
		
		# 3b. General sources (all news, no domain filter)
		print(f"  Searching '{category_name}' - General news sources...")
		general_articles = gnews_client.search(
			query=query, 
			since=args.since, 
			page_size=max_per_category,
			domains=None  # No domain filter = all sources
		)
		print(f"    Found {len(general_articles)} general articles")
		
		# Process all articles (no GPT, no delays!)
		all_articles = gov_articles + general_articles
		for i, article in enumerate(all_articles):
			title = article.get("title", "No title")
			print(f"  Collecting article {i+1}/{len(all_articles)}: {title[:50]}...")
			link = article.get("url")
			if link and link in seen_links:
				continue
			result = simple_process_article(article, default_category=category_name)
			cat = result.get("category") or category_name
			if link:
				seen_links.add(link)
			categorized.setdefault(cat, []).append(result)
	print("🔍 GNews done...")

	# Add results to report by category
	for cat_name, items in categorized.items():
		report.add_category_results(cat_name, items[:max_per_category], since=args.since)

	print("📝 Writing report...")
	output_path = report.write_markdown(output_dir=settings.output_dir)
	
	# Count total articles
	total_articles = sum(len(items) for items in categorized.values())
	
	print(f"\n{'='*60}")
	print(f"✅ Report saved to: {output_path}")
	print(f"📊 Total articles collected: {total_articles}")
	print(f"📁 Articles by category:")
	for cat_name, items in categorized.items():
		print(f"   - {cat_name}: {len(items[:max_per_category])} articles")
	print(f"\n💡 Next steps:")
	print(f"   1. Open dashboard: streamlit run dashboard.py")
	print(f"   2. Review articles and rate them (👍/👎)")
	print(f"   3. Manually adjust categories if needed")
	print(f"   4. Once you have 20+ ratings, run: python analyze_feedback.py")
	print(f"   5. When ready for GPT, add OpenAI payment and use: python main.py")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	main()


