### AI Market Intelligence — Competitor Research Agent

This tool searches recent news, RSS feeds, and legislation after a given date, summarizes with GPT-4, classifies into five categories, assigns an importance score, and saves a Markdown report.

## Features

- **Federal Register of Legislation**: Scrapes "What's new" from https://www.legislation.gov.au (Acts, Legislative Instruments, Gazettes, etc.)
- **RSS Feeds**: 16 curated AU/NZ government and regulator feeds (ASIC, ACCC, OAIC, Privacy NZ, Beehive NZ, etc.)
- **GNews API**: Site-filtered news search across Australian government domains (*.gov.au)
- **GPT-4 Classification**: Automatic summarization, categorization, and importance scoring (0-100)
- **Source Tagging**: [Legislation] and [RSS] tags for easy identification
- **Deduplication**: By URL across all sources
- **Five Categories**: Competition, Regulation, Disruptive Trends & Tech, Consumer Behaviour, Market Trends

## Requirements
- Python 3.9+
- API keys:
  - OpenAI (`OPENAI_API_KEY`): https://platform.openai.com
  - GNews (`GNEWS_API_KEY`): https://gnews.io (100 requests/day free tier)

## Setup

1. **Create and activate a virtual environment** (recommended):
```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env to add your API keys:
# - OPENAI_API_KEY (required)
# - GNEWS_API_KEY (required)
```

## Usage

Run with a start date (ISO format YYYY-MM-DD):
```bash
python main.py --since 2024-12-01
```

### Optional arguments:
- `--max-per-category 2` — Limit articles per category (default: 10)
- `--output-dir reports` — Custom report directory (default: reports/)

### Example:
```bash
python main.py --since 2024-12-01 --max-per-category 5
```

The generated Markdown report will be saved under `reports/` with a timestamped filename.

### **Interactive Dashboard**
View and rate articles in a web interface:
```bash
streamlit run dashboard.py
```
Opens at `http://localhost:8501` with:
- Filter by category, importance, rating status
- Rate articles (👍 Relevant / 👎 Not Relevant)
- Add notes and tags
- View analytics and feedback stats

### **Email Summaries** (Optional)
Get HTML emails with top articles and inline feedback links. See `FEEDBACK_SETUP.md` for configuration.

## Output Format

Reports are organized by category:

```
Competition
- [RSS] Title | Summary | Importance Score (75, [Important]) | Competition | https://...
- Title | Summary | Importance Score (50, [Moderately Important]) | Competition | https://...

Regulation
- [Legislation] Title | Summary | Importance Score (90, [Important]) | Regulation | https://...
- No relevant news on Regulation was released since 2024-12-01.
```

## Importance Scoring

- **91-100**: Very Important — immediate impact
- **75-90**: Important — significant medium-term impact
- **50-74**: Moderately Important — useful but not critical
- **25-49**: Less Important — tangential relevance
- **0-24**: Not Important — irrelevant

## Data Sources

### 1. Federal Register of Legislation
- Acts, Legislative Instruments, Notifiable Instruments, Gazettes
- Scraped from: https://www.legislation.gov.au/whats-new/*
- Tagged as: **[Legislation]**

### 2. RSS Feeds (16 feeds)
**Working feeds:**
- New Zealand Privacy Commissioner
- Beehive.govt.nz (NZ Government)

**Additional feeds** (may have 0 entries depending on date range):
- ASIC, ACCC, OAIC, APRA, AUSTRAC (Australia)
- MBIE, RBNZ, Commerce Commission, FMA (New Zealand)

Tagged as: **[RSS]**

### 3. GNews API (Dual Search)
**Two searches per category:**
1. **Government sources** — Site-filtered: asic.gov.au, accc.gov.au, oaic.gov.au, apra.gov.au, treasury.gov.au, etc.
2. **General sources** — All news (Bloomberg, Reuters, AFR, business press, industry sites, etc.)

This captures BOTH:
- Government/regulatory announcements
- Competitor news (Illion, Experian, Equifax, etc.)
- Market news (M&A, funding, partnerships, IPOs)
- Industry trends and analysis

- 100 requests/day on free tier (10 per category × 2 searches × 5 categories = 10 total)
- No special tag (regular news articles)

## Performance & Rate Limits

### OpenAI Rate Limits (Free Tier)
- **Requests**: 3 per minute (25-second delays between calls)
- **Tokens**: 100,000 per minute

**Token optimization:**
- Content truncated to 500 chars (input)
- Response limited to 300 tokens (output)
- Reduced ~60% token usage vs. original

### Typical Runtime
- **Federal Register**: ~10-20 seconds (4 pages)
- **RSS Feeds**: ~2-3 minutes (16 feeds, some timeouts)
- **GNews**: ~5-10 seconds per category
- **OpenAI Processing**: ~25 seconds per article
- **Total**: ~10-15 minutes for --max-per-category 2

### Tips to Reduce Runtime
1. Use `--max-per-category 1` to process fewer items
2. Add payment method to OpenAI for higher rate limits (3500 RPM)
3. Use more recent dates (e.g., --since 2024-12-15) to reduce RSS items

## Troubleshooting

### OpenAI Rate Limit Error
```
Rate limit reached for gpt-4o-mini... Please try again in 2h...
```
**Solution**: Wait for rate limit reset, or add payment method to OpenAI account.

### RSS Feed Timeouts
Some feeds timeout (10-second limit). These are automatically skipped with error messages.

### Empty Categories
If a category shows "No relevant news", it means:
- No articles found for that category's query, OR
- Date filter excluded older items, OR
- RSS feeds returned 0 entries

Try an older date: `--since 2020-01-01`

## Notes

- **GNews free tier**: 100 requests/day. The script uses **10 requests per run** (2 per category: government + general sources).
- **Dual search strategy**: Each category searches BOTH government domains AND general news to capture regulatory + competitor/market news.
- **Federal Register**: Scraped politely with 15-second timeout and user agent identification.
- **RSS feeds**: Most AU government feeds have empty or malformed RSS. NZ feeds work better.
- **Token optimization**: Content is truncated to ~500 chars to reduce token usage by ~60%.
- **Deduplication**: Articles are deduplicated by URL across all three sources.

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
GNEWS_API_KEY=...

# Optional
OPENAI_MODEL=gpt-4o-mini
MAX_ARTICLES_PER_CATEGORY=10
OUTPUT_DIR=reports
```

## Feedback & Learning

The system includes a **hybrid feedback loop**:

1. **Interactive Dashboard** (`streamlit run dashboard.py`)
   - Rate articles as relevant/not relevant
   - Add notes and context
   - View analytics

2. **Email Summaries** (optional)
   - HTML emails with top articles
   - Inline feedback links
   - See `FEEDBACK_SETUP.md` for setup

3. **Feedback Analysis** (`feedback.jsonl`)
   - All ratings stored as JSONL
   - Analyze patterns
   - Improve queries based on feedback

**Quick start:**
```bash
# Generate report
python main.py --since 2024-12-01

# Open dashboard
streamlit run dashboard.py

# Rate articles → feedback.jsonl updated automatically
```

See **`FEEDBACK_SETUP.md`** for detailed setup guide.

## Future Enhancements

- Auto-learning from feedback (query optimization)
- Fine-tuned relevance model
- Slack/Teams integration
- Azure Bing News Search (better geo filtering)
- Batch OpenAI requests (reduce latency)
- RSS feed auto-discovery

## License

MIT