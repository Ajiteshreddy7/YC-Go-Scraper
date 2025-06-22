#
# Job Application Dashboard Generator
# This script fetches data from Supabase and generates a static HTML dashboard.
#

import os
from supabase import create_client, Client
import pandas as pd

def fetch_all_jobs(supabase: Client):
    """Fetches all jobs from the database, ordered by date."""
    try:
        # Select all columns (*), and order by the 'Date Added' column in descending order
        response = supabase.table('job_applications').select('*').order('Date Added', desc=True).execute()
        print(f"Successfully fetched {len(response.data)} jobs.")
        return response.data
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def generate_html_dashboard(jobs: list):
    """Generates an HTML file from a list of job dictionaries."""
    if not jobs:
        print("No jobs to display. Skipping HTML generation.")
        return

    # Convert the list of job dictionaries to a pandas DataFrame for easy HTML conversion
    df = pd.DataFrame(jobs)

    # Simple styling for the table
    html_style = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 40px;
            background-color: #f8f9fa;
            color: #212529;
        }
        h1 {
            color: #343a40;
            text-align: center;
            margin-bottom: 30px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            min-width: 150px;
            margin: 10px;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            color: #6c757d;
            margin-top: 5px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
            box-shadow: 0 2px 3px rgba(0,0,0,0.1);
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            border: 1px solid #dee2e6;
            padding: 12px 15px;
            text-align: left;
        }
        th {
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        tr:hover {
            background-color: #e2e6ea;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .status-not-applied {
            color: #dc3545;
            font-weight: bold;
        }
        .status-applied {
            color: #28a745;
            font-weight: bold;
        }
        .status-interviewed {
            color: #ffc107;
            font-weight: bold;
        }
        .status-offer {
            color: #17a2b8;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
    """

    # Make the URL a clickable link in a new column
    df['Link'] = df['URL'].apply(lambda url: f'<a href="{url}" target="_blank">Apply</a>')

    # Add status styling
    def style_status(status):
        if status == 'Not Applied':
            return f'<span class="status-not-applied">{status}</span>'
        elif status == 'Applied':
            return f'<span class="status-applied">{status}</span>'
        elif 'Interview' in str(status):
            return f'<span class="status-interviewed">{status}</span>'
        elif 'Offer' in str(status):
            return f'<span class="status-offer">{status}</span>'
        else:
            return status

    df['Status'] = df['Status'].apply(style_status)

    # Select and reorder columns for the dashboard
    display_columns = ['Date Added', 'Company', 'Title', 'Location', 'Status', 'Salary', 'Type', 'Link']
    # Filter out columns that might not exist, just in case
    display_columns = [col for col in display_columns if col in df.columns]
    df_display = df[display_columns]

    # Calculate statistics
    total_jobs = len(df)
    not_applied = len(df[df['Status'].str.contains('Not Applied', na=False)])
    applied = len(df[df['Status'].str.contains('Applied', na=False)])
    interviewed = len(df[df['Status'].str.contains('Interview', na=False)])
    
    # Convert DataFrame to HTML
    html_table = df_display.to_html(index=False, escape=False, border=0)

    # Final HTML document structure
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Application Dashboard</title>
        {html_style}
    </head>
    <body>
        <h1>🚀 My Automated Job Application Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_jobs}</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{not_applied}</div>
                <div class="stat-label">Not Applied</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{applied}</div>
                <div class="stat-label">Applied</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{interviewed}</div>
                <div class="stat-label">Interviewed</div>
            </div>
        </div>
        
        {html_table}
        
        <div class="footer">
            <p>🔄 Auto-updated daily | 📊 Powered by Supabase & GitHub Actions</p>
        </div>
    </body>
    </html>
    """

    # Write the content to an index.html file
    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("Successfully generated index.html")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

if __name__ == '__main__':
    # --- Supabase Configuration ---
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Please set SUPABASE_URL and SUPABASE_KEY environment variables.")
            exit()
            
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        exit()

    print("Fetching jobs from Supabase...")
    all_jobs = fetch_all_jobs(supabase)
    generate_html_dashboard(all_jobs) 