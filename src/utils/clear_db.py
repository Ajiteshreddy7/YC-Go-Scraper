import os
from supabase import create_client

# Clear the database
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
supabase.table('job_applications').delete().neq('id', 0).execute()
print("✅ Database cleared!") 