#!/usr/bin/env python3
"""
Market Intelligence from email newsletters.
Best approach: curated, free, high signal-to-noise ratio.
"""

import argparse
from src.config import Settings, ensure_output_dir
from src.categories import CATEGORIES
from src.email_parser import EmailParser
from src.rss_client import RSSClient
from src.rss_feeds import RSS_FEEDS
from src.report import ReportBuilder
from src.html_report import save_html_report
from src.deduplication import deduplicate_articles
from src.seen_tracker import load_seen_urls, mark_as_seen, cleanup_old_entries
from src.feedback_filter import load_not_relevant_urls
from main_simple import is_relevant, classify_by_keywords, process_article


def parse_args():
	parser = argparse.ArgumentParser(description="AI Market Intelligence — Newsletter Mode")
	parser.add_argument("--since-days", type=int, default=7, help="Parse emails from last N days")
	parser.add_argument("--max-per-category", type=int, default=10, help="Max articles per category")
	return parser.parse_args()


def main():
	print("✅ Starting newsletter intelligence mode...")
	args = parse_args()
	settings = Settings()
	ensure_output_dir(settings.output_dir)

	# Check if email settings are configured
	if not all([settings.email_inbox_host, settings.email_inbox_user, settings.email_inbox_password]):
		print("\n⚠️  Email inbox not configured!")
		print("\nTo use newsletter mode, add to .env:")
		print("  EMAIL_INBOX_HOST=imap.gmail.com")
		print("  EMAIL_INBOX_PORT=993")
		print("  EMAIL_INBOX_USER=your-email@gmail.com")
		print("  EMAIL_INBOX_PASSWORD=your-app-password")
		print("\nFor now, using RSS feeds only...\n")
		use_email = False
	else:
		use_email = True

	max_per_category = args.max_per_category
	report = ReportBuilder(since=f"{args.since_days} days ago")

	# Load previously seen articles AND not-relevant feedback
	print("🔍 Loading previously seen articles...")
	seen_links = load_seen_urls(days_to_keep=30)
	print(f"  Found {len(seen_links)} articles from previous runs")
	
	print("🚫 Loading not-relevant articles from your feedback...")
	not_relevant_urls = load_not_relevant_urls()
	print(f"  Found {len(not_relevant_urls)} articles you rated as not relevant")
	
	# Skip both seen AND not-relevant
	skip_urls = seen_links.union(not_relevant_urls)
	print(f"  Total URLs to skip: {len(skip_urls)}")
	
	# Import normalize function for URL matching
	from src.feedback_filter import normalize_url
	
	categorized = {k: [] for k in CATEGORIES.keys()}

	# Step 1: Parse email newsletters (if configured)
	if use_email:
		print(f"📧 Parsing email newsletters (last {args.since_days} days)...")
		try:
			email_parser = EmailParser(
				host=settings.email_inbox_host,
				port=settings.email_inbox_port,
				username=settings.email_inbox_user,
				password=settings.email_inbox_password
			)
			
			email_articles = email_parser.parse_emails_since(days_ago=args.since_days)
			print(f"  Found {len(email_articles)} articles from newsletters")
			
			email_kept = 0
			for article in email_articles:
				link = article.get("url")
				# Check both exact URL and normalized version (for tracking URL variants)
				if link and (link in skip_urls or normalize_url(link) in skip_urls):
					continue
				
				# Use newsletter's suggested category or classify
				suggested_cat = article.get("_newsletter_category", "Regulation")
				result = process_article(article, suggested_cat)
				if result is None:
					continue
				
				cat = result["category"]
				if link:
					seen_links.add(link)
				categorized[cat].append(result)
				email_kept += 1
			
			print(f"  Kept {email_kept} relevant newsletter articles")
			
		except Exception as e:
			print(f"  Error with email: {e}")
			print(f"  Continuing with RSS only...")

	# Step 2: RSS feeds (backup/supplement)
	print("📡 Fetching RSS feeds...")
	rss_client = RSSClient(feeds=RSS_FEEDS)
	rss_items = rss_client.fetch_since("2024-01-01", max_items_per_feed=50)  # Get all recent
	print(f"  Found {len(rss_items)} RSS items")
	
	rss_kept = 0
	for item in rss_items:
		link = item.get("url")
		# Check both exact URL and normalized version (for tracking URL variants)
		if link and (link in skip_urls or normalize_url(link) in skip_urls):
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

	# Deduplicate
	print("🔄 Deduplicating articles...")
	for cat_name in categorized.keys():
		if categorized[cat_name]:
			original = len(categorized[cat_name])
			categorized[cat_name] = deduplicate_articles(categorized[cat_name])
			deduped = len(categorized[cat_name])
			if original != deduped:
				print(f"  {cat_name}: {original} → {deduped}")
	
	# Sort by date (newest first), then by importance
	print("📅 Sorting articles by date (newest first)...")
	from dateutil import parser as dateparser
	
	for cat_name, items in categorized.items():
		def get_sort_key(item):
			# Try to parse date
			pub_date = item.get("publishedAt")
			if pub_date:
				try:
					date_val = dateparser.parse(pub_date)
					# Return tuple: (date, importance) for sorting
					return (date_val, item.get('importance_score', 0))
				except:
					pass
			# No date: use importance only, but put at bottom
			return (dateparser.parse("2000-01-01"), item.get('importance_score', 0))
		
		items_sorted = sorted(items, key=get_sort_key, reverse=True)
		report.add_category_results(cat_name, items_sorted[:max_per_category], since=f"{args.since_days} days ago")

	output_path = report.write_markdown(output_dir=settings.output_dir)
	
	# Also generate HTML version
	html_path = save_html_report(categorized, f"{args.since_days} days ago", settings.output_dir)
	
	# Mark articles as seen to avoid showing them again
	new_urls = []
	for items in categorized.values():
		for item in items[:max_per_category]:
			url = item.get('link')
			if url:
				new_urls.append(url)
	
	if new_urls:
		mark_as_seen(new_urls)
		print(f"📝 Marked {len(new_urls)} articles as seen")
	
	# Cleanup old entries
	cleanup_old_entries(days_to_keep=7)
	
	# Summary
	total_in_report = sum(len(items[:max_per_category]) for items in categorized.values())
	
	print(f"\n{'='*60}")
	print(f"✅ Markdown report saved to: {output_path}")
	print(f"✅ HTML report saved to: {html_path}")
	print(f"\n💡 Open HTML report in browser for clickable links:")
	print(f"📊 Total articles in report: {total_in_report}")
	for cat, items in categorized.items():
		count = len(items[:max_per_category])
		if count > 0:
			print(f"   - {cat}: {count} articles")
	
	if not use_email:
		print(f"\n💡 To enable newsletter parsing:")
		print(f"   1. Subscribe to newsletters (see NEWSLETTER_SETUP.md)")
		print(f"   2. Configure email inbox in .env")
		print(f"   3. Run again: python main_newsletters.py")
	
	print(f"\n📊 Open dashboard: streamlit run dashboard.py")
	print(f"{'='*60}\n")


if __name__ == "__main__":
	main()


