import asyncio
import random
import logging
import os
from ..actions.utils import stream_output
from ..actions.query_processing import plan_research_outline, get_search_results
from ..document import DocumentLoader, OnlineDocumentLoader, LangChainDocumentLoader
from ..utils.enum import ReportSource
from ..utils.logging_config import get_json_handler


class ResearchConductor:
    """管理并协调研究过程。"""

    def __init__(self, researcher):
        self.researcher = researcher
        self.logger = logging.getLogger('research')
        self.json_handler = get_json_handler()

    async def plan_research(self, query, query_domains=None):
        self.logger.info(f"为以下Query规划研究：{query}")
        if query_domains:
            self.logger.info(f"Query领域：{query_domains}")
        
        await stream_output(
            "logs",
            "planning_research",
            f"🌐 浏览网络以了解更多关于任务的信息：{query}...",
            self.researcher.websocket,
        )

        search_results = await get_search_results(query, self.researcher.retrievers[0], query_domains)
        self.logger.info(f"初始搜索结果已获得：{len(search_results)} 条结果")

        await stream_output(
            "logs",
            "planning_research",
            f"🤔 制定研究计划和任务拆解...",
            self.researcher.websocket,
        )

        outline = await plan_research_outline(
            query=query,
            search_results=search_results,
            agent_role_prompt=self.researcher.role,
            cfg=self.researcher.cfg,
            parent_query=self.researcher.parent_query,
            report_type=self.researcher.report_type,
            cost_callback=self.researcher.add_costs,
            **self.researcher.kwargs
        )
        self.logger.info(f"研究大纲已规划：{outline}")
        return outline

    async def conduct_research(self):
        """运行 Seres 研究者进行研究"""
        if self.json_handler:
            self.json_handler.update_content("query", self.researcher.query)
        
        self.logger.info(f"开始对以下Query进行研究：{self.researcher.query}")
        
        # 每次研究任务开始时重置 visited_urls 和 source_urls
        self.researcher.visited_urls.clear()
        research_data = []

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "starting_research",
                f"🔍 开始对 '{self.researcher.query}' 进行研究任务...",
                self.researcher.websocket,
            )
            await stream_output(
                "logs",
                "agent_generated",
                self.researcher.agent,
                self.researcher.websocket
            )

        # 根据以下源类型研究相关信息
        if self.researcher.source_urls:
            self.logger.info("使用提供的源URL")
            research_data = await self._get_context_by_urls(self.researcher.source_urls)
            if research_data and len(research_data) == 0 and self.researcher.verbose:
                await stream_output(
                    "logs",
                    "answering_from_memory",
                    f"🧐 在提供的资源中找不到相关内容...",
                    self.researcher.websocket,
                )
            if self.researcher.complement_source_urls:
                self.logger.info("通过网络搜索补充")
                additional_research = await self._get_context_by_web_search(self.researcher.query, [], self.researcher.query_domains)
                research_data += ' '.join(additional_research)

        elif self.researcher.report_source == ReportSource.Web.value:
            self.logger.info("使用网络搜索")
            research_data = await self._get_context_by_web_search(self.researcher.query, [], self.researcher.query_domains)

        elif self.researcher.report_source == ReportSource.Local.value:
            self.logger.info("使用本地搜索")
            document_data = await DocumentLoader(self.researcher.cfg.doc_path).load()
            self.logger.info(f"已加载 {len(document_data)} 份文档")
            if self.researcher.vector_store:
                self.researcher.vector_store.load(document_data)

            research_data = await self._get_context_by_web_search(self.researcher.query, document_data, self.researcher.query_domains)

        # 混合搜索，包括本地文档和网络资源
        elif self.researcher.report_source == ReportSource.Hybrid.value:
            if self.researcher.document_urls:
                document_data = await OnlineDocumentLoader(self.researcher.document_urls).load()
            else:
                document_data = await DocumentLoader(self.researcher.cfg.doc_path).load()
            if self.researcher.vector_store:
                self.researcher.vector_store.load(document_data)
            docs_context = await self._get_context_by_web_search(self.researcher.query, document_data, self.researcher.query_domains)
            web_context = await self._get_context_by_web_search(self.researcher.query, [], self.researcher.query_domains)
            research_data = self.researcher.prompt_family.join_local_web_documents(docs_context, web_context)

            
        elif self.researcher.report_source == ReportSource.LangChainDocuments.value:
            langchain_documents_data = await LangChainDocumentLoader(
                self.researcher.documents
            ).load()
            if self.researcher.vector_store:
                self.researcher.vector_store.load(langchain_documents_data)
            research_data = await self._get_context_by_web_search(
                self.researcher.query, langchain_documents_data, self.researcher.query_domains
            )

        elif self.researcher.report_source == ReportSource.LangChainVectorStore.value:
            research_data = await self._get_context_by_vectorstore(self.researcher.query, self.researcher.vector_store_filter)

        # 对来源进行排序和整理
        self.researcher.context = research_data
        if self.researcher.cfg.curate_sources:
            self.logger.info("整理来源")
            self.researcher.context = await self.researcher.source_curator.curate_sources(research_data)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "research_step_finalized",
                f"研究步骤已完成。\n💸 总研究成本：${self.researcher.get_costs()}",
                self.researcher.websocket,
            )
            if self.json_handler:
                self.json_handler.update_content("costs", self.researcher.get_costs())
                self.json_handler.update_content("context", self.researcher.context)

        self.logger.info(f"研究已完成。上下文大小：{len(str(self.researcher.context))}")
        return self.researcher.context

    async def _get_context_by_urls(self, urls):
        """从给定的URL中抓取并压缩上下文"""
        self.logger.info(f"从以下URL获取上下文：{urls}")
        
        new_search_urls = await self._get_new_urls(urls)
        self.logger.info(f"需要处理的新URL：{new_search_urls}")

        scraped_content = await self.researcher.scraper_manager.browse_urls(new_search_urls)
        self.logger.info(f"已从 {len(scraped_content)} 个URL中抓取内容")

        if self.researcher.vector_store:
            self.logger.info("将内容加载到VectorStore中")
            self.researcher.vector_store.load(scraped_content)

        context = await self.researcher.context_manager.get_similar_content_by_query(
            self.researcher.query, scraped_content
        )
        return context

    # 其他方法同样添加日志...

    async def _get_context_by_vectorstore(self, query, filter: dict | None = None):
        """
        通过搜索VectorStore生成研究任务的上下文
        返回：
            context: 上下文列表
        """
        self.logger.info(f"开始VectorStore搜索，Query：{query}")
        context = []
        # 生成子查询，包括原始Query
        sub_queries = await self.plan_research(query)
        # 如果这不是子研究者的一部分，添加原始Query以获得更好的结果
        if self.researcher.report_type != "subtopic_report":
            sub_queries.append(query)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subqueries",
                f"🗂️ 我将基于以下Query进行研究：{sub_queries}...",
                self.researcher.websocket,
                True,
                sub_queries,
            )

        # 使用asyncio.gather异步处理子查询
        context = await asyncio.gather(
            *[
                self._process_sub_query_with_vectorstore(sub_query, filter)
                for sub_query in sub_queries
            ]
        )
        return context

    async def _get_context_by_web_search(self, query, scraped_data: list | None = None, query_domains: list | None = None):
        """
        通过搜索Query并抓取结果生成研究任务的上下文
        返回：
            context: 上下文列表
        """
        self.logger.info(f"开始网络搜索，Query：{query}")
        
        if scraped_data is None:
            scraped_data = []
        if query_domains is None:
            query_domains = []

        # 生成子查询，包括原始Query
        sub_queries = await self.plan_research(query, query_domains)
        self.logger.info(f"生成的子查询：{sub_queries}")
        
        # 如果这不是子研究者的一部分，添加原始Query以获得更好的结果
        if self.researcher.report_type != "subtopic_report":
            sub_queries.append(query)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "subqueries",
                f"🗂️ 我将基于以下Query进行研究：{sub_queries}...",
                self.researcher.websocket,
                True,
                sub_queries,
            )

        # 使用asyncio.gather异步处理子查询
        try:
            context = await asyncio.gather(
                *[
                    self._process_sub_query(sub_query, scraped_data, query_domains)
                    for sub_query in sub_queries
                ]
            )
            self.logger.info(f"已从 {len(context)} 个子查询中获取上下文")
            # 过滤空结果并合并上下文
            context = [c for c in context if c]
            if context:
                combined_context = " ".join(context)
                self.logger.info(f"合并后上下文大小：{len(combined_context)}")
                return combined_context
            return []
        except Exception as e:
            self.logger.error(f"网络搜索期间发生错误：{e}", exc_info=True)
            return []

    async def _process_sub_query(self, sub_query: str, scraped_data: list = [], query_domains: list = []):
        """接收一个子查询并根据它抓取URL并收集上下文。"""
        if self.json_handler:
            self.json_handler.log_event("sub_query", {
                "query": sub_query,
                "scraped_data_size": len(scraped_data)
            })
        
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "running_subquery_research",
                f"\n🔍 正在对 '{sub_query}' 进行研究...",
                self.researcher.websocket,
            )

        try:
            if not scraped_data:
                scraped_data = await self._scrape_data_by_urls(sub_query, query_domains)
                self.logger.info(f"抓取数据大小：{len(scraped_data)}")

            content = await self.researcher.context_manager.get_similar_content_by_query(sub_query, scraped_data)
            self.logger.info(f"子查询找到的内容大小：{len(str(content)) if content else 0} 字符")

            if not content and self.researcher.verbose:
                await stream_output(
                    "logs",
                    "subquery_context_not_found",
                    f"🤷 没有找到 '{sub_query}' 的相关内容...",
                    self.researcher.websocket,
                )
            if content:
                if self.json_handler:
                    self.json_handler.log_event("content_found", {
                        "sub_query": sub_query,
                        "content_size": len(content)
                    })
            return content
        except Exception as e:
            self.logger.error(f"处理子查询 {sub_query} 时发生错误：{e}", exc_info=True)
            return ""

    async def _process_sub_query_with_vectorstore(self, sub_query: str, filter: dict | None = None):
        """接收一个子查询并从用户提供的VectorStore中收集上下文

        参数：
            sub_query (str): 从原始Query生成的子查询

        返回：
            str: 从搜索中获得的上下文
        """
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "running_subquery_with_vectorstore_research",
                f"\n🔍 正在对 '{sub_query}' 进行研究...",
                self.researcher.websocket,
            )

        context = await self.researcher.context_manager.get_similar_content_by_query_with_vectorstore(sub_query, filter)

        return context

    async def _get_new_urls(self, url_set_input):
        """从给定的URL集合中获取新URL。
        参数：url_set_input (set[str])：从中获取新URL的URL集合
        返回：list[str]：给定URL集合中的新URL
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.researcher.visited_urls:
                self.researcher.visited_urls.add(url)
                new_urls.append(url)
                if self.researcher.verbose:
                    await stream_output(
                        "logs",
                        "added_source_url",
                        f"✅ 已将源URL添加到研究：{url}\n",
                        self.researcher.websocket,
                        True,
                        url,
                    )

        return new_urls

    async def _search_relevant_source_urls(self, query, query_domains: list | None = None):
        new_search_urls = []
        if query_domains is None:
            query_domains = []

        # 遍历所有检索器
        for retriever_class in self.researcher.retrievers:
            # 使用子查询实例化检索器
            retriever = retriever_class(query, query_domains=query_domains)

            # 使用当前检索器执行搜索
            search_results = await asyncio.to_thread(
                retriever.search, max_results=self.researcher.cfg.max_search_results_per_query
            )

            # 从搜索结果中收集新URL
            search_urls = [url.get("href") for url in search_results]
            new_search_urls.extend(search_urls)

        # 获取唯一URL
        new_search_urls = await self._get_new_urls(new_search_urls)
        random.shuffle(new_search_urls)

        return new_search_urls

    async def _scrape_data_by_urls(self, sub_query, query_domains: list | None = None):
        """
        在多个检索器上运行子查询并抓取生成的URL。

        参数：
            sub_query (str)：要搜索的子查询。

        返回：
            list：抓取内容结果的列表。
        """
        if query_domains is None:
            query_domains = []

        new_search_urls = await self._search_relevant_source_urls(sub_query, query_domains)

        # 如果启用详细模式，记录研究过程
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "researching",
                f"🤔 正在跨多个源研究相关信息...\n",
                self.researcher.websocket,
            )

        # 抓取新URL
        scraped_content = await self.researcher.scraper_manager.browse_urls(new_search_urls)

        if self.researcher.vector_store:
            self.researcher.vector_store.load(scraped_content)

        return scraped_content
