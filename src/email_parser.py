"""
Email newsletter parser for market intelligence.
Connects to inbox, reads newsletters, extracts article links and summaries.
"""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re


# Map email sources to categories
SOURCE_CATEGORY_MAP = {
	'asic.gov.au': 'Regulation',
	'apra.gov.au': 'Regulation',
	'accc.gov.au': 'Regulation',
	'oaic.gov.au': 'Regulation',
	'austrac.gov.au': 'Regulation',
	'privacy.org.nz': 'Regulation',
	'fma.govt.nz': 'Regulation',
	'rbnz.govt.nz': 'Regulation',
	
	'fintechaustralia.org.au': 'Disruptive Trends and Technological Advancements',
	'innovationaus.com': 'Disruptive Trends and Technological Advancements',
	'itnews.com.au': 'Disruptive Trends and Technological Advancements',
	
	'afr.com': 'Market Trends',
	'interest.co.nz': 'Market Trends',
	'brokernews.com.au': 'Competition',
	'theadviser.com.au': 'Competition',
	
	# Google Alerts - prioritize as high-value news source
	'google.com': 'Market Trends',
	'googlealerts': 'Market Trends',
	
	'equifax.com.au': 'Competition',
	'experian.com.au': 'Competition',
	'illion.com.au': 'Competition',
}


