# 📊 Feedback & Dashboard Setup Guide

This guide shows you how to set up the **hybrid feedback system**: Email summaries + Interactive dashboard + Markdown archives.

## Overview

The system has three components:
1. **Email summaries** — Get top articles delivered to your inbox
2. **Streamlit dashboard** — Interactive web interface for detailed review
3. **Flask feedback server** — Handles feedback from email links

---

## Quick Start (Without Email)

If you just want to use the dashboard (no email), do this:

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate a report
```bash
python main.py --since 2024-12-01 --max-per-category 3
```

### 3. Open the dashboard
```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

### 4. Rate articles
- Click 👍 Relevant or 👎 Not Relevant for each article
- Add notes and tags
- Filter by category, importance, rating status
- View analytics

Done! Feedback is saved to `feedback.jsonl`

---

## Full Setup (With Email)

To enable email summaries with inline feedback links:

### 1. Configure email settings in `.env`

```bash
# Email configuration (optional)
EMAIL_ENABLED=true
EMAIL_TO=your.email@example.com

# SMTP settings (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your.email@gmail.com
```

**Note for Gmail users:**
- You'll need an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
- Enable 2-factor authentication first
- Generate an app password at: https://myaccount.google.com/apppasswords

### 2. Start the feedback server

In one terminal:
```bash
python feedback_server.py
```

This runs at `http://localhost:5000` and handles feedback links from emails.

### 3. Start the dashboard

In another terminal:
```bash
streamlit run dashboard.py
```

This runs at `http://localhost:8501` for detailed review.

### 4. Run the agent

```bash
python main.py --since 2024-12-01
```

This will:
- Generate the report
- Save Markdown to `reports/`
- Send HTML email with top articles
- Include feedback links in email

---

## Using the System

### Email Workflow

1. **Receive email** with top "Very Important" and "Important" articles
2. **Quick feedback** — Click 👍 Relevant or 👎 Not Relevant in email
3. **Deep dive** — Click "Open Interactive Dashboard" for full review

### Dashboard Workflow

1. **Filter articles** by category, importance, rating status
2. **Rate articles** with 👍/👎 buttons
3. **Add notes** for context
4. **View analytics** — relevance rate, category distribution

### Feedback Links

Email contains links like:
```
http://localhost:5000/feedback?url=...&rating=relevant
http://localhost:5000/feedback?url=...&rating=not_relevant
```

When clicked:
1. Feedback saved to `feedback.jsonl`
2. "Thank you" page shown
3. Option to open dashboard

---

## Feedback Data

All feedback is stored in `feedback.jsonl`:

```json
{"article_url": "https://...", "rating": "relevant", "notes": "Key competitor news", "timestamp": "2024-12-01T10:30:00"}
{"article_url": "https://...", "rating": "not_relevant", "notes": "Too general", "timestamp": "2024-12-01T10:31:00"}
```

### Analyzing Feedback

```bash
# Count ratings
grep '"rating": "relevant"' feedback.jsonl | wc -l
grep '"rating": "not_relevant"' feedback.jsonl | wc -l

# Extract URLs of irrelevant articles
grep '"rating": "not_relevant"' feedback.jsonl | jq -r .article_url
```

---

## Scheduled Runs (Optional)

### Daily email digest (macOS/Linux)

1. Edit crontab:
```bash
crontab -e
```

2. Add daily run at 9 AM:
```bash
0 9 * * * cd /path/to/project && /path/to/.venv/bin/python main.py --since $(date -v-7d +\%Y-\%m-\%d) >> logs/cron.log 2>&1
```

This runs daily and searches for news from the last 7 days.

### Keep servers running

Use `tmux` or `screen` to keep dashboard/feedback server running:

```bash
# Start tmux
tmux new -s market_intel

# Run feedback server
python feedback_server.py

# Detach: Ctrl+B, then D

# New window: Ctrl+B, then C
streamlit run dashboard.py

# Detach: Ctrl+B, then D
```

Reattach later:
```bash
tmux attach -t market_intel
```

---

## Troubleshooting

### Email not sending
- Check SMTP credentials in `.env`
- For Gmail, use App Password, not regular password
- Verify `EMAIL_ENABLED=true`

### Dashboard not loading report
- Run `python main.py --since 2024-12-01` first
- Check `reports/` directory has files
- Restart dashboard: `streamlit run dashboard.py`

### Feedback links not working
- Start feedback server: `python feedback_server.py`
- Check it's running at `http://localhost:5000`
- Test: Open `http://localhost:5000/` in browser

### Dashboard shows wrong data
- Clear Streamlit cache: Click menu → "Clear cache"
- Refresh browser
- Check latest report in `reports/`

---

## Next Steps

### Week 1: Collect feedback
- Rate articles as relevant/not relevant
- Add notes for context
- Aim for 50-100 ratings

### Week 2: Analyze patterns
- Review `feedback.jsonl`
- Identify common false positives (e.g., "missing person" stories)
- Identify common true positives (e.g., "merger", "acquisition")

### Week 3: Improve queries
- Add negative keywords: `NOT (missing OR celebrity OR sport)`
- Boost positive keywords
- Adjust importance scoring weights

### Future: Auto-learning
- Train custom relevance model on feedback data
- Auto-adjust queries based on patterns
- Personalized importance scoring

---

## Tips

- **Start simple**: Use dashboard only, skip email for now
- **Rate consistently**: Mark articles as you review them
- **Add notes**: Helps identify patterns later
- **Review weekly**: Look at analytics to spot trends
- **Iterate queries**: Continuously refine based on feedback

---

## Support

Questions? Issues? Create a GitHub issue or check the main README.md
