# 爬虫开发实验 · Vibe Coding 工作流

用「结构化 Prompt → 分步生成 → 运行验证 → 报错反馈 → 重构」的迭代流程，完成一个基于
`requests` + `BeautifulSoup` 的静态网页爬虫，抓取中国新闻网滚动新闻列表页的
**标题 / 发布时间 / 作者 / 链接**，输出 UTF-8 的 `result.csv`，并完成动态渲染页面的方案对比。

## 实验成果

| 项目 | 结果 |
| --- | --- |
| 目标站点 | 中国新闻网滚动新闻（静态 HTML，UTF-8） |
| 抓取条数 | 12 条（列表页解析出 100 条，取前 12 条进详情页补作者） |
| 输出文件 | `result.csv`（UTF-8，列：标题/时间/作者/链接，12 行无错位） |
| 反爬合规 | UA 伪装 + 每条请求间隔 2 秒 + 超时重试 3 次 + 限量抓取 |
| 重构 | 过程式脚本 → `NewsCrawler` 类（Session 复用、职责分层） |
| 进阶挑战 | 接口方案 1 次请求 0.19s，对比 HTML 方案 13 次请求 27.0s |

## 目录结构

```
crawler-experiment/
├── crawler.py              # 步骤 4 重构后最终版：NewsCrawler 类
├── dynamic_crawler.py      # 进阶挑战：RSS 数据接口方案
├── steps/
│   ├── step1_fetch.py      # 步骤 2-1 最小验证：请求并获取 HTML
│   ├── step2_parse.py      # 步骤 2-3 最小验证：解析并打印前 3 条
│   └── step3_save.py       # 步骤 3 完整过程式脚本（重构前）
├── prompts/                # 5 份结构化 Prompt + 迭代记录（Vibe Coding 证据）
├── screenshots/            # 各步骤真实运行截图 + 流程图草图
├── tools/
│   ├── capture_screens.py  # CDP 自动截图脚本
│   └── build_report.py     # 生成实验报告 docx
├── docs/爬虫开发实验报告.docx
├── result.csv              # 抓取结果
├── requirements.txt
└── .gitignore
```

## 运行方式

```bash
pip install -r requirements.txt

# 步骤 1：验证请求
python steps/step1_fetch.py

# 步骤 2：验证解析（打印前 3 条）
python steps/step2_parse.py

# 步骤 3：完整抓取并写 CSV（约 27s，12 条详情请求间隔 2s）
python steps/step3_save.py

# 步骤 4：重构后的类版本（输出相同）
python crawler.py

# 进阶挑战：数据接口方案（约 0.2s）
python dynamic_crawler.py
```

## 任务完成情况

| 实验要求 | 完成情况 | 对应文件 |
| --- | --- | --- |
| 结构化 Prompt（角色+目标+约束+验收） | 已完成，5 份 Prompt 全留档 | `prompts/` |
| 分步生成、最小化验证 | 请求 → 解析 → 存储 三步分别验证 | `steps/` |
| 字段缺失填空串、超时重试 3 次 | 已实现 | `crawler.py` |
| CSV 持久化（UTF-8、列名、对齐） | 已验收，12 行 4 列无错位 | `result.csv` |
| 代码审查 + OOP 重构 | 已完成，对比表见报告 | `crawler.py` |
| 进阶：动态渲染方案对比 | 已完成，代码复杂度与耗时双维度对比 | `dynamic_crawler.py` |
| 实验报告 | 含流程图、6 张截图、7 项问题排查 | `docs/` |

## 合规说明

仅抓取公开页面的公开字段，遵守 `robots` 访问约定，控制请求频率（不低于 2 秒）与抓取量，
数据仅用于课程实验，不用于商业用途与二次分发。
