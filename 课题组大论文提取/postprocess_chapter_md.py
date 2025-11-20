#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节 Markdown 后处理脚本
功能：
1. 移除模型输出中的 <--- Page Split ---> 分隔标记
2. 将 HTML <table> ... </table> 转换为 Markdown 表格

使用方法：
    python postprocess_chapter_md.py path/to/file.md
    python postprocess_chapter_md.py path/to/directory
"""

import argparse
import os
import re
from pathlib import Path


def clean_cell(cell: str) -> str:
    """清理单元格内容，保留 <br>，去掉其他多余标签。"""
    cell = cell.replace("&nbsp;", " ")
    cell = re.sub(r"<br\s*/?>", "[[BR]]", cell, flags=re.IGNORECASE)
    cell = re.sub(r"</?(?:span|div|p)[^>]*>", "", cell, flags=re.IGNORECASE)
    cell = re.sub(r"<.*?>", "", cell, flags=re.DOTALL)
    cell = cell.replace("[[BR]]", "<br>").strip()
    return cell


def convert_table(table_html: str) -> str:
    """将 HTML 表格转换为 Markdown 表格。"""
    rows = re.findall(r"<tr>(.*?)</tr>", table_html, flags=re.DOTALL | re.IGNORECASE)
    if not rows:
        return table_html

    table_data = []
    max_cols = 0
    for row in rows:
        cells = re.findall(r"<t[dh]>(.*?)</t[dh]>", row, flags=re.DOTALL | re.IGNORECASE)
        cleaned = [clean_cell(cell) for cell in cells]
        table_data.append(cleaned)
        max_cols = max(max_cols, len(cleaned))

    if not table_data:
        return table_html

    # 对齐列数
    for row in table_data:
        row.extend([""] * (max_cols - len(row)))

    header = table_data[0]
    separator = ["-" * max(3, len(col) if col else 3) for col in header]

    md_lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(separator) + "|",
    ]

    for row in table_data[1:]:
        md_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(md_lines)


def remove_page_splits(text: str) -> str:
    """移除 <--- Page Split ---> 标记。"""
    return re.sub(r"\s*<---\s*Page\s+Split\s*--->\s*", "\n", text, flags=re.IGNORECASE)


def convert_tables(text: str) -> str:
    """转换文本中的所有 HTML 表格。"""
    pattern = re.compile(r"<table[^>]*>.*?</table>", flags=re.DOTALL | re.IGNORECASE)

    def replacer(match):
        return convert_table(match.group(0))

    return pattern.sub(replacer, text)


def normalize_image_paths(text: str) -> str:
    """将图片路径统一为 ../images/xxx"""
    # 先将已经带 ../ 的也规范化为单个 ../
    def repl(match):
        alt = match.group(1)
        filename = match.group(2)
        return f"{alt}../images/{filename})"

    pattern = re.compile(
        r"(!\[[^\]]*\]\()(?:(?:\.\./)*|\.?/)?images/([^)\s]+)\)",
        flags=re.IGNORECASE,
    )
    return pattern.sub(repl, text)


def fix_heading_levels(text: str) -> str:
    """确保章节与子章节使用正确的 Markdown 级别并在编号与标题之间留空格。"""

    def repl(match):
        hashes = match.group(1)
        number = match.group(2)
        rest = (match.group(3) or "").strip()
        dot_count = number.count(".")
        target_level = min(6, 2 + dot_count)  # 1 -> ##, 1.1 -> ###, 1.1.1 -> ####
        new_hashes = "#" * target_level
        suffix = f" {rest}" if rest else ""
        return f"{new_hashes} {number}{suffix}"

    pattern = re.compile(r"^(#{2,})\s*(\d+(?:\.\d+)*)(.*)$", flags=re.MULTILINE)
    return pattern.sub(repl, text)


def remove_reference_section(text: str) -> str:
    """若章节末尾附带参考文献部分，则移除。"""
    pattern = re.compile(r"(\n##\s*(参考文献|references?)\b.*)$", flags=re.IGNORECASE | re.DOTALL)
    return pattern.sub("", text)


def process_file(path: Path):
    """处理单个 Markdown 文件。"""
    with path.open("r", encoding="utf-8") as f:
        content = f.read()

    original = content
    content = remove_page_splits(content)
    content = convert_tables(content)
    content = normalize_image_paths(content)
    content = fix_heading_levels(content)
    content = remove_reference_section(content)

    if content != original:
        with path.open("w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ 已处理 {path}")
    else:
        print(f"- 无需修改 {path}")


def collect_md_files(target: Path):
    """收集待处理的 Markdown 文件列表。"""
    if target.is_file():
        return [target] if target.suffix.lower() == ".md" else []
    files = []
    for md_file in target.rglob("*.md"):
        files.append(md_file)
    return files


def main():
    parser = argparse.ArgumentParser(description="Markdown 章节后处理")
    parser.add_argument("paths", nargs="+", help="Markdown 文件或目录")
    args = parser.parse_args()

    all_files = []
    for path_str in args.paths:
        target = Path(path_str).resolve()
        if not target.exists():
            print(f"警告：路径不存在 {target}")
            continue
        all_files.extend(collect_md_files(target))

    if not all_files:
        print("未找到需要处理的 Markdown 文件。")
        return

    for md_file in all_files:
        process_file(md_file)


if __name__ == "__main__":
    main()