class EmailParser:
	def __init__(self, host: str, port: int, username: str, password: str):
		self.host = host
		self.port = port
		self.username = username
		self.password = password
	
	def connect(self) -> imaplib.IMAP4_SSL:
		"""Connect to email inbox."""
		mail = imaplib.IMAP4_SSL(self.host, self.port)
		mail.login(self.username, self.password)
		return mail
	
	def parse_emails_since(self, days_ago: int = 7, folder: str = 'INBOX') -> List[Dict]:
		"""
		Parse newsletter emails from the last N days.
		Returns list of article dictionaries.
		"""
		try:
			mail = self.connect()
			mail.select(folder)
			
			# Search for emails since date
			date_since = (datetime.now() - timedelta(days=days_ago)).strftime("%d-%b-%Y")
			_, message_ids = mail.search(None, f'(SINCE {date_since})')
			
			articles = []
			
			for msg_id in message_ids[0].split():
				_, msg_data = mail.fetch(msg_id, '(RFC822)')
				
				for response_part in msg_data:
					if isinstance(response_part, tuple):
						msg = email.message_from_bytes(response_part[1])
						
						# Parse email
						article_batch = self._parse_email(msg)
						articles.extend(article_batch)
			
			mail.close()
			mail.logout()
			
			print(f"  Parsed {len(articles)} articles from {len(message_ids[0].split())} emails")
			return articles
			
		except Exception as e:
			print(f"  Error parsing emails: {e}")
			return []
	
	def _parse_email(self, msg) -> List[Dict]:
		"""Parse a single email to extract article links."""
		articles = []
		
		# Get from address
		from_addr = msg.get('From', '').lower()
		
		# Determine category based on source
		category = 'Regulation'  # Default
		for domain, cat in SOURCE_CATEGORY_MAP.items():
			if domain in from_addr:
				category = cat
				break
		
		# Get subject
		subject = self._decode_header(msg.get('Subject', ''))
		
		# Get email body
		body = self._get_email_body(msg)
		if not body:
			return articles
		
		# Parse HTML to find links
		soup = BeautifulSoup(body, 'html.parser')
		links = soup.find_all('a', href=True)
		
		for link in links:
			href = link['href']
			
			# Skip mailto links
			if href.startswith('mailto:'):
				continue
			
			# Skip unsubscribe, social, footer links
			if any(skip in href.lower() for skip in ['unsubscribe', 'facebook', 'twitter', 'linkedin', 'instagram', 'preferences', 'manage-subscription', 'privacy-policy', 'privacy_policy', 'terms-of-service', 'terms-and-conditions']):
				continue
			
			# Skip internal newsletter links
			if any(skip in href.lower() for skip in ['newsletter', 'subscribe', 'view-in-browser', 'email.', '/t/', '/e/', 'tracking', 'click-track']):
				continue
			
			# Skip very short or suspicious URLs
			if len(href) < 20:
				continue
			
			# Get link text as title
			title = link.get_text(strip=True)
			
			# Skip empty or very short titles
			if not title or len(title) < 15:
				continue
			
			# Skip footer/navigation text
			if any(skip in title.lower() for skip in [
				'unsubscribe', 'view in browser', 'privacy policy', 'terms of service', 
				'click here', 'read more', 'learn more', 'update preferences', 
				'manage subscription', 'forward to a friend', 'open this email',
				'click to view email', 'view email as web page', 'email as web page',
				'update subscription', 'how to set up my account', 'help guide',
				'contact us using', 'why did i get this'
			]):
				continue
			
			# Skip event/promo/whitepaper titles
			if any(skip in title.lower() for skip in [
				'webinar', 'register now', 'join us', 'rsvp', 'congress', 'conference', 
				'forum', 'summit', 'symposium', 'side events', 'whitepaper', 'white paper', 
				'download now', 'free report', 'event invitation', 'podcast', 'bu podcast',
				'enroll', 'enrollment', 'last day', 'deadline', 'market overview', 
				'industry overview', 'report download', 'free guide', 'ebook', 'e-book',
				'what you need to know', 'what professionals need to know',
				'ultimate guide', 'complete guide', 'step-by-step guide',
				'concepts and solutions report', 'optimizing', 'impact of environmental',
				'how a global bank', 'mitigates', 'from trust to risk', 'decentralized verification'
			]):
				continue
			
			# Try to find description near the link
			parent = link.parent
			description = ""
			if parent:
				desc_text = parent.get_text(strip=True)
				# Clean up
				if len(desc_text) > len(title):
					description = desc_text
			
			# Skip generic newsletter headers/footers (check both title and description)
			combined_text = f"{title} {description}".lower()
			if any(phrase in combined_text for phrase in [
				'has sent you this email because you have subscribed',
				'your personal information, including your email address will be used',
				'mailchimp to deliver these emails',
				'unsubscribe from these communications',
				'privacy policy', 'terms of service',
				'if you no longer wish to receive',
				'click here to unsubscribe'
			]):
				continue
			
			# Skip URLs that contain promo patterns
			# Check both the visible URL and any encoded/wrapped URLs
			url_to_check = href.lower()
			# For Biometric Update tracking links, decode the base64 portion if present
			if 'biometricupdate.com/wp-admin/admin-ajax.php' in url_to_check and 'nltr=' in url_to_check:
				try:
					import base64
					import urllib.parse
					# Extract and decode the nltr parameter
					nltr_match = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get('nltr')
					if nltr_match:
						decoded = base64.b64decode(nltr_match[0] + '==').decode('utf-8', errors='ignore')
						url_to_check += ' ' + decoded.lower()
				except:
					pass
			
			if any(skip in url_to_check for skip in ['/register', 'register-', '/webinar', '/event/', '/download', '/whitepaper', '/content-hub/', '/resources/', '/guides/']):
				continue
			
			# Skip if title is just a domain or email
			if '@' in title or title.startswith('http'):
				continue
			
			# Try to find description near the link
			parent = link.parent
			description = ""
			if parent:
				desc_text = parent.get_text(strip=True)
				# Clean up
				if len(desc_text) > len(title):
					description = desc_text
			
			articles.append({
				"title": title,
				"description": description or title,
				"content": description or title,
				"url": href,
				"source": self._extract_source_name(from_addr),
				"publishedAt": msg.get('Date'),
				"_source_type": "Newsletter",
				"_newsletter_category": category,
			})
		
		return articles
	
	def _decode_header(self, header: str) -> str:
		"""Decode email header."""
		if not header:
			return ""
		decoded = decode_header(header)
		return ''.join([
			part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
			for part, encoding in decoded
		])
	
	def _get_email_body(self, msg) -> str:
		"""Extract email body (prefer HTML)."""
		body = ""
		
		if msg.is_multipart():
			for part in msg.walk():
				content_type = part.get_content_type()
				
				if content_type == "text/html":
					try:
						body = part.get_payload(decode=True).decode()
						break  # Prefer HTML
					except:
						pass
				elif content_type == "text/plain" and not body:
					try:
						body = part.get_payload(decode=True).decode()
					except:
						pass
		else:
			try:
				body = msg.get_payload(decode=True).decode()
			except:
				pass
		
		return body
	
	def _extract_source_name(self, from_addr: str) -> str:
		"""Extract clean source name from email address."""
		# Extract domain
		match = re.search(r'@([a-z0-9.-]+)', from_addr)
		if match:
			domain = match.group(1)
			# Clean up
			domain = domain.replace('www.', '').replace('.com.au', '').replace('.gov.au', '').replace('.org.au', '')
			return domain.title()
		return "Unknown"


