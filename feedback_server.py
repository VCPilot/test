#!/usr/bin/env python3
"""
Simple Flask server for email feedback links.
Run with: python feedback_server.py
"""

from flask import Flask, request, redirect, render_template_string
import json
from datetime import datetime
import os

app = Flask(__name__)
FEEDBACK_FILE = "feedback.jsonl"

def save_feedback(article_url, rating, notes=""):
	"""Append feedback to JSONL file."""
	entry = {
		"article_url": article_url,
		"rating": rating,
		"notes": notes,
		"timestamp": datetime.utcnow().isoformat()
	}
	with open(FEEDBACK_FILE, 'a') as f:
		f.write(json.dumps(entry) + '\n')
	return entry

@app.route('/feedback')
def feedback():
	"""Handle feedback from email links."""
	article_url = request.args.get('url', '')
	rating = request.args.get('rating', '')
	
	if not article_url or not rating:
		return "Invalid feedback link", 400
	
	# Save feedback
	save_feedback(article_url, rating)
	
	# Show thank you page
	thank_you_html = """
	<!DOCTYPE html>
	<html>
	<head>
		<title>Feedback Received</title>
		<style>
			body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
			       text-align: center; padding: 50px; background: #f8f9fa; }
			.container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; 
			             border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
			h1 { color: #27ae60; }
			.btn { display: inline-block; margin: 20px 10px; padding: 12px 24px; 
			       background: #3498db; color: white; text-decoration: none; 
			       border-radius: 6px; font-weight: bold; }
		</style>
	</head>
	<body>
		<div class="container">
			<h1>✅ Feedback Received!</h1>
			<p>Thank you for rating this article as <strong>{{ rating }}</strong>.</p>
			<p>Your feedback helps improve future reports.</p>
			<a href="http://localhost:8501" class="btn">📊 Open Dashboard</a>
			<a href="javascript:window.close()" class="btn" style="background: #95a5a6;">Close</a>
		</div>
	</body>
	</html>
	"""
	
	return render_template_string(thank_you_html, rating=rating.replace('_', ' ').title())

@app.route('/dashboard')
def dashboard_redirect():
	"""Redirect to Streamlit dashboard."""
	return redirect("http://localhost:8501")

@app.route('/')
def index():
	"""Show feedback stats."""
	# Load feedback
	feedback_data = []
	if os.path.exists(FEEDBACK_FILE):
		with open(FEEDBACK_FILE, 'r') as f:
			for line in f:
				try:
					feedback_data.append(json.loads(line))
				except:
					pass
	
	relevant_count = len([f for f in feedback_data if f.get('rating') == 'relevant'])
	not_relevant_count = len([f for f in feedback_data if f.get('rating') == 'not_relevant'])
	
	index_html = """
	<!DOCTYPE html>
	<html>
	<head>
		<title>Market Intelligence Feedback</title>
		<style>
			body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
			       padding: 50px; background: #f8f9fa; }
			.container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; 
			             border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
			h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
			.stats { display: flex; justify-content: space-around; margin: 30px 0; }
			.stat { text-align: center; }
			.stat-value { font-size: 3em; font-weight: bold; color: #3498db; }
			.stat-label { color: #7f8c8d; margin-top: 10px; }
			.btn { display: inline-block; margin: 20px 10px; padding: 15px 30px; 
			       background: #3498db; color: white; text-decoration: none; 
			       border-radius: 6px; font-weight: bold; font-size: 1.1em; }
		</style>
	</head>
	<body>
		<div class="container">
			<h1>📊 Market Intelligence Feedback System</h1>
			<p>Feedback stats for all reports:</p>
			
			<div class="stats">
				<div class="stat">
					<div class="stat-value">{{ total }}</div>
					<div class="stat-label">Total Ratings</div>
				</div>
				<div class="stat">
					<div class="stat-value" style="color: #27ae60;">{{ relevant }}</div>
					<div class="stat-label">Relevant</div>
				</div>
				<div class="stat">
					<div class="stat-value" style="color: #e74c3c;">{{ not_relevant }}</div>
					<div class="stat-label">Not Relevant</div>
				</div>
			</div>
			
			<div style="text-align: center;">
				<a href="http://localhost:8501" class="btn">📊 Open Interactive Dashboard</a>
			</div>
		</div>
	</body>
	</html>
	"""
	
	return render_template_string(
		index_html, 
		total=len(feedback_data),
		relevant=relevant_count,
		not_relevant=not_relevant_count
	)

if __name__ == '__main__':
	print("🚀 Feedback server starting...")
	print("📧 Email feedback links: http://localhost:5000/feedback?url=...&rating=...")
	print("📊 Dashboard redirect: http://localhost:5000/dashboard")
	print("📈 Stats page: http://localhost:5000/")
	app.run(debug=True, port=5000)
