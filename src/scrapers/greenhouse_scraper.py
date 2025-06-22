#!/usr/bin/env python3
"""
Greenhouse Platform Scraper
Scrapes jobs from companies using the Greenhouse platform with intelligent filtering.
"""

import requests
import re
import time
from typing import List, Dict
import os
from supabase import create_client, Client

# Keywords to identify early-career roles
EARLY_CAREER_KEYWORDS = [
    'intern', 'internship', 'new grad', 'new graduate', 'associate', 'junior',
    'entry level', 'entry-level', 'rotational', 'co-op', 'fellow', 'apprentice'
]

# Keywords to identify senior roles to exclude
SENIOR_ROLE_KEYWORDS = [
    'senior', 'sr.', 'lead', 'staff', 'principal', 'manager', 'director',
    'architect', 'vp', 'head of', 'chief', 'executive'
]

def is_early_career(title: str) -> bool:
    """Checks if a job title indicates an early-career role."""
    lower_title = title.lower()
    
    # Exclude if it's explicitly a senior role
    if any(keyword in lower_title for keyword in SENIOR_ROLE_KEYWORDS):
        return False
    
    # Include if it contains early-career keywords
    if any(keyword in lower_title for keyword in EARLY_CAREER_KEYWORDS):
        return True
    
    # Include if it has a number from 1-3 (I, II, III, 1, 2, 3)
    if re.search(r'\b(i|ii|iii|1|2|3)\b', lower_title):
        return True
    
    # Include if it's a basic engineering/tech role without senior indicators
    basic_roles = ['engineer', 'developer', 'analyst', 'specialist', 'coordinator']
    if any(role in lower_title for role in basic_roles):
        # But exclude if it has years of experience requirements
        if re.search(r'\b(5|6|7|8|9|10)\+?\s*(years?|yrs?)\b', lower_title):
            return False
        return True
    
    return False

def is_in_usa(location: str) -> bool:
    """Checks if a job location is in the USA or Remote."""
    if not location:
        return False
        
    lower_loc = location.lower()
    
    # USA identifiers
    usa_identifiers = [
        'united states', 'usa', 'us', 'remote', 'united states of america',
        'new york', 'san francisco', 'seattle', 'austin', 'boston', 'chicago',
        'los angeles', 'atlanta', 'dallas', 'houston', 'miami', 'denver',
        'phoenix', 'philadelphia', 'washington', 'dc', 'nashville', 'portland',
        'san diego', 'minneapolis', 'detroit', 'cleveland', 'pittsburgh',
        'charlotte', 'raleigh', 'orlando', 'tampa', 'jacksonville', 'columbus'
    ]
    
    return any(identifier in lower_loc for identifier in usa_identifiers)

def check_if_job_exists(url: str) -> bool:
    """Check if a job URL already exists in the database."""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase: Client = create_client(supabase_url, supabase_key)
        response = supabase.table('job_applications').select('URL').eq('URL', url).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"❌ Error checking if job exists: {e}")
        return False

def save_to_supabase(job_details: Dict) -> bool:
    """Save job details to Supabase database."""
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("❌ Missing Supabase credentials")
            return False
            
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Add timestamp
        import pandas as pd
        job_details['Date Added'] = pd.to_datetime('today').strftime('%Y-%m-%d %H:%M:%S')
        
        data, count = supabase.table('job_applications').insert(job_details).execute()
        print(f"✅ Saved: {job_details.get('Title', 'Unknown')} at {job_details.get('Company', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error saving job: {e}")
        return False

def scrape_greenhouse_jobs(company_name: str) -> List[Dict]:
    """
    Scrapes jobs from a company's Greenhouse board API.

    Args:
        company_name (str): The company's identifier for Greenhouse (e.g., 'airbnb').

    Returns:
        A list of dictionaries, where each dictionary is a filtered job posting.
    """
    print(f"🔍 Scraping Greenhouse for: {company_name}")
    filtered_jobs = []
    
    # The URL for Greenhouse's job board API
    api_url = f"https://api.greenhouse.io/v1/boards/{company_name}/jobs?content=true"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        jobs = response.json().get('jobs', [])
        
        print(f"   Found {len(jobs)} total jobs. Applying filters...")

        for job in jobs:
            title = job.get('title', '')
            location = job.get('location', {}).get('name', 'N/A')
            
            # Apply our filtering logic
            if is_early_career(title) and is_in_usa(location):
                filtered_job = {
                    "title": title,
                    "location": location,
                    "url": job.get('absolute_url', ''),
                    "company": company_name.capitalize(),
                    "department": job.get('department', {}).get('name', ''),
                    "job_type": job.get('metadata', [{}])[0].get('value', '') if job.get('metadata') else '',
                    "updated_at": job.get('updated_at', '')
                }
                filtered_jobs.append(filtered_job)
                print(f"   ✅ {title} - {location}")
        
        print(f"   📊 Found {len(filtered_jobs)} filtered early-career jobs in the USA.")
        return filtered_jobs

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error fetching jobs for {company_name}: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Unexpected error for {company_name}: {e}")
        return []

def process_greenhouse_jobs(jobs: List[Dict]) -> int:
    """
    Processes a list of job dictionaries and saves them to the database.
    
    Returns:
        int: Number of jobs successfully processed
    """
    processed_count = 0
    
    for job in jobs:
        url = job.get("url")
        if not url:
            continue

        print(f"   Processing: {job.get('title')} at {job.get('company')}")

        if check_if_job_exists(url):
            print("   ⏭️ Job already exists in database. Skipping.")
            continue
        
        # Prepare database payload
        db_payload = {
            'Title': job.get('title'),
            'Company': job.get('company'),
            'Location': job.get('location'),
            'URL': url,
            'Type': job.get('job_type', ''),
            'Status': 'Not Applied'
        }
        
        if save_to_supabase(db_payload):
            processed_count += 1
        
        time.sleep(1)  # Be respectful between jobs
    
    return processed_count

def scrape_all_greenhouse_companies(companies: List[str]) -> int:
    """
    Scrapes jobs from all Greenhouse companies in the list.
    
    Args:
        companies (List[str]): List of company identifiers for Greenhouse
        
    Returns:
        int: Total number of jobs processed
    """
    total_processed = 0
    
    print(f"🏢 Starting Greenhouse scraping for {len(companies)} companies...")
    print("=" * 60)
    
    for i, company in enumerate(companies, 1):
        print(f"\n[{i}/{len(companies)}] Processing {company}...")
        
        jobs = scrape_greenhouse_jobs(company)
        if jobs:
            processed = process_greenhouse_jobs(jobs)
            total_processed += processed
            print(f"   📈 Processed {processed} new jobs from {company}")
        else:
            print(f"   ⚠️ No matching jobs found for {company}")
        
        # Be respectful between companies
        if i < len(companies):
            print("   ⏳ Waiting 3 seconds before next company...")
            time.sleep(3)
    
    print(f"\n🎉 Greenhouse scraping complete!")
    print(f"📊 Total jobs processed: {total_processed}")
    
    return total_processed

if __name__ == '__main__':
    # Test with a few companies
    test_companies = ['airbnb', 'stripe', 'slack']
    scrape_all_greenhouse_companies(test_companies) 