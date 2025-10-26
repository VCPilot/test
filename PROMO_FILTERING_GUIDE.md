# Promotional Content Filtering Guide

## The Problem
Biometric Update newsletters contain a mix of:
- ✅ Real news articles (relevant)
- ❌ Event promos (webinars, conferences, summits)
- ❌ Content marketing (whitepapers, ebooks, podcasts)
- ❌ Registration deadlines

**Challenge**: Promo titles SOUND relevant (e.g., "AI fraud detection webinar") but they're not news.

## The Solution: Two-Layer Defense

### Layer 1: Automated Filtering (Catches 90%+)

#### Email Parser Filter (`src/email_parser.py`)
Blocks promotional links at the source by checking:

**Title keywords:**
- webinar, podcast, enroll, deadline, last day
- congress, conference, forum, summit, symposium
- whitepaper, ebook, free report, market overview

**URL patterns:**
- `/register`, `/webinar`, `/event/`, `/download`

#### Relevance Filter (`main_simple.py`)
Second layer catches anything that slips through using the same keyword list.

### Layer 2: Manual Flagging (Handles Edge Cases)

#### New "Mark as Promo" Button
When reviewing in the dashboard:
- **For off-topic articles**: Click regular rating buttons (1-5)
- **For promo/events**: Click **"🚫 Event/Webinar/Promo"** button

**Why this matters:**
```
❌ Bad: Rate webinar as "1 - Not Relevant"
   → Algorithm learns: "AI fraud detection" = not relevant
   → Blocks real news about AI fraud!

✅ Good: Click "🚫 Event/Webinar/Promo"
   → Flagged as promo (won't affect topic learning)
   → Algorithm learns: This is promotional FORMAT, not irrelevant TOPIC
```

## How the Learning Works

### Without Promo Flag:
```json
{
  "article_title": "Register: AI fraud detection webinar",
  "rating": 1,
  "is_promo": false
}
```
→ Algorithm extracts: "ai", "fraud", "detection"
→ Learns: These topics are NOT relevant ❌ WRONG!

### With Promo Flag:
```json
{
  "article_title": "Register: AI fraud detection webinar",
  "rating": 1,
  "is_promo": true
}
```
→ Algorithm SKIPS this entry (doesn't analyze content)
→ Learns: Nothing about the topic, only filters promotional format ✅ CORRECT!

## Usage in Dashboard

### Scenario 1: Off-Topic Article
**Example**: "Trump announces housing policy"
**Action**: Click **"❌ 1"** (Not Relevant)
**Effect**: Algorithm learns to avoid Trump/housing topics

### Scenario 2: Promotional Content
**Example**: "Register now: Biometrics Institute Congress"
**Action**: Click **"🚫 Event/Webinar/Promo"**
**Effect**: 
- Filters URL immediately
- Doesn't affect topic learning
- Keywords added to promo filter list

### Scenario 3: Relevant News
**Example**: "ASIC fines bank for AML breach"
**Action**: Click **"🔥 5"** (Highly Relevant)
**Effect**: Algorithm learns ASIC/AML/enforcement are relevant topics

## Monitoring Effectiveness

Run the agent and check:
```bash
python main_newsletters.py --since-days 1 --max-per-category 10
```

**Before improvements**: ~19 articles (many promos)
**After improvements**: ~10 articles (mostly real news)

## Weekly Auto-Learning

When you run `python auto_learn_v2.py`:
1. Loads all feedback from `feedback.jsonl`
2. **SKIPS** entries where `is_promo = true`
3. Analyzes only genuine topic relevance
4. Recommends keywords based on article content

**Result**: Clean topic learning without noise from promotional content!

## Summary

| Content Type | How to Rate | Effect on Learning |
|-------------|-------------|-------------------|
| Off-topic news | Rate 1-2 | ✅ Learns topic irrelevance |
| Relevant news | Rate 4-5 | ✅ Learns topic relevance |
| Promo/Event | Click "🚫 Promo" | ✅ Skipped from learning |

**Key Principle**: Separate FORMAT filtering (webinar/promo) from TOPIC learning (fraud/banking).

