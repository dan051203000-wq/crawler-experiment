# -*- coding: utf-8 -*-
"""
步骤 2-1：最小化验证 —— 先只让 AI 生成"发送请求并获取 HTML"的代码。
验收标准：成功获取状态码 200 及 HTML 内容。
对应 Prompt：prompts/prompt_01_request.md
"""
import requests

URL = "https://www.chinanews.com.cn/scroll-news/news1.html"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36")
}


def main():
    resp = requests.get(URL, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    print("状态码:", resp.status_code)
    print("HTML 长度:", len(resp.text))
    print("HTML 前 200 字符:")
    print(resp.text[:200])


if __name__ == "__main__":
    main()
