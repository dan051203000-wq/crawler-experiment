# -*- coding: utf-8 -*-
"""
步骤 4：代码审查与工程化重构 —— 面向对象最终版。
对应 Prompt：prompts/prompt_04_refactor.md

重构要点（对比 steps/step3_save.py 过程式版本）：
  1. 全部状态收敛进 NewsCrawler 类：会话复用 requests.Session（连接池，减少握手开销）；
  2. 抓取 / 解析 / 持久化拆成独立方法，职责单一，便于测试；
  3. 重试、限速、UA 伪装成为类配置项，不再散落在代码里；
  4. 统一异常兜底：字段缺失填空字符串，单条失败不影响整体。
"""
import re
import time
import csv
import requests
from bs4 import BeautifulSoup


class NewsCrawler:
    """中国新闻网滚动新闻静态页面爬虫（requests + BeautifulSoup）。"""

    BASE_URL = "https://www.chinanews.com.cn"
    HEADERS = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36")
    }
    FIELDS = ["标题", "时间", "作者", "链接"]

    def __init__(self, list_url: str, out_csv: str = "result.csv",
                 max_items: int = 12, pages: int = 1,
                 delay: float = 2.0, retries: int = 3, timeout: float = 10.0):
        self.list_url = list_url
        self.out_csv = out_csv
        self.max_items = max_items
        self.pages = pages
        self.delay = delay          # 反爬合规：请求间隔不低于 2 秒
        self.retries = retries      # 网络超时重试次数
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    # ---------- 网络层 ----------
    def fetch(self, url: str) -> str | None:
        """带重试的 GET：超时/连接错误最多重试 self.retries 次。"""
        for attempt in range(1, self.retries + 1):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.encoding = "utf-8"
                return resp.text
            except (requests.Timeout, requests.ConnectionError) as e:
                print(f"  [重试 {attempt}/{self.retries}] {url} -> {e.__class__.__name__}")
                time.sleep(self.delay)
        return None

    # ---------- 解析层 ----------
    def parse_list_page(self, html: str) -> list[dict]:
        """解析列表页：标题 / 时间 / 链接（作者占位为空）。"""
        soup = BeautifulSoup(html, "html.parser")
        rows = []
        for li in soup.select("div.content_list li"):
            a = li.select_one("div.dd_bt a")
            if a is None:                                   # 广告位等无效行
                continue
            dd_time = li.select_one("div.dd_time")
            rows.append({
                "标题": a.get_text(strip=True),
                "时间": dd_time.get_text(strip=True) if dd_time else "",
                "作者": "",                                  # 字段缺失填空字符串
                "链接": self.BASE_URL + a["href"],
            })
        return rows

    @staticmethod
    def parse_author(detail_html: str | None) -> str:
        """从详情页提取'作者：xxx'，取不到返回空字符串。"""
        if not detail_html:
            return ""
        m = re.search(r"作者[:：]\s*([^<\s][^<]{0,30})", detail_html)
        return m.group(1).strip() if m else ""

    # ---------- 主流程 ----------
    def crawl(self) -> list[dict]:
        all_rows: list[dict] = []
        for page in range(1, self.pages + 1):
            url = self.list_url if page == 1 else \
                f"https://www.chinanews.com.cn/scroll-news/news{page}.html"
            print(f"[列表页 {page}/{self.pages}] {url}")
            html = self.fetch(url)
            if html is None:
                print("  列表页抓取失败，跳过")
                continue
            all_rows.extend(self.parse_list_page(html))
            if page < self.pages:
                time.sleep(self.delay)

        rows = all_rows[: self.max_items]
        print(f"共解析 {len(all_rows)} 条，按配置抓取前 {len(rows)} 条详情以补齐作者字段")

        ok = 0
        for i, row in enumerate(rows, 1):
            time.sleep(self.delay)                          # 每条详情请求间隔 2 秒
            author = self.parse_author(self.fetch(row["链接"]))
            row["作者"] = author
            ok += 1
            print(f"  [{i}/{len(rows)}] {row['标题'][:22]} | 作者: {author or '(缺省为空)'}")
        return rows

    # ---------- 持久化层 ----------
    def save(self, rows: list[dict]) -> None:
        with open(self.out_csv, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def run(self) -> None:
        print(f"目标: {self.list_url} | 间隔 {self.delay}s | 超时重试 {self.retries} 次")
        rows = self.crawl()
        if not rows:
            print("未抓取到任何数据")
            return
        self.save(rows)
        print(f"成功抓取条数: {len(rows)}")
        print(f"已保存 {self.out_csv}（UTF-8 编码，列: {', '.join(self.FIELDS)}）")


def main():
    crawler = NewsCrawler(
        list_url="https://www.chinanews.com.cn/scroll-news/news1.html",
        out_csv="result.csv",
        max_items=12,   # 每条详情页一次请求，2s 间隔约 25s 跑完
        pages=1,
    )
    crawler.run()


if __name__ == "__main__":
    main()
