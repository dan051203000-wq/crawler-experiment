# -*- coding: utf-8 -*-
"""
步骤 3：数据持久化与异常处理（重构前的完整过程式脚本）。
验收标准：result.csv 为 UTF-8 编码、列名正确、数据对齐。
对应 Prompt：prompts/prompt_03_persist.md

异常处理要点：
  1. 字段缺失时填空字符串，避免程序崩溃（.get(key, "")）；
  2. 网络超时重试 3 次（fetch_with_retry）；
  3. 详情页解析失败不影响整体抓取，只记录日志。
"""
import re
import time
import csv
import requests
from bs4 import BeautifulSoup

URL = "https://www.chinanews.com.cn/scroll-news/news1.html"
BASE = "https://www.chinanews.com.cn"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36")
}
MAX_ITEMS = 12          # 最多抓取条数（每条要访问详情页拿作者）
DELAY = 2               # 请求间隔，反爬合规要求不低于 2 秒
RETRIES = 3             # 超时重试次数
FIELDS = ["标题", "时间", "作者", "链接"]


def fetch_with_retry(url: str, retries: int = RETRIES) -> str | None:
    """带重试的 GET：网络超时/连接错误最多重试 3 次。"""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.encoding = "utf-8"
            return resp.text
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"  [重试 {attempt}/{retries}] {url} 出错: {e.__class__.__name__}")
            time.sleep(DELAY)
    return None


def parse_list(html: str) -> list[dict]:
    """解析列表页，提取 标题/时间/链接（作者为空占位，后面详情页补）。"""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for li in soup.select("div.content_list li"):
        a = li.select_one("div.dd_bt a")
        if a is None:
            continue
        dd_time = li.select_one("div.dd_time")
        rows.append({
            "标题": a.get_text(strip=True),
            "时间": dd_time.get_text(strip=True) if dd_time else "",  # 缺失填空串
            "作者": "",
            "链接": BASE + a["href"],
        })
    return rows


def fetch_author(detail_html: str) -> str:
    """从详情页提取'作者：xxx'，取不到就返回空字符串（不崩溃）。"""
    if not detail_html:
        return ""
    m = re.search(r"作者[:：]\s*([^<\s][^<]{0,30})", detail_html)
    return m.group(1).strip() if m else ""


def main():
    html = fetch_with_retry(URL)
    if html is None:
        print("列表页抓取失败，退出")
        return

    rows = parse_list(html)[:MAX_ITEMS]
    print(f"列表页解析出 {len(parse_list(html))} 条，抓取前 {len(rows)} 条详情获取作者")

    ok = 0
    for i, row in enumerate(rows, 1):
        time.sleep(DELAY)                       # 反爬：间隔不低于 2 秒
        detail = fetch_with_retry(row["链接"])
        row["作者"] = fetch_author(detail)
        ok += 1
        print(f"  [{i}/{len(rows)}] {row['标题'][:20]} | 作者: {row['作者'] or '(缺省为空)'}")

    # 写 CSV：newline="" + utf-8-sig（带 BOM 的 UTF-8，Excel 打开不乱码）
    with open("result.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"成功抓取条数: {ok}")
    print("已保存 result.csv")


if __name__ == "__main__":
    main()
