from typing import Dict, List
from datetime import datetime
import os
import re


def importance_level(score: int) -> str:
	if score >= 91:
		return "Very Important"
	if score >= 75:
		return "Important"
	if score >= 50:
		return "Moderately Important"
	if score >= 25:
		return "Less Important"
	return "Not Important"


def clean_summary(summary: str, max_length: int = 350, title: str = "") -> str:
	"""Clean and improve summary text."""
	if not summary or len(summary.strip()) < 10:
		# If no meaningful summary, extract source from title
		if title:
			# Try to extract source/publication from title
			if " - " in title:
				parts = title.split(" - ")
				if len(parts) >= 2:
					source = parts[-1].strip()
					return f"Source: {source}. Click link to read full article for details."
			elif "|" in title:
				parts = title.split("|")
				if len(parts) >= 2:
					source = parts[-1].strip()
					return f"Source: {source}. Click link to read full article for details."
			return "Click link above to read full article for details."
		return ""  # Empty summary, will show title
	
	# Remove HTML tags
	summary = re.sub(r'<[^>]+>', '', summary)
	
	# Remove HTML entities
	summary = summary.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&quot;', '"')
	
	# Remove common email footers and disclaimers
	footer_patterns = [
		r'Disclaimer.*',
		r'This email contains general information.*',
		r'For more.*visit our website',
		r'To unsubscribe.*',
		r'You (are )?receiv(ed|ing) this.*',
		r'If you received this email by mistake.*',
		r'Please confirm.*subscription.*',
		r'© \d{4}.*',
		r'Your Google Account.*is now protected.*',
		r'Please confirm your subscription.*',
	]
	for pattern in footer_patterns:
		summary = re.sub(pattern, '', summary, flags=re.IGNORECASE | re.DOTALL)
	
	# Clean up whitespace first
	summary = re.sub(r'\s+', ' ', summary).strip()
	
	# If summary is exactly the same as title, just return empty (title will be shown)
	if title and summary.lower().strip() == title.lower().strip():
		return ""
	
	# Extract first 2-4 sentences (usually the key info)
	# Split on sentence boundaries but be careful not to split on abbreviations
	sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', summary)
	if sentences and len(sentences) > 1:
		# Take first 2-4 sentences or until we hit max_length
		result = ""
		for sentence in sentences[:4]:
			sentence = sentence.strip()
			if sentence and len(result) + len(sentence) + 1 <= max_length:
				result += sentence + " "
			elif result:  # Already have some content, stop here
				break
		summary = result.strip()
	
	# Truncate if still too long, but try to end at sentence boundary
	if len(summary) > max_length:
		# Try to find last sentence boundary before max_length
		truncated = summary[:max_length]
		last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
		if last_period > max_length * 0.7:  # If we can keep at least 70% with sentence boundary
			summary = summary[:last_period + 1]
		else:
			summary = summary[:max_length-3] + "..."
	
	# Return summary (even if short - it's better than nothing)
	return summary.strip()


class ReportBuilder:
	def __init__(self, since: str) -> None:
		self.since = since
		self.categories: Dict[str, List[Dict]] = {}

	def add_category_results(self, category: str, items: List[Dict], since: str) -> None:
		self.categories[category] = items

	def _render_category(self, category: str, items: List[Dict]) -> str:
		lines: List[str] = [f"## {category}\n"]
		if not items:
			lines.append(f"*No relevant news on {category} was released since {self.since}.*\n")
			return "\n".join(lines)
		for it in items:
			title = (it.get("title") or "Untitled").strip()
			summary = clean_summary(it.get("summary") or "", max_length=350, title=title)
			score = int(it.get("importance_score") or 0)
			label = (it.get("importance_label") or importance_level(score)).strip()
			cat = (it.get("category") or category).strip()
			link = it.get("link") or ""
			
			# Format link - show both Markdown link AND raw URL
			if link:
				link_text = f"[Read Article →]({link}) | {link}"
			else:
				link_text = ""
			
			# If no summary after cleaning, just show title and link
			if not summary:
				lines.append(f"- **{title}** | Score: **{score}** ({label}) | {link_text}")
			else:
				lines.append(f"- **{title}** | {summary} | Score: **{score}** ({label}) | {link_text}")
		return "\n".join(lines)

	def write_markdown(self, output_dir: str) -> str:
		stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
		filename = f"market_intel_report_{stamp}.md"
		path = os.path.join(output_dir, filename)
		sections: List[str] = []
		for category, items in self.categories.items():
			sections.append(self._render_category(category, items))
			sections.append("")
		content = "\n\n".join(sections).strip() + "\n"
		with open(path, "w", encoding="utf-8") as f:
			f.write(content)
		return path
