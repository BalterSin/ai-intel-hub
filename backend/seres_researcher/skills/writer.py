from typing import Dict, Optional
import json

from ..utils.llm import construct_subtopics
from ..actions import (
    stream_output,
    generate_report,
    generate_draft_section_titles,
    write_report_introduction,
    write_conclusion
)


class ReportGenerator:
    """根据研究数据生成报告。"""

    def __init__(self, researcher):
        self.researcher = researcher
        self.research_params = {
            "query": self.researcher.query,
            "agent_role_prompt": self.researcher.cfg.agent_role or self.researcher.role,
            "report_type": self.researcher.report_type,
            "report_source": self.researcher.report_source,
            "tone": self.researcher.tone,
            "websocket": self.researcher.websocket,
            "cfg": self.researcher.cfg,
            "headers": self.researcher.headers,
        }

    async def write_report(self, existing_headers: list = [], relevant_written_contents: list = [], ext_context=None, custom_prompt="") -> str:
        """
        根据现有标题和相关内容撰写报告。

        参数:
            existing_headers (list): 现有标题列表。
            relevant_written_contents (list): 相关内容列表。
            ext_context (Optional): 外部上下文（可选）。
            custom_prompt (str): 报告的自定义提示。

        返回:
            str: 生成的报告。
        """
        # 在撰写报告之前发送所选图片
        research_images = self.researcher.get_research_images()
        if research_images:
            await stream_output(
                "images",
                "selected_images",
                json.dumps(research_images),
                self.researcher.websocket,
                True,
                research_images
            )

        context = ext_context or self.researcher.context
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "writing_report",
                f"✍️ 正在为 '{self.researcher.query}' 撰写报告...",
                self.researcher.websocket,
            )

        report_params = self.research_params.copy()
        report_params["context"] = context
        report_params["custom_prompt"] = custom_prompt

        if self.researcher.report_type == "subtopic_report":
            report_params.update({
                "main_topic": self.researcher.parent_query,
                "existing_headers": existing_headers,
                "relevant_written_contents": relevant_written_contents,
                "cost_callback": self.researcher.add_costs,
            })
        else:
            report_params["cost_callback"] = self.researcher.add_costs

        report = await generate_report(**report_params, **self.researcher.kwargs)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "report_written",
                f"📝 已为 '{self.researcher.query}' 撰写完成报告。",
                self.researcher.websocket,
            )

        return report

    async def write_report_conclusion(self, report_content: str) -> str:
        """
        为报告撰写结论。

        参数:
            report_content (str): 报告内容。

        返回:
            str: 生成的结论。
        """
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "writing_conclusion",
                f"✍️ 正在为 '{self.researcher.query}' 撰写结论...",
                self.researcher.websocket,
            )

        conclusion = await write_conclusion(
            query=self.researcher.query,
            context=report_content,
            config=self.researcher.cfg,
            agent_role_prompt=self.researcher.cfg.agent_role or self.researcher.role,
            cost_callback=self.researcher.add_costs,
            websocket=self.researcher.websocket,
            prompt_family=self.researcher.prompt_family,
            **self.researcher.kwargs
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "conclusion_written",
                f"📝 已为 '{self.researcher.query}' 撰写完成结论。",
                self.researcher.websocket,
            )

        return conclusion

    async def write_introduction(self):
        """撰写报告的引言部分。"""
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "writing_introduction",
                f"✍️ 正在为 '{self.researcher.query}' 撰写引言...",
                self.researcher.websocket,
            )

        introduction = await write_report_introduction(
            query=self.researcher.query,
            context=self.researcher.context,
            agent_role_prompt=self.researcher.cfg.agent_role or self.researcher.role,
            config=self.researcher.cfg,
            websocket=self.researcher.websocket,
            cost_callback=self.researcher.add_costs,
            prompt_family=self.researcher.prompt_family,
            **self.researcher.kwargs
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "introduction_written",
                f"📝 已为 '{self.researcher.query}' 撰写完成引言。",
                self.researcher.websocket,
            )

        return introduction

    async def get_subtopics(self):
        """检索研究的子主题。"""
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "generating_subtopics",
                f"🌳 正在为 '{self.researcher.query}' 生成子主题...",
                self.researcher.websocket,
            )

        subtopics = await construct_subtopics(
            task=self.researcher.query,
            data=self.researcher.context,
            config=self.researcher.cfg,
            subtopics=self.researcher.subtopics,
            prompt_family=self.researcher.prompt_family,
            **self.researcher.kwargs
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subtopics_generated",
                f"📊 已为 '{self.researcher.query}' 生成子主题：{subtopics}",
                self.researcher.websocket,
            )

        return subtopics

    async def get_draft_section_titles(self, current_subtopic: str):
        """为报告生成草稿章节标题。"""
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "generating_draft_sections",
                f"📑 正在为 '{self.researcher.query}' 生成草稿章节标题...",
                self.researcher.websocket,
            )

        draft_section_titles = await generate_draft_section_titles(
            query=self.researcher.query,
            current_subtopic=current_subtopic,
            context=self.researcher.context,
            role=self.researcher.cfg.agent_role or self.researcher.role,
            websocket=self.researcher.websocket,
            config=self.researcher.cfg,
            cost_callback=self.researcher.add_costs,
            prompt_family=self.researcher.prompt_family,
            **self.researcher.kwargs
        )

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "draft_sections_generated",
                f"🗂️ 已为 '{self.researcher.query}' 生成草稿章节标题。",
                self.researcher.websocket,
            )

        return draft_section_titles
