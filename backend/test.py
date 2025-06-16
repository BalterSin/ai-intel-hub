from seres_researcher import SeresResearcher
import asyncio
from dotenv import load_dotenv
load_dotenv()
async def get_report(query: str, report_type: str):
    researcher = SeresResearcher(query, report_type, report_source="hybrid") #report_source="web","local","hybrid",本地文件存放在my_docs/下
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    
    # Get additional information
    research_context = researcher.get_research_context()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()
    return report, research_context, research_images, research_sources

if __name__ == "__main__":
    query = "调研新能源汽车最新进展"
    report_type = "research_report" # report_type = "detailed report"(more detail), "deep"(deep research)

    report, context, images, sources = asyncio.run(get_report(query, report_type))
    
    print("Report:")
    print(report)
    print("\nNumber of Research Images:")
    print(len(images))
    print("\nNumber of Research Sources:")
    print(len(sources))