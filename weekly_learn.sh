#!/bin/bash
# Weekly auto-learning script
# Run this every Sunday to update filters based on your feedback

cd "/Users/jamfor/Library/CloudStorage/Dropbox/Personal/General/AI Market Intelligence"
source .venv/bin/activate

echo "🧠 Weekly Auto-Learning Process"
echo "================================"
echo ""

# Check feedback count
feedback_count=$(wc -l < feedback.jsonl 2>/dev/null || echo "0")
echo "📊 Current feedback: $feedback_count ratings"
echo ""

if [ "$feedback_count" -lt 20 ]; then
    echo "⚠️  Not enough feedback yet ($feedback_count/20)"
    echo "   Continue rating articles and run again next week"
    exit 0
fi

# Run analyzer first (for your review)
echo "📈 Running feedback analysis..."
python analyze_feedback.py

echo ""
echo "================================"
echo ""

# Ask to apply auto-learning
echo "🤖 Ready to auto-update filters based on your feedback?"
echo ""
python auto_learn.py

echo ""
echo "✅ Weekly learning complete!"
echo ""
echo "📝 Changes logged to: learning_log.jsonl"
echo "🔍 Next: Run daily updates to see improved results"
