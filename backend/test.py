from seres_researcher import SeresResearcher
import asyncio
import time
import os
from typing import List
from dotenv import load_dotenv
from utils import generate_report_files, sanitize_filename
load_dotenv()

async def write_report(query: str, report_type: str, report_source: str, document_urls: List[str] ):
    os.makedirs("outputs", exist_ok=True)
    researcher = SeresResearcher(query, report_type, report_source = report_source, document_urls = document_urls) 
    research_result = await researcher.conduct_research()
    report = await researcher.write_report()

    research_id = sanitize_filename(f"task_{int(time.time())}_{query}")

    pdf_path, docx_path, md_path = await generate_report_files(report, research_id).values()


    return report, docx_path, pdf_path, md_path

if __name__ == "__main__":
    query = "预测2025-2030年新能源汽车产业发展趋势"
    report_type = "research_report" # report_type = "detailed report"(more detail), "deep"(deep research)
    report_source = "hybrid" #report_source="web","local","hybrid",本地文件存放在my_docs/下
    # ./my_docs/新能源汽车产业发展规划（2021—2035年）- 中华人民共和国国家发展和改革委员会.html
    document_urls = ["https://www.chinairn.com/userfiles/20250516/20250516163010881.pdf"] #2025-2030年新能源汽车产业深度调研-中国产业研究院.pdf
    #document_urls: 指定网络上的文档加入知识库 支持后缀：["pdf", "txt", "doc", "docx", "pptx", "csv", "xls", "xlsx", "md"]

    report, docx_path, pdf_path, md_path = asyncio.run(write_report(query, report_type, report_source, document_urls))
    
    print("Report:")
    print(report)
    print("\nPDF Path:")
    print(pdf_path)
    print("\nDocx Path:")
    print(docx_path)
    print("\nMarkdown Path:")
    print(md_path)