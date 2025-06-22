#
# Universal Job Application Tracker - v2.0
# This script uses Google's Gemini AI to extract job details from any URL
# and saves them to a CSV file.
#

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import google.generativeai as genai
import json
import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- CONFIGURATION ---
# The name of the CSV file where we'll store the job data.
CSV_FILE = 'job_applications.csv'

# IMPORTANT: Set up your API Key
# 1. Get your key from https://aistudio.google.com/app/apikey
# 2. In your terminal, set the environment variable:
#    For Mac/Linux: export GOOGLE_API_KEY='YOUR_API_KEY'
#    For Windows: set GOOGLE_API_KEY='YOUR_API_KEY'
# 3. The script will read the key from the environment.
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("="*50)
    print("ERROR: GOOGLE_API_KEY environment variable not found.")
    print("Please set the environment variable with your API key.")
    print("="*50)
    exit()


def get_page_text(url):
    """
    Fetches comprehensive text content from a URL using Selenium for JavaScript-rendered content.
    Handles modern websites that load job descriptions dynamically.
    
    Args:
        url (str): The URL to fetch.
        
    Returns:
        str: The comprehensive text content of the page, or None if it fails.
    """
    try:
        print("Setting up browser for JavaScript-rendered content...")
        
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize the browser
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to the URL
            print(f"Loading page: {url}")
            driver.get(url)
            
            # Wait for the page to load (wait for body to be present)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for JavaScript content to load
            time.sleep(3)
            
            # Try to find job description content
            job_content_selectors = [
                '[class*="job-description"]',
                '[class*="job-details"]',
                '[class*="position-description"]',
                '[class*="role-description"]',
                '[class*="career-description"]',
                'main',
                'article',
                '[role="main"]',
                '.content',
                '#content',
                '.job-content',
                '.position-content',
                '.description',
                '[class*="description"]'
            ]
            
            job_content = None
            for selector in job_content_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if len(text) > 500:  # Look for substantial content
                            job_content = element
                            print(f"Found job content using selector: {selector}")
                            break
                    if job_content:
                        break
                except:
                    continue
            
            # If no specific content found, get the entire page
            if job_content:
                text_content = job_content.text
            else:
                print("No specific job content found, extracting entire page")
                text_content = driver.find_element(By.TAG_NAME, "body").text
            
            # Clean up the text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            print(f"Using Selenium extraction (extracted {len(cleaned_text)} characters)")
            return cleaned_text
            
        finally:
            # Always close the browser
            driver.quit()
        
    except Exception as e:
        print(f"An error occurred during Selenium extraction: {e}")
        print("Falling back to simple HTTP request...")
        
        # Fallback to simple HTTP request
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            print(f"Using fallback HTTP extraction (extracted {len(cleaned_text)} characters)")
            return cleaned_text
            
        except Exception as fallback_error:
            print(f"Fallback extraction also failed: {fallback_error}")
            return None

