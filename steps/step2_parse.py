# -*- coding: utf-8 -*-
"""
步骤 2-3（迭代）：请求跑通后，再让 AI 生成"解析 HTML 提取字段"的代码。
验收标准：打印前 3 条数据，验证解析逻辑正确。
对应 Prompt：prompts/prompt_02_parse.md

页面结构（人工审查 AI 生成代码后确认的选择器）：
  div.content_list > li
    div.dd_lm  > a   —— 栏目（社会/财经/国际……）
    div.dd_bt  > a   —— 标题 + 详情页链接
    div.dd_time        —— 发布时间，如 "11-18 15:10"
"""
import requests
from bs4 import BeautifulSoup

URL = "https://www.chinanews.com.cn/scroll-news/news1.html"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36")
}
BASE = "https://www.chinanews.com.cn"


def main():
    resp = requests.get(URL, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    for li in soup.select("div.content_list li"):
        a_title = li.select_one("div.dd_bt a")
        if a_title is None:          # 广告位/占位行，直接跳过
            continue
        dd_time = li.select_one("div.dd_time")
        dd_lm = li.select_one("div.dd_lm")
        items.append({
            "标题": a_title.get_text(strip=True),
            "链接": BASE + a_title["href"],
            "时间": dd_time.get_text(strip=True) if dd_time else "",
            "栏目": dd_lm.get_text(strip=True) if dd_lm else "",
        })

    print("共解析出条目:", len(items))
    print("前 3 条数据验证:")
    for row in items[:3]:
        print(row)


if __name__ == "__main__":
    main()
