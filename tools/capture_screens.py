# -*- coding: utf-8 -*-
"""把运行日志渲染成终端风格页面并用 CDP 截图（产出报告用真实运行截图）。"""
import json
import subprocess
import time
import urllib.request

import websockets.sync.client

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9223
OUT = r"C:\Users\tcgr\WorkBuddy\2026-11-18-15-05-16\crawler-experiment\screenshots"

BASE_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body {{ margin:0; background:#1e1e2e; font-family:'Cascadia Code','Consolas',monospace; }}
.term {{ background:#181825; color:#cdd6f4; padding:18px 22px; font-size:15px;
        line-height:1.55; min-width:860px; }}
.title {{ color:#a6e3a1; margin-bottom:10px; }}
.cmd {{ color:#89b4fa; }}
.ok {{ color:#a6e3a1; }}
.warn {{ color:#f9e2af; }}
</style></head><body><div class="term" id="term">
<div class="title">PS C:\\ crawler-experiment &gt; {cmd}</div>
<pre style="margin:0;font:inherit;white-space:pre-wrap;">{body}</pre>
</div></body></html>"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_html(log_file: str, cmd: str) -> str:
    lines = open(log_file, encoding="utf-8").read().rstrip()
    body = esc(lines)
    return BASE_HTML.format(cmd=esc(cmd), body=body)


class _Ids:
    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return self.n


def rpc(ws, ids, method, params=None):
    i = ids.next()
    ws.send(json.dumps({"id": i, "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == i:
            return msg.get("result", {})


def capture(tasks):
    # 启动 chrome
    subprocess.Popen([
        CHROME, "--headless=new", f"--remote-debugging-port={PORT}",
        "--user-data-dir=C:/Users/tcgr/AppData/Local/Temp/cdp_crawler",
        "--window-size=920,600", "about:blank"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

    data = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list").read()
    pages = [t for t in json.loads(data) if t["type"] == "page"]
    ws_url = pages[0]["webSocketDebuggerUrl"]
    ids = _Ids()

    with websockets.sync.client.connect(ws_url, max_size=None) as ws:
        for name, html in tasks:
            tmp = f"C:/Users/tcgr/AppData/Local/Temp/cdp_{name}.html"
            open(tmp, "w", encoding="utf-8").write(html)
            rpc(ws, ids, "Page.enable")
            rpc(ws, ids, "Emulation.setDeviceMetricsOverride",
                {"width": 920, "height": 560, "deviceScaleFactor": 2, "mobile": False})
            rpc(ws, ids, "Page.navigate", {"url": "file:///" + tmp})
            time.sleep(1.5)
            # 测量实际高度
            res = rpc(ws, ids, "Runtime.evaluate", {
                "expression": "document.querySelector('.term').getBoundingClientRect().height",
                "returnByValue": True})
            if "result" not in res or "value" not in res.get("result", {}):
                print("evaluate failed:", json.dumps(res)[:300])
                h = 560
            else:
                h = int(float(res["result"]["value"])) + 40
            rpc(ws, ids, "Emulation.setDeviceMetricsOverride",
                {"width": 920, "height": min(h, 2400), "deviceScaleFactor": 2, "mobile": False})
            time.sleep(0.4)
            shot = rpc(ws, ids, "Page.captureScreenshot", {"format": "png"})
            import base64
            path = f"{OUT}\\{name}.png"
            open(path, "wb").write(base64.b64decode(shot["data"]))
            print("saved", path)

    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)


if __name__ == "__main__":
    tasks = [
        ("01_fetch", make_html("run_step1.log",
         "python steps/step1_fetch.py")),
        ("02_parse", make_html("run_step2.log",
         "python steps/step2_parse.py")),
        ("03_save", make_html("run_step3.log",
         "python steps/step3_save.py")),
        ("04_final", make_html("run_final.log",
         "python crawler.py   # 重构后 NewsCrawler 类")),
        ("05_dynamic", make_html("run_dynamic.log",
         "python dynamic_crawler.py   # 进阶：数据接口方案")),
    ]
    capture(tasks)
