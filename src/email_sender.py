import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os


class EmailSender:
	def __init__(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, from_email: str):
		self.smtp_host = smtp_host
		self.smtp_port = smtp_port
		self.smtp_user = smtp_user
		self.smtp_password = smtp_password
		self.from_email = from_email
	
	def send_report(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
		"""Send HTML email with optional plain text fallback."""
		try:
			msg = MIMEMultipart('alternative')
			msg['Subject'] = subject
			msg['From'] = self.from_email
			msg['To'] = to_email
			
			# Plain text fallback
			if text_content:
				part1 = MIMEText(text_content, 'plain')
				msg.attach(part1)
			
			# HTML content
			part2 = MIMEText(html_content, 'html')
			msg.attach(part2)
			
			# Send email
			with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
				server.starttls()
				server.login(self.smtp_user, self.smtp_password)
				server.sendmail(self.from_email, to_email, msg.as_string())
			
			return True
		except Exception as e:
			print(f"Error sending email: {e}")
			return False


def generate_html_email(articles_by_category: Dict[str, List[Dict]], report_date: str, dashboard_url: str) -> str:
	"""Generate HTML email with top articles and feedback links."""
	
	# Group articles by importance
	very_important = []
	important = []
	
	for category, articles in articles_by_category.items():
		for article in articles:
			score = article.get('importance_score', 0)
			if score >= 91:
				very_important.append(article)
			elif score >= 75:
				important.append(article)
	
	# Sort by score
	very_important.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
	important.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
	
	# Generate HTML
	html = f"""
<!DOCTYPE html>
<html>
<head>
	<style>
		body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
		h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
		h2 {{ color: #34495e; margin-top: 30px; }}
		.article {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 4px; }}
		.article.very-important {{ border-left-color: #e74c3c; background: #fee; }}
		.article.important {{ border-left-color: #f39c12; background: #fef5e7; }}
		.article-title {{ font-weight: bold; font-size: 1.1em; margin-bottom: 8px; color: #2c3e50; }}
		.article-summary {{ margin: 10px 0; color: #555; }}
		.article-meta {{ font-size: 0.9em; color: #7f8c8d; margin: 8px 0; }}
		.feedback-buttons {{ margin-top: 12px; }}
		.btn {{ display: inline-block; padding: 8px 16px; margin: 4px 8px 4px 0; text-decoration: none; border-radius: 4px; font-size: 0.9em; }}
		.btn-relevant {{ background: #27ae60; color: white; }}
		.btn-not-relevant {{ background: #e74c3c; color: white; }}
		.btn-view {{ background: #3498db; color: white; }}
		.dashboard-link {{ display: inline-block; margin: 20px 0; padding: 15px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 1.1em; }}
		.stats {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin: 20px 0; }}
	</style>
</head>
<body>
	<h1>📊 Market Intelligence Report</h1>
	<p><strong>Date:</strong> {report_date}</p>
	
	<div class="stats">
		<strong>Summary:</strong> {len(very_important)} Very Important | {len(important)} Important | 
		<a href="{dashboard_url}" style="color: #3498db;">View Full Report →</a>
	</div>
"""
	
	# Very Important items
	if very_important:
		html += "<h2>🔴 Very Important</h2>\n"
		for article in very_important[:5]:  # Top 5
			html += format_article_html(article, "very-important", dashboard_url)
	
	# Important items
	if important:
		html += "<h2>🟠 Important</h2>\n"
		for article in important[:5]:  # Top 5
			html += format_article_html(article, "important", dashboard_url)
	
	html += f"""
	<div style="text-align: center; margin: 40px 0;">
		<a href="{dashboard_url}" class="dashboard-link">
			📊 Open Interactive Dashboard
		</a>
	</div>
	
	<hr style="margin: 40px 0; border: none; border-top: 1px solid #ddd;">
	<p style="font-size: 0.9em; color: #7f8c8d; text-align: center;">
		AI Market Intelligence Agent | Powered by GPT-4, GNews, Federal Register
	</p>
</body>
</html>
"""
	
	return html


def format_article_html(article: Dict, importance_class: str, dashboard_url: str) -> str:
	"""Format a single article as HTML."""
	title = article.get('title', 'Untitled')
	summary = article.get('summary', '')
	score = article.get('importance_score', 0)
	label = article.get('importance_label', '')
	category = article.get('category', '')
	link = article.get('link', '')
	
	# Encode URL for feedback links
	import urllib.parse
	encoded_url = urllib.parse.quote(link)
	
	return f"""
<div class="article {importance_class}">
	<div class="article-title">{title}</div>
	<div class="article-summary">{summary}</div>
	<div class="article-meta">
		<strong>Score:</strong> {score} ({label}) | <strong>Category:</strong> {category}
	</div>
	<div class="feedback-buttons">
		<a href="{dashboard_url}/feedback?url={encoded_url}&rating=relevant" class="btn btn-relevant">👍 Relevant</a>
		<a href="{dashboard_url}/feedback?url={encoded_url}&rating=not_relevant" class="btn btn-not-relevant">👎 Not Relevant</a>
		<a href="{link}" class="btn btn-view" target="_blank">🔗 Read Article</a>
	</div>
</div>
"""