def extract_details_with_gemini(text_content, url):
    """
    Uses Gemini AI with a sophisticated prompt to extract job details from comprehensive text content.
    The prompt is designed to handle noisy content and find details even when scattered throughout the page.

    Args:
        text_content (str): The text scraped from the job posting page.
        url (str): The original URL for tracking purposes.

    Returns:
        dict: A dictionary with the extracted job details, or None.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Debug: Show what content we're working with
    print(f"\nDEBUG: Content length: {len(text_content)} characters")
    print(f"DEBUG: First 500 characters: {text_content[:500]}...")
    print(f"DEBUG: Looking for salary patterns in content...")
    
    # Check if salary-related content exists in the text
    salary_keywords = ['salary', 'pay', 'compensation', '$', 'dollar', 'hourly', 'annual', 'monthly']
    found_salary_content = [keyword for keyword in salary_keywords if keyword.lower() in text_content.lower()]
    if found_salary_content:
        print(f"DEBUG: Found salary-related keywords: {found_salary_content}")
    else:
        print("DEBUG: No salary-related keywords found in content")
    
    # Check if job type content exists
    job_type_keywords = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'freelance']
    found_job_type_content = [keyword for keyword in job_type_keywords if keyword.lower() in text_content.lower()]
    if found_job_type_content:
        print(f"DEBUG: Found job type keywords: {found_job_type_content}")
    else:
        print("DEBUG: No job type keywords found in content")
    
    # --- Sophisticated prompt designed for noisy content ---
    prompt = f"""
    You are an expert job data extraction specialist. Your task is to analyze the following text from a job posting webpage and extract key details.

    CRITICAL INSTRUCTIONS:
    1. This text contains ALL content from the webpage including navigation, headers, footers, sidebars, and main content
    2. Job details can be ANYWHERE in this text - not just in the main description
    3. You must be extremely thorough and check every section, line, and word
    4. Look for patterns, keywords, and contextual clues throughout the entire text

    EXTRACTION STRATEGY:
    - Job Title: Look for the most prominent job title (often in headers, titles, or near the top)
    - Company Name: Search for company names in headers, footers, "About" sections, or near the job title
    - Location: Check for location info in headers, requirements, company info, or job details
    - Salary: Search for ANY mention of money, compensation, pay, salary, hourly rate, or benefits
    - Job Type: Look for employment type indicators like "Full-time", "Part-time", "Contract", etc.

    SALARY DETECTION PATTERNS (search for these):
    - Dollar amounts: $X, $X-$Y, $X to $Y, $X/Y, $X per hour
    - Words: salary, compensation, pay, hourly, annual, monthly, wage
    - Phrases: "competitive salary", "salary range", "compensation package"
    - Benefits: "benefits include", "package includes", "total compensation"

    JOB TYPE DETECTION PATTERNS (search for these):
    - Full-time, Part-time, Contract, Temporary, Internship, Freelance
    - "Employment type:", "Job type:", "Position type:"
    - "40 hours per week", "flexible hours", "remote work"

    Return ONLY a valid JSON object with these exact keys:
    {{
        "job_title": "the job title found",
        "company_name": "the company name found", 
        "location": "location information found",
        "salary_range": "salary/compensation information found (or null if none)",
        "job_type": "employment type found (or null if none)"
    }}

    IMPORTANT: 
    - If you find multiple instances of the same information, use the most prominent/relevant one
    - If information is truly not present, use null (not empty string)
    - Be very thorough - this text contains ALL page content including navigation and footers
    - Look in every section, header, footer, and sidebar for these details

    Text to analyze:
    ---
    {text_content}
    ---
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Debug: Show AI response
        print(f"DEBUG: AI Response: {response.text}")
        
        # Clean up the response to extract only the JSON part
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Handle cases where the AI might return multiple JSON objects or extra text
        if json_text.startswith('{') and json_text.endswith('}'):
            details = json.loads(json_text)
        else:
            # Try to find JSON within the response
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_text = json_text[start_idx:end_idx]
                details = json.loads(json_text)
            else:
                raise ValueError("No valid JSON found in response")
        
        job_details = {
            'Title': details.get('job_title'),
            'Company': details.get('company_name'),
            'Location': details.get('location'),
            'Salary': details.get('salary_range'),
            'Type': details.get('job_type'),
            'URL': url,
            'Status': 'Not Applied',
            'Date Added': pd.to_datetime('today').strftime('%Y-%m-%d')
        }
        return job_details

    except Exception as e:
        print(f"\nAn error occurred with the Gemini API or JSON parsing.")
        print(f"Error details: {e}")
        if 'response' in locals():
            print(f"Raw AI Response:\n{response.text[:500]}...")
        return None


def save_to_csv(job_details):
    """
    Saves the job details dictionary to a CSV file.
    """
    # Define the order of columns for the CSV
    columns = ['Date Added', 'Company', 'Title', 'Location', 'Salary', 'Type', 'Status', 'URL']
    df = pd.DataFrame([job_details])
    df = df[columns] # Ensure columns are in the correct order

    if not os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, index=False, mode='w')
        print(f"\nSuccess! '{CSV_FILE}' created and job details saved.")
    else:
        df.to_csv(CSV_FILE, index=False, mode='a', header=False)
        print(f"\nSuccess! Job details appended to '{CSV_FILE}'.")


def main():
    """Main function to run the universal job tracker."""
    print("--- Universal AI Job Tracker (v2.0) ---")
    
    while True:
        url = input("\nEnter a job URL from any website (or type 'exit' to quit): ")
        
        if url.lower() == 'exit':
            break
        
        if not url.startswith(('http://', 'https://')):
            print("Please enter a valid URL (e.g., https://...)")
            continue
            
        print("\nStep 1: Fetching page content...")
        page_text = get_page_text(url)
        
        if page_text:
            print("Step 2: Asking Gemini AI to extract details...")
            job_details = extract_details_with_gemini(page_text, url)
            
            if job_details:
                print("Step 3: Saving to your spreadsheet...")
                save_to_csv(job_details)

    print("\nHappy job hunting!")


if __name__ == '__main__':
    main() 