import urllib.parse
from seres_researcher import SeresResearcher
from report_type.detailed_report.detailed_report import DetailedReport
import asyncio
import time
import os
import urllib
from typing import List
from dotenv import load_dotenv
from utils import generate_report_files, sanitize_filename
load_dotenv()

async def write_report(query: str, report_type: str, report_source: str ):
    os.makedirs("outputs", exist_ok=True)

    researcher = SeresResearcher(query, report_type, report_format="ieee", report_source = report_source) 
    __  = await researcher.conduct_research()
    report = await researcher.write_report()

    """researcher = DetailedReport(query, report_type, report_source = report_source)
    report = await researcher.run()"""

    research_id = sanitize_filename(f"task_{int(time.time())}_{query}")

    res = await generate_report_files(report, research_id)
    pdf_path, docx_path, md_path = [urllib.parse.unquote(i) for i in res.values()]

    return report, docx_path, pdf_path, md_path

if __name__ == "__main__":
    query = "调研2025华为HDC大会内容, 生成一份详细的调研报告, 不少于3000字"
    report_type = "research_report" # report_type = "detailed report"(more detail), "deep"(deep research)
    report_source = "web" #report_source="web","local","hybrid", 本地文档存放在my_docs/下
    # 本地文档./my_docs/2025-2030年新能源汽车产业深度调研及未来发展现状趋势预测报告-中国产业研究院.PDF
  
    report, docx_path, pdf_path, md_path = asyncio.run(write_report(query, report_type, report_source))
    
    print("Report:")
    print(report)
    print("\nPDF Path:")
    print(pdf_path)
    print("\nDocx Path:")
    print(docx_path)
    print("\nMarkdown Path:")
    print(md_path)