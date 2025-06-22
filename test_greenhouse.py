#!/usr/bin/env python3
"""
Test script for Greenhouse scraper
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.greenhouse_scraper import scrape_all_greenhouse_companies

def test_greenhouse_scraper():
    """Test the Greenhouse scraper with a few companies"""
    print("🧪 Testing Greenhouse Scraper")
    print("=" * 40)
    
    # Test with a few well-known companies
    test_companies = [
        'airbnb',      # Airbnb
        'stripe',      # Stripe
        'slack',       # Slack
        'shopify',     # Shopify
        'uber'         # Uber
    ]
    
    print(f"Testing with {len(test_companies)} companies: {', '.join(test_companies)}")
    print()
    
    # Run the scraper
    total_processed = scrape_all_greenhouse_companies(test_companies)
    
    print(f"\n🧪 Test Results:")
    print(f"   Total jobs processed: {total_processed}")
    
    if total_processed > 0:
        print("   ✅ Greenhouse scraper is working!")
    else:
        print("   ⚠️ No jobs found - check company identifiers and filters")

if __name__ == '__main__':
    test_greenhouse_scraper() 