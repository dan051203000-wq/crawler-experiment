# Prompt 02：解析 HTML 提取字段（步骤 2-3）

```
请求已跑通（状态码 200）。现在让 AI 生成"解析 HTML 提取字段"的代码。
约束：使用 BeautifulSoup；只解析，不存储；
列表页选择器请基于真实 DOM 结构；解析失败的字段填空字符串而不是抛异常。
验收：打印解析出的总条数与前 3 条数据（标题/时间/栏目/链接）。
```

## 迭代记录

- AI 初版用 `find_all("li")` 全局匹配，把导航栏 `<li>` 也抓了进来；
  反馈"解析结果混入了导航链接"后，改为锁定 `content_list li`。
- 首次锁定 `ul.content_list li` 仍解析出 0 条：把 CSS 样式类名
  `.content_list li` 想当然当成了 `ul`，实际容器是 `div.content_list`。
  用 `soup.select` 逐级验证父节点后修正为 `div.content_list li`，
  解析出 110 条 → 通过。
- 广告位 `<li>`（无 `div.dd_bt a`）需要跳过，加了空值保护。
- 验收结果：解析出约 110 条，前 3 条标题/时间/栏目正确 → 通过（见 steps/step2_parse.py）。
