# Prompt 01：发送请求并获取 HTML（步骤 2-1）

> 按"角色 + 目标 + 约束 + 验收标准"格式编写的结构化 Prompt，禁止一次性生成全部代码。

```
你是 Python 后端工程师。我需要编写一个静态网页爬虫。
目标：抓取 https://www.chinanews.com.cn/scroll-news/news1.html 的列表页，
提取标题、时间、作者、链接。
约束：使用 requests 和 BeautifulSoup；必须设置 User-Agent 伪装；
请求间隔不低于 2 秒；遇到网络超时需重试 3 次。
本步骤只做一件事：先仅生成"发送请求并获取 HTML"的最小代码，
不要写解析和存储逻辑。
验收：运行后打印状态码 200、HTML 长度和前 200 字符。
```

## 迭代记录

- AI 首次生成的代码未设置 `resp.encoding = "utf-8"`，中文标题出现乱码；
  反馈"输出中文乱码"后补充了编码声明。
- 验收结果：状态码 200，HTML 长度约 8.2 万字符 → 通过（见 steps/step1_fetch.py）。
