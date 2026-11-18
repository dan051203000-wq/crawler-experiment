# -*- coding: utf-8 -*-
"""生成《爬虫开发实验报告》docx：含版面草图、真实运行截图、验收表与问题表。"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.path.join(ROOT, "screenshots")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False


# ---------------- 版面 / 流程草图 ----------------
def make_sketch():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#eef4ff", ec="#2f5fbf", fontsize=9.5):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.08",
                           fc=fc, ec=ec, lw=1.4)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fontsize, color="#1c2b45", linespacing=1.6)

    def arrow(x1, y1, x2, y2, label=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=14, lw=1.4, color="#5a6b85"))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.14, label, ha="center",
                    fontsize=8, color="#5a6b85")

    ax.text(5, 3.95, "抓取流程与页面结构映射", ha="center", fontsize=12,
            fontweight="bold", color="#1c2b45")

    box(0.2, 2.35, 2.2, 1.15, "① 列表页请求\nGET 滚动新闻页\nUA 伪装 + timeout 10s", fontsize=8.8)
    box(2.95, 2.35, 2.3, 1.15, "② 解析条目\n div.content_list li\n├ div.dd_bt a → 标题/链接\n└ div.dd_time → 时间", "#fff6e8", "#c98416")
    box(5.85, 2.35, 2.2, 1.15, "③ 详情页请求\n（逐条，间隔 2s）\n正则提取“作者：xxx”", "#eaf9ef", "#2f8f4e")
    box(8.35, 2.35, 1.45, 1.15, "④ 写 CSV\nUTF-8\n12 行", "#fdeef2", "#b5345c")

    arrow(2.35, 2.92, 2.95, 2.92)
    arrow(5.25, 2.92, 5.85, 2.92, "每页 100 条")
    arrow(8.05, 2.92, 8.35, 2.92)

    # 字段映射
    ax.text(0.25, 1.85, "字段映射", fontsize=10, fontweight="bold", color="#1c2b45")
    rows = [
        ("标题", "div.content_list li > div.dd_bt > a  文本"),
        ("时间", "div.content_list li > div.dd_time  文本（11-18 15:10）"),
        ("链接", "div.dd_bt > a[href] 前拼接 https://www.chinanews.com.cn"),
        ("作者", "详情页正文信息区，正则 作者[：:]\\s*(.+?)\\s*$"),
    ]
    ax.add_patch(plt.Rectangle((0.25, 0.55), 9.5, 1.15, fc="#f7f8fa", ec="#d5dae2", lw=1))
    for i, (k, v) in enumerate(rows):
        y = 1.52 - i * 0.25
        ax.text(0.45, y, k, fontsize=9, color="#2f5fbf", fontweight="bold")
        ax.text(1.15, y, v, fontsize=8.6, color="#33415c")

    ax.text(0.25, 0.2, "异常兜底：字段缺失填空字符串；超时重试 3 次；单条详情失败不影响整体。",
            fontsize=8.6, color="#8a5a00")

    path = os.path.join(SHOT, "00_sketch.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ---------------- docx 辅助 ----------------
def set_font(run, size=12, bold=False, font_cn="宋体", font_en="Times New Roman",
             color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font_en
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_cn)
    if color:
        run.font.color.rgb = color


def add_para(doc, text, size=12, bold=False, align=None, indent=True,
             font_cn="宋体", space_after=6, first_line=True):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.5
    if first_line and indent:
        pf.first_line_indent = Pt(size * 2)
    run = p.add_run(text)
    set_font(run, size, bold, font_cn)
    return p


def add_heading(doc, text, level=1):
    size = 16 if level == 1 else 14 if level == 2 else 12
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.4
    run = p.add_run(text)
    set_font(run, size, True, "黑体", "Times New Roman")
    return p


def add_table(doc, headers, rows, widths=None, font_size=10):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_font(run, font_size, True, "黑体")
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "EEF2F8")
        hdr[i]._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.line_spacing = 1.2
            run = p.add_run(str(val))
            set_font(run, font_size)
    if widths:
        for r in table.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Cm(w)
    doc.add_paragraph()
    return table


def add_figure(doc, img_path, caption, width_cm=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(img_path, width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(10)
    run = cap.add_run(caption)
    set_font(run, 10.5, False, "楷体")


def add_code(doc, text):
    for line in text.strip("\n").split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.left_indent = Pt(18)
        run = p.add_run(line if line else " ")
        set_font(run, 9, False, "宋体", "Consolas")
    doc.add_paragraph()


# ---------------- 正文 ----------------
def build():
    sketch = make_sketch()
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.4)
    sec.left_margin = sec.right_margin = Cm(2.6)

    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.paragraph_format.space_after = Pt(6)
    set_font(t.add_run("爬虫开发实验报告"), 22, True, "黑体")

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(14)
    set_font(sub.add_run("实验名称：基于 Vibe Coding 工作流的静态网页爬虫开发"), 12, False, "楷体")

    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.paragraph_format.space_after = Pt(16)
    set_font(info.add_run("姓名：张娜丹        班级：____________        学号：____________        日期：2026-11-18"),
             11, False, "宋体")

    # 一、实验目的
    add_heading(doc, "一、实验目的")
    for s in ["1. 掌握 Vibe Coding 的核心工作流（意图定义、任务拆解、验证闭环），改变传统逐行编写代码的习惯。",
              "2. 学会使用结构化 Prompt 驱动 AI 生成 Python 爬虫代码（基于 requests 与 BeautifulSoup）。",
              "3. 掌握对 AI 生成代码的审查、调试与重构能力，建立反爬合规意识。"]:
        add_para(doc, s)

    # 二、实验环境
    add_heading(doc, "二、实验环境")
    add_table(doc,
              ["项目", "配置"],
              [["操作系统", "Windows 11"],
               ["Python", "3.13.12"],
               ["核心依赖", "requests 2.34.2、beautifulsoup4 4.15.0、pandas 3.0.6"],
               ["AI 编程助手", "AI 编程助手（Vibe Coding 迭代式协作）"],
               ["目标站点", "中国新闻网滚动新闻（https://www.chinanews.com.cn/scroll-news/news1.html，静态 HTML，UTF-8）"],
               ["数据接口（进阶）", "https://www.chinanews.com.cn/rss/scroll-news.xml"]],
              widths=[3.5, 12.0])

    # 三、需求分析与设计
    add_heading(doc, "三、需求分析与设计")
    add_heading(doc, "3.1 需求拆解", 2)
    add_para(doc, "实验要求在公开新闻网站列表页抓取“标题、发布时间、作者、链接”四个字段并输出 result.csv。"
                  "拆解后确认三个技术事实：① 列表页为静态 HTML，requests 可直接拿到数据；"
                  "② 列表页不含作者字段，需访问详情页补齐；③ 详情页请求量大，必须限速与容错。")
    add_table(doc,
              ["目标字段", "页面位置", "提取方式"],
              [["标题", "列表页 <div.dd_bt> 内 <a> 文本", "BeautifulSoup 选择器"],
               ["时间", "列表页 <div.dd_time> 文本（如 11-18 15:10）", "BeautifulSoup 选择器"],
               ["链接", "列表页 <div.dd_bt> 内 <a href> 相对路径", "选择器取属性 + 域名拼接"],
               ["作者", "详情页正文信息区“作者：xxx”", "正则 作者[：:]\\s*(.+?)"]],
              widths=[2.8, 7.2, 5.5])
    add_para(doc, "因此采用“两段式抓取”：先一次性解析列表页拿到 100 条条目，再对前 12 条逐条访问详情页补作者，"
                  "每条间隔 2 秒，既满足字段完整性，又把请求量控制在合规范围内。")

    add_heading(doc, "3.2 版面与流程草图", 2)
    add_figure(doc, sketch, "图 1  抓取流程与页面结构映射草图", 15.5)

    add_heading(doc, "3.3 项目结构", 2)
    add_code(doc, """crawler-experiment/
