#!/usr/bin/env python3
"""
Debug script to inspect Google Careers page structure
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def debug_google_careers():
    """Debug Google Careers page structure"""
    print("🔍 Debugging Google Careers page structure...")
    
    url = "https://careers.google.com/jobs/results/"
    
    # Setup Selenium
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(url)
            time.sleep(5)
            
            print(f"📄 Page title: {driver.title}")
            
            # Find all elements with div.sMn82b class
            job_elements = driver.find_elements(By.CSS_SELECTOR, "div.sMn82b")
            print(f"🔍 Found {len(job_elements)} job elements with div.sMn82b")
            
            if job_elements:
                # Inspect the first job element
                first_job = job_elements[0]
                print("\n📋 First job element analysis:")
                print(f"   Tag name: {first_job.tag_name}")
                print(f"   Class: {first_job.get_attribute('class')}")
                print(f"   Inner HTML (first 200 chars): {first_job.get_attribute('innerHTML')[:200]}...")
                
                # Look for links within this element
                links_in_job = first_job.find_elements(By.TAG_NAME, "a")
                print(f"   Links found within: {len(links_in_job)}")
                
                for i, link in enumerate(links_in_job[:3]):  # Show first 3 links
                    try:
                        href = link.get_attribute('href')
                        text = link.text
                        print(f"     Link {i+1}: href='{href}', text='{text[:50]}...'")
                    except Exception as e:
                        print(f"     Link {i+1}: Error getting attributes - {e}")
            
            # Try to find any clickable elements
            print("\n🔍 Looking for clickable elements...")
            clickable_selectors = [
                "[role='button']",
                "[onclick]",
                "[data-job-id]",
                "[data-js-action]"
            ]
            
            for selector in clickable_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   Found {len(elements)} elements with {selector}")
                    for i, elem in enumerate(elements[:2]):  # Show first 2
                        try:
                            print(f"     Element {i+1}: {elem.tag_name}, class='{elem.get_attribute('class')}'")
                        except:
                            pass
            
            # Look for any URLs in the page source
            print("\n🔍 Searching for URLs in page source...")
            page_source = driver.page_source
            import re
            
            # Look for Google careers URLs
            google_urls = re.findall(r'https://careers\.google\.com/[^"\s]+', page_source)
            unique_google_urls = list(set(google_urls))
            print(f"   Found {len(unique_google_urls)} unique Google URLs in page source")
            
            for i, url in enumerate(unique_google_urls[:5]):  # Show first 5
                print(f"     URL {i+1}: {url}")
            
            # Look for job-specific patterns
            job_urls = re.findall(r'https://careers\.google\.com/jobs/results/[^"\s]+', page_source)
            unique_job_urls = list(set(job_urls))
            print(f"   Found {len(unique_job_urls)} unique job URLs in page source")
            
            for i, url in enumerate(unique_job_urls[:5]):  # Show first 5
                print(f"     Job URL {i+1}: {url}")
            
            # Save page source for manual inspection
            with open('google_careers_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"\n💾 Saved page source to google_careers_debug.html for manual inspection")
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    debug_google_careers() 