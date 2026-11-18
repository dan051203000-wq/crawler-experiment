# -*- coding: utf-8 -*-
"""
进阶挑战：动态渲染页面的应对方案与对比。
对应 Prompt：prompts/prompt_05_dynamic.md

思路：如果目标页面是 Vue/React 动态渲染的，BeautifulSoup 拿到的
初始 HTML 里没有数据。应对路径按优先级：
  1. 浏览器 F12 -> Network -> XHR，找到页面实际调用的数据接口，
     用 requests 直接请求接口（JSON/XML），跳过渲染环节 —— 最快最稳；
  2. 接口有加密/鉴权难以复现时，再用 Playwright/Selenium 等无头浏览器
     执行 JS 渲染后取 DOM（本实验未采用：依赖重、慢一个数量级）。

本脚本演示方案 1：中新网滚动新闻同时提供 RSS 数据接口
  https://www.chinanews.com.cn/rss/scroll-news.xml
数据以 XML 返回，无需解析 HTML、无需访问详情页即可拿到标题/时间/链接。

运行对比（同样的 12 条数据）：
  python crawler.py            # HTML 方案：1 次列表页 + 12 次详情页 ≈ 26 个请求
  python dynamic_crawler.py    # 接口方案：1 次接口请求即得全部字段
结论详见 docs/爬虫开发实验报告.docx 「进阶挑战」一节。
"""
import re
import time
import csv
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://www.chinanews.com.cn/rss/scroll-news.xml"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36")
}


def fetch_rss() -> str | None:
    for attempt in range(1, 4):
        try:
            resp = requests.get(RSS_URL, headers=HEADERS, timeout=10)
            resp.encoding = "utf-8"
            return resp.text
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"  [重试 {attempt}/3] {e.__class__.__name__}")
            time.sleep(2)
    return None


def main():
    t0 = time.perf_counter()
    xml_text = fetch_rss()
    if xml_text is None:
        print("接口请求失败")
        return

    root = ET.fromstring(xml_text)
    rows = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()      # 缺失字段直接填空串
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "") or ""
        # RSS 无作者字段时填空字符串；尝试从 description 开头提取正文来源
        m = re.search(r"来源[:：]\s*([^<\s][^<]{0,30})", desc)
        rows.append({
            "标题": title,
            "时间": item.findtext("pubDate", "").strip(),
            "作者": m.group(1).strip() if m else "",
            "链接": link,
        })

    rows = rows[:12]
    elapsed = time.perf_counter() - t0

    with open("result_dynamic.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["标题", "时间", "作者", "链接"])
        writer.writeheader()
        writer.writerows(rows)

    for r in rows[:3]:
        print(r)
    print(f"成功抓取条数: {len(rows)}")
    print(f"接口方案耗时: {elapsed:.2f}s（仅 1 次 HTTP 请求，无详情页访问、无强制间隔）")


if __name__ == "__main__":
    main()