├── crawler.py              # 重构后最终版（NewsCrawler 类）
├── dynamic_crawler.py      # 进阶挑战：数据接口方案
├── steps/                  # 分步生成的过程代码
│   ├── step1_fetch.py      # 步骤2-1 请求验证
│   ├── step2_parse.py      # 步骤2-3 解析验证
│   └── step3_save.py       # 步骤3 持久化（重构前）
├── prompts/                # 5 份结构化 Prompt 与迭代记录
├── screenshots/            # 运行截图
├── result.csv              # 抓取结果（UTF-8，12 条）
└── docs/                   # 本报告""")

    # 四、实验过程
    add_heading(doc, "四、实验过程")
    add_heading(doc, "4.1 步骤 1：需求澄清与结构化 Prompt", 2)
    add_para(doc, "按照“角色 + 目标 + 约束 + 验收标准”编写初始 Prompt，明确使用 requests 与 BeautifulSoup、"
                  "UA 伪装、请求间隔不低于 2 秒、超时重试 3 次，并要求 AI 本步骤只生成请求代码。"
                  "完整 Prompt 见仓库 prompts/prompt_01_request.md。")
    add_code(doc, """你是 Python 后端工程师。我需要编写一个静态网页爬虫。
目标：抓取 https://www.chinanews.com.cn/scroll-news/news1.html 的列表页，
提取标题、时间、作者、链接。
约束：使用 requests 和 BeautifulSoup；必须设置 User-Agent 伪装；
请求间隔不低于 2 秒；遇到网络超时需重试 3 次。
本步骤只做一件事：先仅生成"发送请求并获取 HTML"的最小代码。
验收：运行后打印状态码 200、HTML 长度和前 200 字符。""")
    add_para(doc, "AI 首版代码漏了响应编码声明，导致中文乱码；把现象反馈后补上 resp.encoding = \"utf-8\"，"
                  "跑通状态码 200、HTML 长度 83733 字符，验收通过。")
    add_figure(doc, os.path.join(SHOT, "01_fetch.png"), "图 2  步骤 1 运行结果：状态码 200 与 HTML 长度")

    add_heading(doc, "4.2 步骤 2：分步生成与最小化验证", 2)
    add_para(doc, "请求跑通后才让 AI 生成解析代码。AI 初版用 find_all(\"li\") 全局匹配，把导航栏条目也抓了进来；"
                  "反馈后锁定列表容器。这里踩了一个真实坑：CSS 里写的是 .content_list li 样式，"
                  "AI 据此推断容器为 <ul class=\"content_list\">，实际 DOM 是 <div class=\"content_list\">，"
                  "导致第一次运行解析出 0 条。用 soup.select 逐级打印父节点后修正为 div.content_list li，"
                  "解析出 100 条。")
    add_figure(doc, os.path.join(SHOT, "02_parse.png"), "图 3  步骤 2 运行结果：解析出 100 条，前 3 条字段正确")

    add_heading(doc, "4.3 步骤 3：数据持久化与异常处理", 2)
    add_para(doc, "解析验证通过后追加存储与容错逻辑：所有字段用 .get(key, \"\") 兜底，"
                  "作者字段缺失填空字符串；网络超时/连接错误重试 3 次；单条详情页失败只影响该行作者为空，"
                  "不中断整体流程。CSV 使用 utf-8-sig（带 BOM 的 UTF-8），解决 Excel 打开中文乱码问题。")
    add_figure(doc, os.path.join(SHOT, "03_save.png"), "图 4  步骤 3 运行结果：12 条全部抓到作者，成功条数 12")

    add_para(doc, "对 result.csv 做了五项验收检查：")
    add_table(doc,
              ["检查项", "要求", "实测结果", "结论"],
              [["文件编码", "UTF-8", "utf-8-sig（带 BOM 的 UTF-8，BOM 校验通过）", "通过"],
               ["列名", "标题/时间/作者/链接", "['标题', '时间', '作者', '链接']", "通过"],
               ["行数", "与打印成功条数一致", "12 行 = 成功抓取 12 条", "通过"],
               ["列对齐", "每行 4 列", "12 行全部 4 列，0 行错位", "通过"],
               ["可读性", "Excel 打开不乱码", "中文标题、作者正常显示", "通过"]],
              widths=[3.0, 4.8, 6.2, 2.0])

    add_heading(doc, "4.4 步骤 4：代码审查与工程化重构", 2)
    add_para(doc, "将过程式脚本整体喂回 AI，要求审查性能瓶颈与安全隐患并重构为 NewsCrawler 类。"
                  "AI 指出三处问题：每次循环新建 HTTP 连接（改用 requests.Session 复用连接池）、"
                  "UA 与重试次数硬编码散落（收敛为类常量与构造参数）、状态依赖全局变量（收敛为实例属性）。"
                  "重构后按 fetch / parse_list_page / parse_author / crawl / save 分层，功能不变。")
    add_table(doc,
              ["对比项", "重构前（steps/step3_save.py）", "重构后（crawler.py）"],
              [["组织结构", "函数 + 全局常量", "NewsCrawler 类，职责分层"],
               ["连接复用", "每次 requests.get 新建连接", "requests.Session 复用 TCP 连接池"],
               ["可配置性", "MAX_ITEMS/DELAY 改源码", "构造参数 max_items/pages/delay/retries"],
               ["异常兜底", "函数内部各自 try", "统一 fetch 重试 + 字段空串兜底"],
               ["输出结果", "12 条，字段一致", "12 条，字段一致（逻辑未变）"]],
              widths=[3.0, 6.5, 6.5])
    add_figure(doc, os.path.join(SHOT, "04_final.png"), "图 5  步骤 4 重构后运行结果：功能一致，成功条数 12")

    # 五、进阶挑战
    add_heading(doc, "五、进阶挑战：动态渲染页面的抓取方案")
    add_para(doc, "若目标站点是 Vue/React 动态渲染，初始 HTML 中不含数据，BeautifulSoup 解析会得到空列表。"
                  "可行路径有两条：① 打开开发者工具 Network 面板找到页面调用的数据接口，用 requests 直接请求接口；"
                  "② 接口被加密/鉴权难以复现时，用 Playwright/Selenium 无头浏览器执行 JS 后再取 DOM。"
                  "本实验实现方案 ①：中新网同时提供 RSS 数据接口 /rss/scroll-news.xml，"
                  "用 xml.etree 直接解析，无需访问详情页。")
    add_table(doc,
              ["对比维度", "HTML 解析方案（crawler.py）", "数据接口方案（dynamic_crawler.py）"],
              [["数据来源", "渲染完成的 HTML DOM", "RSS XML 接口"],
               ["请求次数（12 条）", "13 次（1 次列表页 + 12 次详情页）", "1 次"],
               ["实测耗时", "27.0 s（12 次详情请求 × 2s 强制间隔）", "0.19 s"],
               ["代码复杂度", "需维护 CSS 选择器 + 正则，还要处理详情页补字段", "XML 树按节点取字段，逻辑线性"],
               ["字段完整度", "标题/时间/作者/链接齐全", "标题/时间/链接齐全，接口未提供作者（空串）"],
               ["抗改版能力", "页面结构调整即失效", "接口相对稳定，但需注意鉴权与加密"],
               ["适用场景", "静态页、无可用接口", "前后端分离站点、有公开或可复现接口"]],
              widths=[3.2, 6.4, 6.4])
    add_para(doc, "结论：动态渲染不是“必须上无头浏览器”。优先找接口，能用接口就不用渲染；"
                  "只有接口被加密或服务端渲染不可复现时，才付出无头浏览器的性能代价。"
                  "两方案在字段完整性上也有取舍——接口未必提供全部字段，需要与业务需求对齐。")
    add_figure(doc, os.path.join(SHOT, "05_dynamic.png"), "图 6  进阶挑战：接口方案 1 次请求 0.19s 抓取 12 条")

    # 六、问题与解决
    add_heading(doc, "六、问题与解决方法")
    add_table(doc,
              ["序号", "问题现象", "原因分析", "解决方法"],
              [["1", "解析结果混入导航栏和广告链接", "用 find_all(\"li\") 全局匹配，未限定列表容器", "锁定 div.content_list li，跳过无标题节点的广告位"],
               ["2", "锁定列表后仍解析出 0 条", "把 CSS 类 .content_list 想当然当成 ul，实际容器是 div", "打印父节点链路验证 DOM，改为 div.content_list li，解析出 100 条"],
               ["3", "获取的 HTML 中文乱码", "requests 未声明响应编码，按 ISO-8859-1 解码", "显式设置 resp.encoding = \"utf-8\""],
               ["4", "result.csv 在 Excel 打开中文乱码", "无 BOM 的 UTF-8 被 Excel 按本地编码解析", "改用 utf-8-sig，仍是 UTF-8 且 Excel 兼容"],
               ["5", "作者字段抓不到", "列表页本身不含作者，只在详情页“作者：xxx”处", "进详情页用正则提取，取不到填空字符串"],
               ["6", "个别详情页超时导致脚本中断风险", "未做重试与兜底，异常直接抛出", "fetch 重试 3 次并返回 None，作者空串兜底，整体继续"],
               ["7", "大量请求有被封风险", "详情页请求密集", "UA 伪装 + 每条间隔 2 秒 + 限量 12 条，遵守爬虫合规"]],
              widths=[1.2, 5.2, 4.8, 4.8])

    # 七、总结
    add_heading(doc, "七、实验总结")
    add_para(doc, "本次实验完整走通了 Vibe Coding 的闭环，最大收获不是写出爬虫，而是三个判断习惯：")
    add_para(doc, "第一，AI 写的代码必须当作“待审代码”看。两个最典型的错误——全局 find_all(\"li\") 和把 "
                  ".content_list 当成 ul——都不是语法错误，AI 跑起来也不报错，只是结果为空或混入脏数据，"
                  "只有验收标准写清楚（“打印前 3 条”），问题才暴露得出来。", indent=True)
    add_para(doc, "第二，验收标准要可量化。状态码 200、解析条数、CSV 列数与编码、成功条数，"
                  "这些可校验的点让每一步都有明确通过/不通过，而不是“看起来能跑”。")
    add_para(doc, "第三，反爬合规是设计约束而不是事后补丁：UA 伪装、2 秒间隔、限量抓取，写进第一版 Prompt，"
                  "比事后加 sleep 更可靠。进阶挑战也说明，工程选择要比“技术炫技”更优先——"
                  "接口方案比无头浏览器快两个数量级，代价只是作者字段缺失，是否可接受取决于业务需求。")

    path = os.path.join(DOCS, "爬虫开发实验报告.docx")
    doc.save(path)
    print("saved", path)


if __name__ == "__main__":
    build()
