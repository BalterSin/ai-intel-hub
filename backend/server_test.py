from fastapi import FastAPI
from seres_researcher import SeresResearcher
import asyncio
from utils import generate_report_files, sanitize_filename
import time
import urllib
import os
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Seres Researcher"}

@app.get("/report/{report_type}")
async def write_report(query: str, report_type: str, report_format:str, report_source:str):
    os.makedirs("outputs", exist_ok=True)

    researcher = SeresResearcher(query, report_type, report_format=report_format, report_source = report_source) 
    __  = await researcher.conduct_research()
    report = await researcher.write_report()

    """researcher = DetailedReport(query, report_type, report_source = report_source)
    report = await researcher.run()"""

    research_id = sanitize_filename(f"task_{int(time.time())}_{query}")

    res = await generate_report_files(report, research_id)
    pdf_path, docx_path, md_path = [urllib.parse.unquote(i) for i in res.values()]

    return {
        "report": report,
        "docx_path": docx_path,
        "pdf_path": pdf_path,
        "md_path": md_path
    }

# 运行后端测试:
# uvicorn server_test:app --reload
# 测试后端响应:
# curl -X GET "http://localhost:8000/report/research_report?query=调研新能源汽车行业进展?report_format=ieee?report_source=web"