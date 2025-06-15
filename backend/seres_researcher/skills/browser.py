from seres_researcher.utils.workers import WorkerPool

from ..actions.utils import stream_output
from ..actions.web_scraping import scrape_urls
from ..web_scraper.utils import get_image_hash


class BrowserManager:
    """管理Research Agent的上下文。"""

    def __init__(self, researcher):
        self.researcher = researcher
        self.worker_pool = WorkerPool(researcher.cfg.max_scraper_workers)

    async def browse_urls(self, urls: list[str]) -> list[dict]:
        """
        从一组URL中抓取内容。

        参数：
            urls (list[str]): 要抓取的URL列表。

        返回：
            list[dict]: 抓取内容的结果列表。
        """
        if self.researcher.verbose:
            await stream_output(
                "logs",
                "scraping_urls",
                f"🌐 正在从 {len(urls)} 个URL中抓取内容...",
                self.researcher.websocket,
            )

        scraped_content, images = await scrape_urls(
            urls, self.researcher.cfg, self.worker_pool
        )
        self.researcher.add_research_sources(scraped_content)
        new_images = self.select_top_images(images, k=4)  # 选择前4张图片
        self.researcher.add_research_images(new_images)

        if self.researcher.verbose:
            await stream_output(
                "logs",
                "scraping_content",
                f"📄 已抓取 {len(scraped_content)} 页内容",
                self.researcher.websocket,
            )
            await stream_output(
                "logs",
                "scraping_images",
                f"🖼️ 从 {len(images)} 张图片中选择了 {len(new_images)} 张新图片",
                self.researcher.websocket,
                True,
                new_images,
            )
            await stream_output(
                "logs",
                "scraping_complete",
                f"🌐 抓取完成",
                self.researcher.websocket,
            )

        return scraped_content

    def select_top_images(self, images: list[dict], k: int = 2) -> list[str]:
        """
        根据图片内容选择最相关的图片并去除重复项。

        参数：
            images (list[dict]): 包含 'url' 和 'score' 键的图片字典列表。
            k (int): 如果没有高分图片时要选择的图片数量。

        返回：
            list[str]: 选定的图片URL列表。
        """
        unique_images = []
        seen_hashes = set()
        current_research_images = self.researcher.get_research_images()

        # 按图片评分降序处理图片
        for img in sorted(images, key=lambda im: im["score"], reverse=True):
            img_hash = get_image_hash(img['url'])
            if (
                img_hash
                and img_hash not in seen_hashes
                and img['url'] not in current_research_images
            ):
                seen_hashes.add(img_hash)
                unique_images.append(img["url"])

                if len(unique_images) == k:
                    break

        return unique_images
