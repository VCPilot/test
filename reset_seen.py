#!/usr/bin/env python3
"""
Reset the seen articles tracker to get a fresh batch.
Use this when you want to re-run and see more articles.
"""

import os
import json
from datetime import datetime, timedelta

SEEN_FILE = "seen_articles.jsonl"


def reset_seen(keep_days: int = 0):
	"""
	Reset seen tracker.
	
	Args:
		keep_days: 0 = delete all (fresh start)
		           7 = keep last week
		           30 = keep last month
	"""
	if not os.path.exists(SEEN_FILE):
		print("No seen articles file found - nothing to reset")
		return
	
	# Count current entries
	with open(SEEN_FILE, 'r') as f:
		total_before = sum(1 for _ in f)
	
	if keep_days == 0:
		# Full reset
		os.remove(SEEN_FILE)
		print(f"✅ Reset complete!")
		print(f"   Removed {total_before} seen articles")
		print(f"   Next run will show ALL articles as new")
	else:
		# Partial reset - keep recent entries
		cutoff = datetime.now() - timedelta(days=keep_days)
		kept = []
		
		with open(SEEN_FILE, 'r') as f:
			for line in f:
				try:
					entry = json.loads(line)
					timestamp = entry.get('timestamp')
					if timestamp:
						entry_date = datetime.fromisoformat(timestamp)
						if entry_date >= cutoff:
							kept.append(line)
				except:
					pass
		
		# Rewrite file
		with open(SEEN_FILE, 'w') as f:
			for line in kept:
				f.write(line)
		
		removed = total_before - len(kept)
		print(f"✅ Partial reset complete!")
		print(f"   Kept {len(kept)} articles from last {keep_days} days")
		print(f"   Removed {removed} older articles")
		print(f"   Next run will show articles older than {keep_days} days as new")


if __name__ == "__main__":
	import argparse
	
	parser = argparse.ArgumentParser(description="Reset seen articles tracker")
	parser.add_argument("--keep-days", type=int, default=0, 
	                    help="Keep articles from last N days (0=full reset, 7=keep week, 30=keep month)")
	args = parser.parse_args()
	
	if args.keep_days == 0:
		confirm = input(f"Reset ALL seen articles? This will show all articles as new on next run. (y/n): ")
		if confirm.lower() != 'y':
			print("Cancelled")
			exit()
	
	reset_seen(args.keep_days)
