"""
Curated list of news sites to monitor for market intelligence.
Organized by relevance and focus area.
"""

# HIGH PRIORITY - Financial Services & Credit Industry
FINANCIAL_SERVICES_SITES = [
	"afr.com.au",  # Australian Financial Review - premium financial news
	"brokernews.com.au",  # Australian Broker - mortgage, lending, credit
	"theadviser.com.au",  # Financial services, lending
	"innovationaus.com",  # Fintech, regtech, startups
]

# REGULATORS - Official announcements
REGULATOR_SITES = [
	"asic.gov.au",  # ASIC - financial services regulator
	"apra.gov.au",  # APRA - banking/super regulator
	"accc.gov.au",  # ACCC - competition & consumer
	"oaic.gov.au",  # Privacy Commissioner
	"austrac.gov.au",  # AML/CTF regulator
	"treasury.gov.au",  # Treasury - policy & legislation
	"rba.gov.au",  # Reserve Bank
]

# TECHNOLOGY & IDENTITY
TECH_SITES = [
	"itnews.com.au",  # Enterprise IT, identity, cybersecurity
	"zdnet.com",  # Tech news (filter for AU content)
	"computerworld.com.au",  # IT & business technology
]

# NEW ZEALAND
NZ_SITES = [
	"stuff.co.nz",  # Major NZ news
	"nzherald.co.nz",  # NZ Herald
	"interest.co.nz",  # Banking, lending, economics
	"nbr.co.nz",  # National Business Review
	"rbnz.govt.nz",  # Reserve Bank NZ
	"fma.govt.nz",  # Financial Markets Authority
	"privacy.org.nz",  # Privacy Commissioner (already in RSS)
]

# INTERNATIONAL (for AU/NZ coverage)
INTERNATIONAL_SITES = [
	"bloomberg.com",  # Filter for Australia/NZ
	"reuters.com",  # Filter for Australia/NZ
	"risk.net",  # Risk management & credit
]

# ALL SITES COMBINED
ALL_MONITORED_SITES = (
	FINANCIAL_SERVICES_SITES +
	REGULATOR_SITES +
	TECH_SITES +
	NZ_SITES +
	INTERNATIONAL_SITES
)

# CATEGORY-SPECIFIC SITE GROUPS
CATEGORY_SITES = {
	"Competition": FINANCIAL_SERVICES_SITES + ["risk.net", "bloomberg.com"],
	"Regulation": REGULATOR_SITES + FINANCIAL_SERVICES_SITES,
	"Disruptive Trends and Technological Advancements": TECH_SITES + FINANCIAL_SERVICES_SITES,
	"Consumer Behaviour and Insights": FINANCIAL_SERVICES_SITES + ["interest.co.nz"],
	"Market Trends": FINANCIAL_SERVICES_SITES + NZ_SITES + ["bloomberg.com", "reuters.com"],
}


