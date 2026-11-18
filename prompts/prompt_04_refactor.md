# Prompt 04：代码审查与工程化重构（步骤 4）

```
请审查下面这段完整爬虫代码（steps/step3_save.py 的内容），
指出潜在的性能瓶颈或安全隐患，并将其重构为面向对象的类结构
（如 NewsCrawler 类），保持功能不变。
```

## AI 审查结论（人工核实后采纳）

| 问题 | 类型 | 重构方案 |
| --- | --- | --- |
| 每次循环都新建 HTTP 连接 | 性能 | 改用 `requests.Session` 复用 TCP 连接池 |
| UA 硬编码散落多处 | 可维护性 | 收敛为类常量 `HEADERS` |
| `parse_list` 返回量依赖全局变量 | 安全/健壮性 | 状态全部收敛进类，`max_items` 可配置 |
| 异常只捕获 Timeout/ConnectionError | 健壮性 | 保持窄捕获并返回 None 兜底，单条失败不影响整体 |

## 重构验证

- 对比重构前后 result.csv：列名、行数、字段内容一致 → 核心逻辑未被破坏；
- 代码行数持平但职责分为 fetch / parse / save 三层，可读性提升
  （见根目录 crawler.py）。
