#!/bin/bash
# Daily market intelligence update script
# Usage: ./daily_update.sh

cd "/Users/jamfor/Library/CloudStorage/Dropbox/Personal/General/AI Market Intelligence"
source .venv/bin/activate

echo "🚀 Running daily market intelligence update..."
echo ""

# Run with 3-day window (catches weekends if you miss a day)
python main_newsletters.py --since-days 3 --max-per-category 10

echo ""
echo "✅ Update complete!"
echo "📊 Open dashboard: http://localhost:8501"
echo ""
echo "💡 Rate articles in dashboard, then run again tomorrow"
