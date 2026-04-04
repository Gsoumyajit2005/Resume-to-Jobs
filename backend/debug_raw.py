import asyncio
import pandas as pd
from jobspy import scrape_jobs

async def test_raw():
    # Test jobspy directly
    print("Testing jobspy directly...")
    try:
        df = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "google"],
            search_term="Developer Python",
            location=None,  # Important: use actual None, not "None" string
            results_wanted=30,
            hours_old=72,
            country_indeed='usa',
        )
        
        print(f"Raw jobspy results: {len(df)} jobs")
        if not df.empty:
            print("\nColumns:", df.columns.tolist())
            print("\nSource distribution:")
            if 'site' in df.columns:
                source_counts = df['site'].value_counts()
                for source, count in source_counts.items():
                    print(f"  {source}: {count}")
            
            print("\nFirst few jobs:")
            for i, row in df.head(10).iterrows():
                title = row.get('title', 'N/A')
                company = row.get('company', 'N/A')
                site = row.get('site', 'N/A')
                location = row.get('location', 'N/A')
                print(f"  {site:12} | {title} at {company} ({location})")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_raw())