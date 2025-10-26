# 🚀 Quick Start Guide - Market Intelligence System

## Daily Workflow (5 minutes/day)

### 1. Run Daily Update
```bash
./daily_update.sh
```

**What it does:**
- Parses your email newsletters from last 3 days
- Filters for financial services/regulatory/tech news
- Skips articles you rated "not relevant"
- Skips articles you've already seen
- Removes duplicates
- Sorts by date (newest first)
- Generates Markdown + HTML reports

### 2. Review in Dashboard
```bash
# Dashboard should already be running at:
http://localhost:8501

# If not, start it:
streamlit run dashboard.py
```

**In the dashboard:**
- Select "Date (Newest First)" in sidebar
- Review 15-25 new articles
- Click blue "🔗 Open Article in Browser" buttons
- Rate: ⚡ 4-5 for relevant, ❌ 1-2 for not relevant
- Add notes explaining why (optional but helpful)

### 3. Done!
Next-day articles you rated "not relevant" won't appear again.

---

## Weekly Learning (10 minutes/week)

### Every Sunday (or weekly):
```bash
./weekly_learn.sh
```

**What it does:**
- Analyzes your ratings and notes
- Finds patterns (e.g., "webinar" appears in not-relevant)
- Shows you recommendations
- Asks to auto-update filters
- Logs changes for audit trail

**Result:** Future runs will automatically filter out patterns you don't like!

---

## Current System Status

### ✅ What's Working:

**Data Sources:**
- 📧 Email newsletters (28+ per day)
- 📡 RSS feeds (RBA, Privacy NZ)

**Intelligence:**
- ✅ 482 links extracted daily
- ✅ ~75 relevant after filtering
- ✅ ~20-25 in final report (after dedup)
- ✅ Skips 237 URLs (seen + not-relevant)

**Features:**
- ✅ Feedback filtering (won't show not-relevant again)
- ✅ Smart deduplication (removes duplicate stories)
- ✅ Date sorting (newest first)
- ✅ Clickable links in dashboard
- ✅ Weekly auto-learning

**Quality:**
- ~80% relevance (based on your ratings)
- Coverage: Regulation (60%), Disruptive Trends (30%), Other (10%)

---

## File Structure

```
daily_update.sh          ← Run daily
weekly_learn.sh          ← Run weekly
main_newsletters.py      ← Main script (called by daily_update.sh)
dashboard.py             ← Streamlit dashboard
analyze_feedback.py      ← Analyze your ratings
auto_learn.py            ← Auto-update filters

reports/                 ← Generated reports
  *.md                   ← Markdown reports
  *.html                 ← HTML reports (clickable in browser)

feedback.jsonl           ← Your ratings and notes
seen_articles.jsonl      ← Tracks shown articles (30 days)
learning_log.jsonl       ← Auto-learning audit trail

src/                     ← Code modules
```

---

## Troubleshooting

### Dashboard not loading?
```bash
pkill -f streamlit
streamlit run dashboard.py
```

### Want to see more articles?
```bash
# Increase max per category
python main_newsletters.py --since-days 3 --max-per-category 20
```

### Want to reset and see everything fresh?
```bash
python reset_seen.py
python main_newsletters.py --since-days 7
```

### Dashboard still showing old articles at top?
- Select "Date (Newest First)" in left sidebar
- Or select "Importance (Highest First)"

---

## Next Steps

### This Week:
1. Run `./daily_update.sh` every morning
2. Rate articles in dashboard
3. Build up 50+ more ratings

### Next Sunday:
1. Run `./weekly_learn.sh`
2. Review recommendations
3. Apply auto-updates
4. See improved relevance

### Next Month:
1. Subscribe to more newsletters (see NEWSLETTER_SETUP.md)
2. Add OpenAI payment for GPT-powered summarization (optional)
3. Set up automated daily runs (cron job)

---

## Key Insights

**Best practices from your feedback (236 ratings):**
- ✅ ASIC enforcement articles → Highly relevant
- ✅ Privacy/data protection → Relevant
- ✅ Fraud/identity verification → Relevant
- ❌ Webinars/promos → Not relevant
- ❌ Health/general government → Not relevant
- ❌ International (non-AU/NZ) → Not relevant

**The system learns from this and gets better over time!**

---

## Quick Commands

```bash
# Daily update
./daily_update.sh

# Weekly learning
./weekly_learn.sh

# Analyze feedback
python analyze_feedback.py

# Reset seen articles
python reset_seen.py

# View latest HTML report
open reports/market_intel_report_*.html | tail -1
```

---

**You're all set!** The system is production-ready for daily use with weekly auto-learning. 🎉