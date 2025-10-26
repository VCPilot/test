import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
	openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
	openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	newsapi_api_key: str = os.getenv("NEWSAPI_API_KEY", "")
	gnews_api_key: str = os.getenv("GNEWS_API_KEY", "")
	serpapi_key: str = os.getenv("SERPAPI_KEY", "")
	max_articles_per_category: int = int(os.getenv("MAX_ARTICLES_PER_CATEGORY", "10"))
	output_dir: str = os.getenv("OUTPUT_DIR", "reports")
	
	# Email settings (optional)
	email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
	email_to: str = os.getenv("EMAIL_TO", "")
	smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
	smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
	smtp_user: str = os.getenv("SMTP_USER", "")
	smtp_password: str = os.getenv("SMTP_PASSWORD", "")
	smtp_from: str = os.getenv("SMTP_FROM", "")
	
	# Email inbox settings (for newsletter parsing)
	email_inbox_host: str = os.getenv("EMAIL_INBOX_HOST", "")
	email_inbox_port: int = int(os.getenv("EMAIL_INBOX_PORT", "993"))
	email_inbox_user: str = os.getenv("EMAIL_INBOX_USER", "")
	email_inbox_password: str = os.getenv("EMAIL_INBOX_PASSWORD", "")


def ensure_output_dir(path: str) -> None:
	if not os.path.isdir(path):
		os.makedirs(path, exist_ok=True)
