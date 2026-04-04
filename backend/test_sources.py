import asyncio
from services.job_service import get_job_service
from schemas.job import JobSearchRequest

async def test():
    service = get_job_service()
    request = JobSearchRequest(role='Developer', skills=['Python'], max_results=20)  # Increased to see more jobs
    try:
        result = await service.search_jobs(request)
        print(f'Success: Found {result.total_jobs} jobs')
        
        # Count jobs by source
        source_counts = {}
        for job in result.jobs:
            source = job.source
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("\nJobs by source:")
        for source, count in source_counts.items():
            print(f"  {source}: {count}")
        
        print("\nFirst 10 jobs:")
        for i, job in enumerate(result.jobs[:10]):
            print(f"  {i+1}. {job.title} at {job.company}")
            print(f"      Source: {job.source}, Location: {job.location}")
            if job.salary_range:
                print(f"      Salary: {job.salary_range}")
            print()
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())