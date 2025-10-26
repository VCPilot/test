from typing import Dict
import time
from openai import OpenAI


PROMPT_TEMPLATE = (
	"Analyze this news item and return JSON with: title (concise headline), summary (1-3 sentences, facts only), "
	"importance_score (0-100: 91-100=Very Important, 75-90=Important, 50-74=Moderately Important, 25-49=Less Important, 0-24=Not Important), "
	"importance_label (Very Important|Important|Moderately Important|Less Important|Not Important), "
	"category (Competition|Regulation|Disruptive Trends and Technological Advancements|Consumer Behaviour and Insights|Market Trends), "
	"link (original url). Default category: {default_category}. Return only JSON."
)


class OpenAINLP:
	def __init__(self, api_key: str, model: str) -> None:
		self.client = OpenAI(api_key=api_key)
		self.model = model
		self.last_request_time = 0

	def process_article(self, article: Dict, default_category: str) -> Dict:
		# Rate limiting: wait 25 seconds between requests (3 requests per minute)
		current_time = time.time()
		time_since_last = current_time - self.last_request_time
		if time_since_last < 25:
			wait_time = 25 - time_since_last
			print(f"    Rate limiting: waiting {wait_time:.1f} seconds...")
			time.sleep(wait_time)
		self.last_request_time = time.time()
		
		# Truncate content to reduce token usage (keep first 500 chars)
		title = (article.get("title") or "")[:200]
		description = (article.get("description") or "")[:300]
		content = (article.get("content") or "")[:500]
		
		# Simplified payload - only essential fields
		payload = f"Title: {title}\nDesc: {description}\nContent: {content}\nURL: {article.get('url')}"
		
		prompt = PROMPT_TEMPLATE.format(default_category=default_category)
		messages = [
			{"role": "system", "content": "Concise market intelligence analyst. Output JSON only."},
			{"role": "user", "content": f"{payload}\n\n{prompt}"},
		]
		completion = self.client.chat.completions.create(
			model=self.model, 
			messages=messages, 
			temperature=0.2,
			max_tokens=300  # Limit response tokens
		)
		text = completion.choices[0].message.content or "{}"
		try:
			import json
			obj = json.loads(text)
		except Exception:
			obj = {
				"title": article.get("title") or "Untitled",
				"summary": article.get("description") or "",
				"importance_score": 0,
				"importance_label": "Not Important",
				"category": default_category,
				"link": article.get("url"),
			}
		# If this came from RSS or Legislation, prefix the title
		source_type = article.get("_source_type")
		if source_type in ("RSS", "Legislation"):
			title = obj.get("title") or "Untitled"
			tag = f"[{source_type}]"
			if not title.startswith(tag):
				obj["title"] = f"{tag} {title}"
		return obj
