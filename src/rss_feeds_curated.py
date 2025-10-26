"""
Curated RSS feeds - WORKING feeds only, filtered by relevance.
Updated based on testing.
"""

# WORKING FEEDS with high relevance
RSS_FEEDS_WORKING = [
	# Privacy & Data Protection
	"https://www.privacy.org.nz/blog/rss/",  # NZ Privacy Commissioner - GOOD
	
	# NOTE: Beehive.govt.nz is too broad - includes health, sports, etc.
	# We need to find category-specific feeds or use GNews/web scraping instead
]

# FEEDS TO TEST (may work with different date ranges)
RSS_FEEDS_TO_TEST = [
	"https://asic.gov.au/about-asic/news-centre/rss-feeds/",
	"https://www.apra.gov.au/news-and-publications",
	"https://www.accc.gov.au/media-releases",
	"https://www.oaic.gov.au/newsroom",
]

# BROKEN/EMPTY FEEDS (documented for reference)
RSS_FEEDS_BROKEN = [
	"https://asic.gov.au/rss?feed=media-releases",  # Returns 0 entries
	"https://www.accc.gov.au/rss/media-releases.xml",  # 404 error
	"https://www.oaic.gov.au/rss/news",  # 404 error
	"https://www.apra.gov.au/media-releases/rss",  # 404 error
	"https://www.beehive.govt.nz/rss.xml",  # Too broad - general government news
]

# Use only working feeds by default
RSS_FEEDS = RSS_FEEDS_WORKING


