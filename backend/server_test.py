from fastapi import FastAPI
from seres_researcher import SeresResearcher
import asyncio

app = FastAPI()

@app.get("/report/{report_type}")
async def get_report(query: str, report_type: str) -> dict:
    researcher = SeresResearcher(query, report_type)
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()
    source_urls = researcher.get_source_urls()
    return {
        "report": report,
        "source_urls": source_urls,
    }

# 运行后端测试:
# uvicorn server_test:app --reload
# 测试后端响应:
# curl -X GET "http://localhost:8000/report/research_report?query=调研新能源汽车行业进展"