from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def inline_markdown(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
    value = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', value)
    return value


def slugify(text: str, index: int) -> str:
    value = re.sub(r"[`*_~\[\]()#.：:，,。！？!?\"'/\\]", "", text).strip().lower()
    value = re.sub(r"\s+", "-", value)
    return value[:72] or f"heading-{index}"


def render_table(rows: list[str]) -> str:
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
    if len(parsed) < 2:
        return "".join(f"<p>{inline_markdown(row)}</p>" for row in rows)
    head = "<thead><tr>" + "".join(f"<th>{inline_markdown(cell)}</th>" for cell in parsed[0]) + "</tr></thead>"
    body = "<tbody>" + "".join(
        "<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>"
        for row in parsed[2:]
    ) + "</tbody>"
    return f'<div class="table-wrap"><table>{head}{body}</table></div>'


def markdown_to_html(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    parts: list[str] = []
    toc: list[tuple[int, str, str]] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_rows: list[str] = []
    code_lines: list[str] = []
    code_lang = "text"
    list_tag = "ul"
    in_code = False
    heading_index = 0

    def flush_paragraph() -> None:
        if paragraph:
            parts.append("<p>" + inline_markdown(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items:
            parts.append(f"<{list_tag}>" + "".join(f"<li>{inline_markdown(item)}</li>" for item in list_items) + f"</{list_tag}>")
            list_items.clear()
            list_tag = "ul"

    def flush_table() -> None:
        if table_rows:
            parts.append(render_table(table_rows))
            table_rows.clear()

    for line in markdown.splitlines():
        if line.startswith("```"):
            if not in_code:
                flush_paragraph(); flush_list(); flush_table()
                in_code = True
                code_lang = line.removeprefix("```").strip() or "text"
                code_lines = []
            else:
                parts.append(f'<pre data-lang="{html.escape(code_lang)}"><code>{html.escape(chr(10).join(code_lines))}</code></pre>')
                in_code = False
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph(); flush_list(); flush_table()
            continue
        if line.strip() == "---":
            flush_paragraph(); flush_list(); flush_table(); parts.append("<hr>")
            continue
        if line.startswith("|") and line.rstrip().endswith("|"):
            flush_paragraph(); flush_list(); table_rows.append(line)
            continue
        flush_table()
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph(); flush_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            heading_index += 1
            anchor = slugify(title, heading_index)
            if level <= 3:
                toc.append((level, title, anchor))
            parts.append(f'<h{level} id="{anchor}">{inline_markdown(title)}</h{level}>')
            continue
        if line.startswith(">"):
            flush_paragraph(); flush_list(); parts.append("<blockquote>" + inline_markdown(line.lstrip("> ").strip()) + "</blockquote>")
            continue
        list_match = re.match(r"^(-|\d+\.)\s+", line)
        if list_match:
            flush_paragraph()
            next_tag = "ol" if list_match.group(1) != "-" else "ul"
            if list_items and next_tag != list_tag:
                flush_list()
            list_tag = next_tag
            list_items.append(re.sub(r"^(-|\d+\.)\s+", "", line).strip())
            continue
        paragraph.append(line.strip())

    flush_paragraph(); flush_list(); flush_table()
    return "\n".join(parts), toc


def build_page(source: Path, output: Path, title: str, subtitle: str, links: list[tuple[str, str]], css_href: str) -> None:
    body, toc = markdown_to_html(source.read_text(encoding="utf-8"))
    toc_html = "".join(
        f'<a class="toc-level-{level}" href="#{anchor}">{html.escape(text)}</a>'
        for level, text, anchor in toc
    )
    links_html = "".join(f'<a href="{html.escape(href)}">{html.escape(label)}</a>' for label, href in links)
    template = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><link rel="stylesheet" href="{html.escape(css_href)}">
<style>
.standalone-reader{{width:min(1380px,calc(100% - 44px));margin:0 auto;padding:18px 0 78px;position:relative;z-index:2}}
.standalone-hero,.standalone-toc,.standalone-content{{border:1px solid var(--line);background:linear-gradient(145deg,rgba(245,235,210,.105),rgba(245,235,210,.045)),linear-gradient(180deg,rgba(16,22,17,.94),rgba(6,8,6,.90));box-shadow:var(--shadow-deep),inset 0 1px rgba(255,255,255,.05);backdrop-filter:blur(18px) saturate(1.08)}}
.standalone-hero{{position:relative;overflow:hidden;border-radius:38px;padding:clamp(28px,4vw,48px);margin-bottom:24px}}
.standalone-layout{{display:grid;grid-template-columns:292px minmax(0,1fr);gap:22px;align-items:start}}
.standalone-toc{{position:sticky;top:18px;border-radius:28px;padding:20px;max-height:calc(100vh - 36px);overflow:auto}}
.standalone-toc-title{{margin-bottom:12px;color:var(--accent-amber);font-family:var(--font-mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase}}
.standalone-toc a{{display:block;border:1px solid transparent;border-radius:13px;padding:8px 10px;color:var(--paper-soft);font-size:14px;line-height:1.45;text-decoration:none}}
.standalone-toc a:hover{{color:var(--paper);border-color:rgba(117,233,255,.20);background:rgba(117,233,255,.08);transform:translateX(2px)}}
.standalone-toc .toc-level-2{{margin-left:10px}}.standalone-toc .toc-level-3{{margin-left:20px;color:var(--paper-muted)!important}}
.standalone-content{{border-radius:34px;padding:clamp(28px,4vw,58px);color:var(--paper-soft);line-height:1.86;font-size:17px}}
.standalone-content h1,.standalone-content h2,.standalone-content h3,.standalone-content h4{{color:var(--paper);line-height:1.24;letter-spacing:-.02em;scroll-margin-top:28px}}
.standalone-content h1,.standalone-content h2{{font-family:var(--font-display)}}.standalone-content h1{{margin:0 0 28px;padding-bottom:18px;border-bottom:1px solid var(--line);font-size:clamp(32px,4vw,54px)}}
.standalone-content h2{{margin:46px 0 16px;padding-left:16px;border-left:4px solid var(--accent-red);font-size:clamp(28px,3vw,38px)}}.standalone-content h3{{margin:32px 0 12px;color:#f8d89b;font-size:23px}}
.standalone-content strong{{color:#fff4df}}.standalone-content a{{color:var(--accent-cyan)}}.standalone-content code{{border:1px solid rgba(117,233,255,.22);border-radius:8px;padding:2px 6px;color:#c9f7ff;background:rgba(117,233,255,.08);font-family:var(--font-mono)}}
.standalone-content pre{{overflow:auto;border:1px solid rgba(117,233,255,.18);border-radius:20px;margin:22px 0;padding:22px;background:rgba(4,8,7,.96)}}.standalone-content pre::before{{content:attr(data-lang);display:block;margin-bottom:12px;color:var(--accent-amber);font-family:var(--font-mono);font-size:12px;text-transform:uppercase}}.standalone-content pre code{{border:0;padding:0;background:transparent}}
.standalone-content blockquote{{margin:24px 0;border-left:4px solid var(--accent-amber);border-radius:16px;padding:14px 18px;color:#f2d8a8;background:rgba(232,184,91,.08)}}
.standalone-content .table-wrap{{overflow:auto;margin:22px 0;border:1px solid var(--line);border-radius:20px}}.standalone-content table{{width:100%;border-collapse:collapse;min-width:720px}}.standalone-content th,.standalone-content td{{border-bottom:1px solid var(--line);padding:13px 15px;text-align:left;vertical-align:top}}.standalone-content th{{color:var(--paper);background:rgba(255,106,61,.09)}}
.top-links{{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 24px}}.top-links a{{border:1px solid rgba(242,230,200,.18);border-radius:999px;padding:10px 14px;color:var(--paper);background:rgba(242,230,200,.07);text-decoration:none}}
@media(max-width:980px){{.standalone-layout{{grid-template-columns:1fr}}.standalone-toc{{position:relative;top:0;max-height:none}}}}
</style></head><body><div class="standalone-reader"><div class="standalone-hero"><a class="back-link" href="{html.escape(links[0][1])}">← 返回课程中心</a><p class="eyebrow">AI Course · HTML</p><h1>{html.escape(title)}</h1><p class="doc-summary">{html.escape(subtitle)}</p><div class="top-links">{links_html}</div></div><div class="standalone-layout"><aside class="standalone-toc"><div class="standalone-toc-title">目录</div><nav>{toc_html}</nav></aside><article class="standalone-content markdown-body">{body}</article></div></div></body></html>'''
    output.write_text(template, encoding="utf-8")


def parse_link(value: str) -> tuple[str, str]:
    label, href = value.split("=", 1)
    return label, href


def main() -> None:
    parser = argparse.ArgumentParser(description="Render course Markdown into standalone HTML")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--css", required=True)
    parser.add_argument("--link", action="append", required=True, type=parse_link)
    args = parser.parse_args()
    build_page(args.source, args.output, args.title, args.subtitle, args.link, args.css)


if __name__ == "__main__":
    main()
