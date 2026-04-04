import asyncio
from services.job_service import get_job_service
from schemas.job import JobSearchRequest

async def test():
    service = get_job_service()
    request = JobSearchRequest(role='Developer', skills=['Python'], max_results=30)  # Get all 30
    try:
        result = await service.search_jobs(request)
        print(f'Success: Found {result.total_jobs} jobs')
        
        # Count jobs by source
        source_counts = {}
        for job in result.jobs:
            source = job.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\nJobs by source:")
        for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")
        
        print("\nAll jobs with sources:")
        for i, job in enumerate(result.jobs):
            print(f"  {i+1:2d}. [{job.source:12}] {job.title} at {job.company}")
            if job.location:
                print(f"      Location: {job.location}")
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())