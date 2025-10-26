"""
Generate HTML report with clickable links for browser viewing.
"""

from typing import Dict, List
from datetime import datetime
import os


def importance_badge(score: int) -> str:
	"""Return HTML badge for importance level."""
	if score >= 91:
		return '<span style="background: #e74c3c; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">🔴 Very Important</span>'
	elif score >= 75:
		return '<span style="background: #f39c12; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">🟠 Important</span>'
	elif score >= 50:
		return '<span style="background: #f1c40f; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">🟡 Moderately Important</span>'
	elif score >= 25:
		return '<span style="background: #95a5a6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">⚪ Less Important</span>'
	else:
		return '<span style="background: #bdc3c7; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">Not Important</span>'


def generate_html_report(categories: Dict[str, List[Dict]], since: str) -> str:
	"""Generate HTML report with clickable links."""
	
	html = f"""<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>Market Intelligence Report - {datetime.now().strftime('%Y-%m-%d')}</title>
	<style>
		body {{
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
			line-height: 1.6;
			max-width: 1200px;
			margin: 0 auto;
			padding: 20px;
			background: #f5f7fa;
			color: #2c3e50;
		}}
		h1 {{
			color: #2c3e50;
			border-bottom: 4px solid #3498db;
			padding-bottom: 15px;
			margin-bottom: 30px;
		}}
		h2 {{
			color: #34495e;
			margin-top: 40px;
			margin-bottom: 20px;
			padding: 10px;
			background: #ecf0f1;
			border-left: 5px solid #3498db;
		}}
		.article {{
			background: white;
			margin: 15px 0;
			padding: 20px;
			border-radius: 8px;
			box-shadow: 0 2px 5px rgba(0,0,0,0.1);
			border-left: 4px solid #3498db;
		}}
		.article-title {{
			font-size: 1.2em;
			font-weight: bold;
			color: #2c3e50;
			margin-bottom: 10px;
		}}
		.article-summary {{
			color: #555;
			margin: 12px 0;
			line-height: 1.5;
		}}
		.article-meta {{
			margin-top: 15px;
			padding-top: 10px;
			border-top: 1px solid #ecf0f1;
		}}
		.article-link {{
			display: inline-block;
			margin-top: 10px;
			padding: 10px 20px;
			background: #3498db;
			color: white;
			text-decoration: none;
			border-radius: 5px;
			font-weight: bold;
		}}
		.article-link:hover {{
			background: #2980b9;
		}}
		.tag {{
			display: inline-block;
			background: #9b59b6;
			color: white;
			padding: 3px 8px;
			border-radius: 3px;
			font-size: 0.85em;
			margin-right: 5px;
		}}
		.empty-category {{
			color: #7f8c8d;
			font-style: italic;
			padding: 10px;
		}}
		.header-stats {{
			background: white;
			padding: 20px;
			border-radius: 8px;
			margin-bottom: 30px;
			box-shadow: 0 2px 5px rgba(0,0,0,0.1);
		}}
	</style>
</head>
<body>
	<h1>📊 Market Intelligence Report</h1>
	<div class="header-stats">
		<p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
		<p><strong>Period:</strong> Articles from {since}</p>
	</div>
"""
	
	# Add each category
	for category, items in categories.items():
		html += f'\n\t<h2>{category}</h2>\n'
		
		if not items:
			html += f'\t<p class="empty-category">No relevant news on {category} was released since {since}.</p>\n'
			continue
		
		for item in items:
			title = item.get('title', 'Untitled').strip()
			summary = item.get('summary', '').strip()
			score = int(item.get('importance_score', 0))
			link = item.get('link', '')
			
			# Extract tags from title
			tags = []
			if '[RSS]' in title:
				tags.append('RSS')
				title = title.replace('[RSS]', '').strip()
			if '[Legislation]' in title:
				tags.append('Legislation')
				title = title.replace('[Legislation]', '').strip()
			if '[Newsletter]' in title:
				tags.append('Newsletter')
				title = title.replace('[Newsletter]', '').strip()
			
			tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in tags])
			
			html += f'''
	<div class="article">
		<div class="article-title">{title}</div>
		<div class="article-meta">
			{tags_html}
			{importance_badge(score)}
		</div>
		<div class="article-summary">{summary}</div>
		<a href="{link}" target="_blank" class="article-link">🔗 Read Full Article</a>
	</div>
'''
	
	html += """
</body>
</html>"""
	
	return html


def save_html_report(categories: Dict[str, List[Dict]], since: str, output_dir: str) -> str:
	"""Save HTML report to file."""
	html = generate_html_report(categories, since)
	
	stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
	filename = f"market_intel_report_{stamp}.html"
	path = os.path.join(output_dir, filename)
	
	with open(path, 'w', encoding='utf-8') as f:
		f.write(html)
	
	return path
