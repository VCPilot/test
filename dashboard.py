#!/usr/bin/env python3
"""
Streamlit dashboard for Market Intelligence reports.
Run with: streamlit run dashboard.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd


# Page config
st.set_page_config(
	page_title="Market Intelligence Dashboard",
	page_icon="📊",
	layout="wide"
)

# Load feedback
FEEDBACK_FILE = "feedback.jsonl"

def load_feedback():
	"""Load existing feedback from JSONL file."""
	feedback = {}
	if os.path.exists(FEEDBACK_FILE):
		with open(FEEDBACK_FILE, 'r') as f:
			for line in f:
				try:
					entry = json.loads(line)
					url = entry.get('article_url')
					if url:
						feedback[url] = entry
				except:
					pass
	return feedback

def save_feedback(article_url, rating, notes="", tags=None, article_title="", article_summary="", is_promo=False):
	"""Append feedback to JSONL file with article metadata for learning."""
	entry = {
		"article_url": article_url,
		"rating": rating,
		"notes": notes,
		"tags": tags or [],
		"article_title": article_title,  # Store for content analysis
		"article_summary": article_summary,  # Store for content analysis
		"is_promo": is_promo,  # Flag for promotional/event content (not used for topic learning)
		"timestamp": datetime.utcnow().isoformat()
	}
	with open(FEEDBACK_FILE, 'a') as f:
		f.write(json.dumps(entry) + '\n')
	return entry

def load_latest_report():
	"""Load the most recent markdown report."""
	reports_dir = Path("reports")
	if not reports_dir.exists():
		return None, []
	
	# Find latest report
	reports = sorted(reports_dir.glob("market_intel_report_*.md"), reverse=True)
	if not reports:
		return None, []
	
	latest = reports[0]
	
	# Parse markdown to extract articles
	articles = []
	current_category = None
	
	with open(latest, 'r') as f:
		import re
		for line in f:
			line = line.strip()
			if not line:
				continue
			
			# Category header (new format with ##)
			if line.startswith("## "):
				current_category = line[3:].strip()
				continue
			
			# Category header (old format)
			if line in ["Competition", "Regulation", "Disruptive Trends and Technological Advancements", 
			            "Consumer Behaviour and Insights", "Market Trends"]:
				current_category = line
				continue
			
			# Article line (starts with -)
			if line.startswith("- ") and current_category:
				# New format: - **Title** | Summary | Score: **XX** (Label) | [Read Article →](link)
				# Old format: - Title | Summary | Importance Score (xx, [Label]) | Category | Link
				
				# Extract link first using regex (before splitting)
				link = ""
				link_match = re.search(r'\[Read Article →\]\(([^)]+)\)', line)
				if link_match:
					link = link_match.group(1)
				
				parts = line[2:].split(" | ")
				
				if len(parts) >= 2:
					# Extract title (remove ** markdown and [RSS] tags)
					title = parts[0].replace("**", "").strip()
					
					# Detect format by looking for "Score:" in any part
					score = 0
					summary = ""
					
					# New format: - **Title** | Summary | Score: **70** (Label) | [Link]
					if len(parts) >= 4 and "Score:" in parts[2]:
						summary = parts[1].strip()
						try:
							score = int(parts[2].split("**")[1])
						except:
							score = 50
					# Alternate new format: - **Title** | Score: **70** (Label) | [Link]
					elif len(parts) >= 3 and "Score:" in parts[1]:
						try:
							score = int(parts[1].split("**")[1])
						except:
							score = 50
						summary = title  # No separate summary
					# Old format: - Title | Summary | Importance Score (70, [Label]) | Category | Link
					elif len(parts) >= 3:
						summary = parts[1].strip()
						try:
							score = int(parts[2].split("(")[1].split(",")[0])
						except:
							score = 50
					else:
						summary = parts[1] if len(parts) >= 2 else ""
						score = 50
					
					# Link already extracted above (before split)
					# If link is still empty, it means the regex didn't match
					# This shouldn't happen with new format, but keep old format support
					if not link and len(parts) >= 5:
						link = parts[4].strip()
					
					# Use line position as proxy for date order (reports are pre-sorted by date)
					articles.append({
						"title": title,
						"summary": summary,
						"score": score,
						"category": current_category,
						"link": link,
						"_line_order": len(articles)  # Track original order from file
					})
	
	return latest.name, articles

# Main dashboard
st.title("📊 Market Intelligence Dashboard")

# Load data
feedback = load_feedback()
report_name, articles = load_latest_report()

if not articles:
	st.error("No reports found. Run `python main.py --since 2024-12-01` to generate a report.")
	st.stop()

st.success(f"📄 Loaded report: {report_name}")

# Sidebar filters
st.sidebar.header("Filters")
categories = ["All"] + sorted(set(a["category"] for a in articles))
selected_category = st.sidebar.selectbox("Category", categories)

min_score = st.sidebar.slider("Minimum Importance Score", 0, 100, 0)

# Sort options
st.sidebar.subheader("Sort By")
sort_by = st.sidebar.radio("Sort articles by:", ["Date (Newest First)", "Importance (Highest First)", "Category"])

show_rated = st.sidebar.checkbox("Show only rated articles", False)
show_unrated = st.sidebar.checkbox("Show only unrated articles", False)

# Filter articles
filtered_articles = articles

if selected_category != "All":
	filtered_articles = [a for a in filtered_articles if a["category"] == selected_category]

filtered_articles = [a for a in filtered_articles if a["score"] >= min_score]

if show_rated:
	filtered_articles = [a for a in filtered_articles if a["link"] in feedback]
elif show_unrated:
	filtered_articles = [a for a in filtered_articles if a["link"] not in feedback]

# Sort articles based on selection
if sort_by == "Date (Newest First)":
	# Use line order from report (reports are pre-sorted by date within categories)
	# Show articles in the order they appear in the report file (newest first within each category)
	filtered_articles = sorted(filtered_articles, key=lambda x: x.get('_line_order', 999))
elif sort_by == "Importance (Highest First)":
	filtered_articles = sorted(filtered_articles, key=lambda x: x.get('score', 0), reverse=True)
elif sort_by == "Category":
	# Group by category, then by line order
	filtered_articles = sorted(filtered_articles, key=lambda x: (x.get('category', ''), x.get('_line_order', 999)))

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Articles", len(articles))
col2.metric("Filtered", len(filtered_articles))
col3.metric("Rated", len([a for a in articles if a["link"] in feedback]))
col4.metric("Avg Score", f"{sum(a['score'] for a in articles) / len(articles):.0f}")

# Articles list
st.header(f"Articles ({len(filtered_articles)})")

for i, article in enumerate(filtered_articles):
	link = article["link"]
	existing_feedback = feedback.get(link, {})
	
	# Article container
	with st.expander(f"**{article['title']}**", expanded=i < 5):
		# Score badge
		score = article["score"]
		if score >= 91:
			st.markdown(f"🔴 **Very Important** ({score})")
		elif score >= 75:
			st.markdown(f"🟠 **Important** ({score})")
		elif score >= 50:
			st.markdown(f"🟡 **Moderately Important** ({score})")
		else:
			st.markdown(f"⚪ **Less Important** ({score})")
		
		st.markdown(f"**Category:** {article['category']}")
		
		# Clean and display summary
		from src.report import clean_summary
		clean_sum = clean_summary(article['summary'], max_length=300, title=article['title'])
		st.markdown(f"**Summary:** {clean_sum}")
		
		# Clickable link button
		if article['link']:
			st.link_button("🔗 Open Article in Browser", article['link'], use_container_width=True)
			# Also show copyable URL
			with st.expander("📋 Copy URL"):
				st.code(article['link'], language=None)
		
		# Debug: show if link is empty
		if not article.get('link'):
			st.error("⚠️ No link found for this article")
		
		# Feedback section
		st.divider()
		st.markdown("**Rate Relevance (1-5):**")
		
		# 1-5 Rating buttons
		col1, col2, col3, col4, col5 = st.columns(5)
		
		with col1:
			if st.button("❌ 1", key=f"rate1_{i}", help="Not Relevant - Completely off-topic"):
				save_feedback(link, 1, article_title=article['title'], article_summary=article['summary'])
				st.error("Rated 1 - Not Relevant")
				st.rerun()
		
		with col2:
			if st.button("📝 2", key=f"rate2_{i}", help="Slightly Relevant - Tangential connection"):
				save_feedback(link, 2, article_title=article['title'], article_summary=article['summary'])
				st.warning("Rated 2 - Slightly Relevant")
				st.rerun()
		
		with col3:
			if st.button("📋 3", key=f"rate3_{i}", help="Moderately Relevant - Useful but not priority"):
				save_feedback(link, 3, article_title=article['title'], article_summary=article['summary'])
				st.info("Rated 3 - Moderately Relevant")
				st.rerun()
		
		with col4:
			if st.button("⚡ 4", key=f"rate4_{i}", help="Very Relevant - Important for our domain"):
				save_feedback(link, 4, article_title=article['title'], article_summary=article['summary'])
				st.success("Rated 4 - Very Relevant")
				st.rerun()
		
		with col5:
			if st.button("🔥 5", key=f"rate5_{i}", help="Highly Relevant - Exactly what we need"):
				save_feedback(link, 5, article_title=article['title'], article_summary=article['summary'])
				st.success("Rated 5 - Highly Relevant")
				st.rerun()
		
		# Special "Mark as Promo" button
		if st.button("🚫 Event/Webinar/Promo", key=f"promo_{i}", help="Flag as promotional content (webinar/event/whitepaper) - blocks it but won't affect topic learning"):
			save_feedback(link, 1, notes="Promotional/event content", article_title=article['title'], article_summary=article['summary'], is_promo=True)
			st.warning("✅ Flagged as Promo (blocked from future reports, excluded from learning)")
			st.rerun()
		
		# Show existing feedback
		if existing_feedback:
			rating = existing_feedback.get('rating')
			is_promo = existing_feedback.get('is_promo', False)
			
			# Special display for promo-flagged items
			if is_promo:
				rating_text = "🚫 Promo/Event (Blocked, not used for learning)"
			else:
				rating_text = {
					1: "❌ 1 (Not Relevant)",
					2: "📝 2 (Slightly Relevant)", 
					3: "📋 3 (Moderately Relevant)",
					4: "⚡ 4 (Very Relevant)",
					5: "🔥 5 (Highly Relevant)",
					"relevant": "👍 Relevant (Legacy)",
					"not_relevant": "👎 Not Relevant (Legacy)"
				}.get(rating, f"Rating: {rating}")
			
			st.info(f"**Previous rating:** {rating_text} on {existing_feedback.get('timestamp', '')[:10]}")
			if existing_feedback.get('notes'):
				st.text(f"Notes: {existing_feedback.get('notes')}")
		
		# Notes input
		notes = st.text_input("Add notes (optional):", key=f"notes_{i}")
		if notes and st.button("Save Notes", key=f"save_{i}"):
			save_feedback(link, existing_feedback.get('rating', 'unrated'), notes=notes, 
			            article_title=article['title'], article_summary=article['summary'])
			st.success("Notes saved!")
			st.rerun()

# Feedback analytics
st.sidebar.header("Analytics")
if feedback:
	relevant_count = len([f for f in feedback.values() if f.get('rating') == 'relevant'])
	not_relevant_count = len([f for f in feedback.values() if f.get('rating') == 'not_relevant'])
	
	st.sidebar.metric("Relevant", relevant_count)
	st.sidebar.metric("Not Relevant", not_relevant_count)
	if relevant_count + not_relevant_count > 0:
		accuracy = relevant_count / (relevant_count + not_relevant_count) * 100
		st.sidebar.metric("Relevance Rate", f"{accuracy:.0f}%")
