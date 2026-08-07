#!/usr/bin/env python3
"""Render a self-contained offline review dashboard for source-extraction.json."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Source Extraction Review</title>
<style>
:root{color-scheme:light;--bg:#f5f5f7;--card:rgba(255,255,255,.76);--card-strong:rgba(255,255,255,.92);--ink:#1d1d1f;--muted:#6e6e73;--line:rgba(60,60,67,.16);--accent:#007aff;--good:#248a3d;--warn:#c93400;--bad:#d70015;--shadow:0 16px 44px rgba(0,0,0,.08)}
@media(prefers-color-scheme:dark){:root{color-scheme:dark;--bg:#000;--card:rgba(28,28,30,.78);--card-strong:rgba(36,36,38,.94);--ink:#f5f5f7;--muted:#aeaeb2;--line:rgba(255,255,255,.16);--accent:#0a84ff;--good:#30d158;--warn:#ff9f0a;--bad:#ff453a;--shadow:0 22px 64px rgba(0,0,0,.38)}}
*{box-sizing:border-box}html{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI","PingFang SC","Hiragino Sans GB",Arial,sans-serif;-webkit-font-smoothing:antialiased}body{margin:0;background:radial-gradient(circle at 90% 0,rgba(0,122,255,.13),transparent 30rem),var(--bg);color:var(--ink);font-size:15px;line-height:1.55}main{max-width:1220px;margin:auto;padding:30px 22px 68px}h1{margin:0 0 6px;font-size:clamp(26px,4vw,40px);letter-spacing:-.04em}h2{margin:30px 0 12px;font-size:21px;letter-spacing:-.025em}h3{margin:0 0 6px;font-size:16px}p{margin:6px 0;color:var(--muted)}a{color:var(--accent);overflow-wrap:anywhere}.eyebrow{color:var(--accent);font-weight:650;letter-spacing:.08em;text-transform:uppercase;font-size:11px}.notice{border:1px solid var(--line);background:var(--card);backdrop-filter:saturate(160%) blur(24px);-webkit-backdrop-filter:saturate(160%) blur(24px);padding:15px 17px;border-radius:18px;margin:18px 0;box-shadow:var(--shadow)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}.card{border:1px solid var(--line);background:var(--card);border-radius:18px;padding:16px;min-width:0;box-shadow:0 1px 0 rgba(255,255,255,.35) inset}.metric{font-size:27px;font-weight:650;letter-spacing:-.03em;overflow-wrap:anywhere;word-break:break-word}.label{color:var(--muted);font-size:12px}.good{color:var(--good)}.warn{color:var(--warn)}.bad{color:var(--bad)}.tag{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:3px 9px;margin:2px 4px 2px 0;font-size:11px;background:var(--card-strong)}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:16px;background:var(--card)}table{border-collapse:collapse;width:100%;min-width:760px}th,td{text-align:left;vertical-align:top;padding:10px 11px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-size:11px;position:sticky;top:0;background:var(--card-strong)}tr:last-child td{border-bottom:0}.source-card{display:grid;gap:12px}.source-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.links{display:flex;flex-wrap:wrap;gap:8px}.links a{border:1px solid var(--line);border-radius:10px;padding:5px 9px;text-decoration:none;background:var(--card-strong)}.warning-list{margin:6px 0 0;padding-left:20px;color:var(--warn)}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.9em;overflow-wrap:anywhere}.small{font-size:12px;color:var(--muted)}.action-list{margin:8px 0 0;padding-left:19px}.action-list li{margin:5px 0;color:var(--muted)}@media(prefers-reduced-transparency:reduce){.notice{backdrop-filter:none;-webkit-backdrop-filter:none;background:var(--card-strong)}}@media(max-width:620px){main{padding:22px 12px 48px}.source-head{display:block}.metric{font-size:23px}}
</style></head>
<body><main>
<div class="eyebrow">Materials Evidence Reasoner · source review</div>
<h1>文献提取检查台</h1>
<p id="subtitle">仅审查文件处理质量、来源锚点和可回查入口；不把提取文本升级为科学结论。</p>
<div id="content"></div>
<script id="embedded-data" type="application/json">__DATA__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("embedded-data").textContent), root=document.getElementById("content");
const arr=v=>Array.isArray(v)?v:[], obj=v=>(v&&typeof v==="object"&&!Array.isArray(v))?v:{};
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n}
function safeRelativeHref(value){const text=String(value||"").replaceAll("\\\\","/");if(!text||text.startsWith("/")||text.startsWith("//")||/^[a-z][a-z0-9+.-]*:/i.test(text))return null;return text}
function link(parent,label,href){const clean=safeRelativeHref(href);if(!clean){if(href)parent.appendChild(el("span","small",`${label}（非相对路径，未创建链接）`));return}const a=el("a","",label);a.href=clean;a.target="_blank";a.rel="noopener";parent.appendChild(a)}
function statusClass(value){return value==="failed"||value==="input-error"||value==="download-failed"||value==="inspection-failed"?"bad":value==="partial"||value==="empty"||value==="review-required"||value==="review-recommended"||value==="missing"||value==="skipped"||value==="incomplete"?"warn":"good"}
function card(label,value,cls){const c=el("div","card"),v=el("div","metric "+(cls||""),value),l=el("div","label",label);c.append(v,l);return c}
function section(title,sub){const s=el("section");s.append(el("h2","",title));if(sub)s.append(el("p","",sub));return s}
function badge(value){return el("span","tag "+statusClass(value),value||"未提供")}
function sourceRow(doc){const row=el("tr"),name=el("td");name.append(el("strong","",doc.name||doc.source_id),el("div","small",doc.source_id));const st=el("td");st.append(badge(doc.status),badge(doc.review_status||"未评估"));const kind=el("td");kind.append(el("div","",doc.detected_kind||"未知"),el("div","small",doc.extractor||"未知"));const attempts=arr(doc.backend_attempts).map(item=>`${item.backend||"?"}: ${item.status||"?"}`).join(" → ");if(attempts)kind.append(el("div","small",attempts));const count=el("td","small",`章节 ${doc.section_count||0} · 段落 ${doc.block_count||0} · 表格 ${doc.table_count||0} · 图 ${doc.figure_count||0}`);const hash=el("td","small",doc.sha256||"未记录");const entry=el("td","links");link(entry,"原始文件",doc.path);link(entry,"Markdown",doc.content_path);link(entry,"结构 JSON",doc.structure_path);arr(doc.table_paths).forEach((p,i)=>link(entry,`表 ${i+1}`,p));arr(doc.page_image_paths).forEach((p,i)=>link(entry,`页图 ${i+1}`,p));arr(doc.figure_image_paths).forEach((p,i)=>link(entry,`图像 ${i+1}`,p));const warnings=el("td","small");arr(doc.recommended_actions).forEach(x=>warnings.append(el("div","warn",x)));arr(doc.warnings).forEach(x=>warnings.append(el("div","small",x)));row.append(name,st,kind,count,hash,entry,warnings);return row}
function render(){
 const summary=obj(data.summary), env=obj(data.environment), policy=obj(data.policy), docs=arr(data.documents);
 const overview=section("先看这四步","确认环境 → 打开文献 Markdown → 抽查表格/图像 → 回到原始页码或章节绑定证据。");
 const metrics=el("div","grid");metrics.append(card("文件",summary.file_count||docs.length),card("可交给 LLM",summary.ready_count||0,"good"),card("需要复核",summary.review_needed_count||0,"warn"),card("部分/有限",summary.partial_count||0,"warn"),card("空结果",summary.empty_count||0,"warn"),card("失败",summary.failed_count||0,"bad"),card("表格",summary.table_count||0),card("图注/图像",summary.figure_count||0));overview.append(metrics);root.append(overview);
 const envSec=section("当前处理环境","环境信息来自运行 bundle，不代表每个文件都成功使用了所有库。"), envGrid=el("div","grid");
 const ocrLabel=policy.ocr?(policy.ocr_backend&&env.capabilities&&env.capabilities.pdf_ocr?`已请求 · ${policy.ocr_backend}`:"已请求但当前后端未提供") : "关闭";
 const model=obj(policy.model_download), cache=obj(env.model_cache), modelState=model.status||cache.status||"未记录", modelAction=model.download_performed?(modelState==="ready"?"本次已准备/复用":"本次已尝试"):(model.download_requested?"使用已有缓存":"未需要");
 envGrid.append(card("Python",env.python_executable||"未记录"),card("PDF 策略",policy.pdf_backend||"未记录"),card("OCR",ocrLabel),card("Docling 模型",modelState,statusClass(modelState)),card("模型下载",modelAction),card("图像导出",policy.extract_figures?"已开启":"关闭"));envSec.append(envGrid);
 const packages=obj(env.packages), packageTable=el("div","table-wrap"), pt=el("table"), tr=el("tr");["公开库","版本"].forEach(x=>tr.append(el("th","",x)));pt.append(tr);Object.keys(packages).forEach(name=>{const row=el("tr");row.append(el("td","",name),el("td","",packages[name]||"缺失"));pt.append(row)});packageTable.append(pt);envSec.append(packageTable);
 const capabilities=obj(env.capabilities), capabilityTable=el("div","table-wrap"), ct=el("table"), ch=el("tr");["能力","状态","缺失时建议"].forEach(x=>ch.append(el("th","",x)));ct.append(ch);Object.keys(capabilities).forEach(name=>{const row=el("tr"),hint=obj(env.install_hints)[name]||"按当前环境合同处理";row.append(el("td","",name),el("td","",capabilities[name]?"可用":"缺失"),el("td","",capabilities[name]?"":""+hint));ct.append(row)});capabilityTable.append(ct);envSec.append(el("h3","","按文件类型查看能力"),capabilityTable);
 const profiles=obj(env.profile_status), profileTable=el("div","table-wrap"), pr=el("table"), ph=el("tr");["处理 profile","状态","下一步"].forEach(x=>ph.append(el("th","",x)));pr.append(ph);Object.keys(profiles).forEach(name=>{const spec=obj(profiles[name]),row=el("tr");row.append(el("td","",name),el("td","",spec.status||"未记录"),el("td","",spec.next_step||""));pr.append(row)});profileTable.append(pr);envSec.append(el("h3","","按任务选择处理 profile"),profileTable);
 if(arr(env.warnings).length){const w=el("ul","warning-list");env.warnings.forEach(x=>w.append(el("li","",x)));envSec.append(w)}root.append(envSec);
 const srcSec=section("文件清单","`status=partial/empty/failed` 必须在正式引用前处理；先打开原始文件，再用 Markdown/结构 JSON/CSV 做定位和抽查。"), wrap=el("div","table-wrap"), table=el("table"), head=el("tr");["来源","状态","类型/后端","数量","SHA-256","入口","警告"].forEach(x=>head.append(el("th","",x)));table.append(head);
 docs.forEach(doc=>table.append(sourceRow(doc)));wrap.append(table);srcSec.append(wrap);root.append(srcSec);
 const policySec=section("证据边界","提取产物只提供候选文本、表格和定位；最终 evidence 仍需绑定原始来源、实体、条件和定位。");const ul=el("ul");["原始文件路径与 SHA-256 保存在 bundle。","Markdown 是阅读层；结构 JSON/CSV 是机器审查层。","PDF 页图/图像只用于视觉核对，不能替代来源锚点。","XLSX 公式不会被执行；缺失缓存值不能当作观测值。","转换失败、fallback 和 OCR 都必须进入分析限制。"].forEach(x=>ul.append(el("li","",x)));policySec.append(ul);root.append(policySec);
}
render();
</script></main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="source-extraction.json")
    parser.add_argument("-o", "--output", type=Path, default=Path("source-extraction-dashboard.html"))
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR cannot read source bundle: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict) or not isinstance(data.get("documents"), list):
        print("ERROR input is not a source-extraction bundle", file=sys.stderr)
        return 2
    bundle_root = args.input.resolve().parent
    output = args.output.resolve()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = HTML.replace("__DATA__", payload)
    # The bundle stores paths relative to its own directory. Relocate them so
    # the dashboard remains useful when its HTML is written elsewhere.
    if output.parent != bundle_root:
        for doc in data["documents"]:
            for key in ("path", "content_path", "structure_path"):
                value = doc.get(key)
                if value:
                    doc[key] = os.path.relpath(bundle_root / value, output.parent).replace(os.sep, "/")
            for key in ("table_paths", "page_image_paths", "figure_image_paths"):
                doc[key] = [os.path.relpath(bundle_root / value, output.parent).replace(os.sep, "/") for value in doc.get(key, [])]
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        html = HTML.replace("__DATA__", payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(f"WROTE {output} ({output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
