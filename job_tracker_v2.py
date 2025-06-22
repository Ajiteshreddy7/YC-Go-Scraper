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
    Fetches the main readable text content from a URL.
    
    Args:
        url (str): The URL to fetch.
        
    Returns:
        str: The cleaned text content of the page, or None if it fails.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Use BeautifulSoup to parse the HTML and extract all human-readable text.
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
            
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return cleaned_text
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def extract_details_with_gemini(text_content, url):
    """
    Uses Gemini AI to extract job details from text content.

    Args:
        text_content (str): The text scraped from the job posting page.
        url (str): The original URL for tracking purposes.

    Returns:
        dict: A dictionary with the extracted job details, or None.
    """
    # Create the generative model
    model = genai.GenerativeModel('gemini-pro')
    
    # This is our instruction to the AI. We're telling it how to behave
    # and what format to return the data in. This is called "Prompt Engineering".
    prompt = f"""
    You are an expert data extraction assistant. Your task is to analyze the following text from a job posting website and extract the key details.

    Return the information in a clean JSON format with the following keys:
    - "job_title"
    - "company_name"
    - "location" (e.g., "City, State" or "Remote")
    - "salary_range" (if mentioned, otherwise return null)
    - "job_type" (e.g., "Full-time", "Contract", if mentioned, otherwise null)

    Here is the text to analyze:
    ---
    {text_content[:8000]} 
    ---
    """
    
    try:
        # Ask Gemini to generate the content based on our prompt
        response = model.generate_content(prompt)
        
        # Clean up the response to extract only the JSON part
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Convert the JSON string into a Python dictionary
        details = json.loads(json_text)
        
        # Add the tracking fields
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
        print(f"An error occurred with the Gemini API or JSON parsing: {e}")
        print("Raw AI Response:\n", response.text)
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