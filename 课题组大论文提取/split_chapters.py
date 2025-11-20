#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文分章节后处理脚本
读取转换后的.mmd文件，识别章节并分割保存为单独文件
"""

import os
import re
import sys
from pathlib import Path


def normalize_title(title: str) -> str:
    """去除标题中的空格和特殊空白，便于匹配"""
    return re.sub(r'\s+', '', title).strip()


def clean_title_text(text: str) -> str:
    """清理标题中的末尾页码等多余信息"""
    text = re.sub(r'[\.。·]\s*\d+$', '', text.strip())
    text = re.sub(r'\s+\d+$', '', text.strip())
    return text.strip()


def normalize_heading_line(line: str) -> str:
    """
    将类似“## 第5章 总结与展望”转换为标准 markdown 标题 “## 5 总结与展望”
    仅处理已有 markdown 标题的行，避免目录中的“第X章”被误识别
    """
    stripped = line.strip()
    if not stripped.startswith('#'):
        return line

    heading_body = stripped.lstrip('#').strip()
    match = re.match(r'^第\s*(\d+)\s*章\s*(.*)$', heading_body)
    if match:
        number = match.group(1)
        title = clean_title_text(match.group(2))
        heading = f"{number} {title}".strip()
        return f"## {heading}"
    return line


def extract_chapter_name(line):
    """从章节标题行提取章节名称"""
    # 移除markdown标题标记
    line = re.sub(r'^#+\s*', '', line).strip()
    return clean_title_text(line)


def is_chapter_title(line):
    """判断是否是章节标题"""
    line = line.strip()
    if not line.startswith('##'):
        return False
    # 提取标题内容
    match = re.match(r'^##\s+(.*)$', line)
    if not match:
        return False
    title = match.group(1).strip()
    norm = normalize_title(title)
    # 排除空标题
    if not norm:
        return False
    # 摘要或Abstract
    if '摘要' in norm or 'abstract' in norm.lower():
        return True
    # 目录/目次等也算标题（用于后续跳过）
    directory_keywords = ['目录', '目次', '图目录', '表目录']
    for keyword in directory_keywords:
        if keyword in norm:
            return True
    # 判断是否是主章节（数字开头，但不是子章节 1.1）
    if re.match(r'^\d+(?!\.)', norm):
        return True
    if re.match(r'^\d+[^\d\.]', norm):
        return True
    # 判断是否是总结、展望等结尾章节
    if ('总结' in norm or '展望' in norm) and not re.match(r'^\d+\.\d+', norm):
        return True
    return False


def should_keep_chapter(chapter_name):
    """判断是否应该保留该章节"""
    norm = normalize_title(chapter_name)
    norm_lower = norm.lower()

    # 若标题末尾是“ . 数字”或“。数字”之类（通常来自目录页码），忽略
    if re.search(r'[\.。·]\s*\d+$', chapter_name.strip()):
        return False
    
    # 需要保留的章节关键词
    keep_keywords = ['摘要', 'abstract', '绪论', '深水网箱', '开放海域', '总结', '展望']
    
    # 需要跳过的章节关键词
    skip_keywords = ['致谢', '独创性声明', '版权使用授权', '目录', '目次', '图目录', '表目录',
                     '参考文献', '作者简历', '教育经历', '学术成果', '科研项目']
    
    for skip in skip_keywords:
        if skip in norm or skip.lower() in norm_lower:
            return False
    
    for keep in keep_keywords:
        if (keep in norm or keep in norm_lower):
            if keep in ['总结', '展望'] and re.match(r'^\d+\.\d+', norm):
                continue
            return True
    
    # 数字开头且不是子章节（如 1绪论、2深水网箱）
    if re.match(r'^[1-9](?!\.)', norm):
        return True
    
    return False


def get_chapter_filename(chapter_name):
    """根据章节名称生成文件名"""
    norm = normalize_title(chapter_name)
    norm_lower = norm.lower()
    
    # 摘要或Abstract统一命名
    if '摘要' in norm or 'abstract' in norm_lower:
        return '0-中英文摘要'
    
    # 尝试从章节名称提取编号（如 "1 绪论"、"3开放海域"、"4总结与展望"）
    num_match = re.search(r'^(\d+)', norm)
    if num_match:
        chapter_num = num_match.group(1)
        # 提取章节名称（去掉编号，可能没有空格）
        name_part = re.sub(r'^(\d+)', '', norm).strip()
        if not name_part:
            name_part = chapter_name.strip()
        # 简化章节名称（取前20个字符，避免文件名过长）
        if len(name_part) > 20:
            name_part = name_part[:20]
        return f'{chapter_num}-{name_part}'
    
    # 默认使用章节名称（清理特殊字符）
    filename = re.sub(r'[<>:"/\\|?*]', '', chapter_name).strip()
    if len(filename) > 30:
        filename = filename[:30]
    return filename


def split_chapters(input_file, output_dir):
    """分割章节主函数"""
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    chapters = {}
    current_chapter = None
    current_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        normalized_line = normalize_heading_line(line)
        if normalized_line != line:
            line = normalized_line
            lines[i] = normalized_line  # 保留修改后的标题
        
        # 检查是否是章节标题
        if is_chapter_title(line):
            chapter_name = extract_chapter_name(line)
            
            # 判断是否应该保留
            if should_keep_chapter(chapter_name):
                # 保存上一个章节
                if current_chapter is not None and current_content:
                    chapters[current_chapter] = '\n'.join(current_content)
                
                # 开始新章节
                current_chapter = chapter_name
                current_content = [line]  # 包含章节标题
            else:
                # 不需要的章节，清空当前章节
                if current_chapter is not None:
                    # 保存上一个章节
                    if current_content:
                        chapters[current_chapter] = '\n'.join(current_content)
                    current_chapter = None
                    current_content = []
        else:
            # 普通内容行
            if current_chapter is not None:
                current_content.append(line)
        
        i += 1
    
    # 保存最后一个章节
    if current_chapter is not None and current_content:
        chapters[current_chapter] = '\n'.join(current_content)
    
    # 处理摘要和Abstract合并
    cn_key = None
    en_key = None
    for key in list(chapters.keys()):
        norm = normalize_title(key)
        if cn_key is None and '摘要' in norm:
            cn_key = key
        elif en_key is None and 'abstract' in norm.lower():
            en_key = key
    
    if cn_key and en_key:
        abstract_content = chapters[cn_key] + '\n\n' + chapters[en_key]
        chapters['0-中英文摘要'] = abstract_content
        del chapters[cn_key]
        if en_key in chapters:
            del chapters[en_key]
    elif cn_key:
        chapters['0-中英文摘要'] = chapters[cn_key]
        del chapters[cn_key]
    elif en_key:
        chapters['0-中英文摘要'] = chapters[en_key]
        del chapters[en_key]
    
    # 保存章节文件
    if not chapters:
        print("警告：未检测到任何章节！")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"检测到 {len(chapters)} 个章节，开始保存...")
    
    # 使用字典去重，确保相同文件名只保存一次（保留最后一个）
    saved_files = {}
    for chapter_name, chapter_content in chapters.items():
        filename = get_chapter_filename(chapter_name)
        saved_files[filename] = (chapter_name, chapter_content)
    
    for filename, (chapter_name, chapter_content) in saved_files.items():
        output_file = os.path.join(output_dir, f'{filename}.md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
        
        print(f"  ✓ 已保存: {filename}.md (来源: {chapter_name})")
    
    print(f"\n完成！所有章节文件已保存到: {output_dir}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python split_chapters.py <输入.mmd文件> [输出目录]")
        print("示例: python split_chapters.py outputs/论文名/论文名.mmd outputs/论文名/chapters")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        # 默认输出到输入文件同目录下的chapters子目录
        input_path = Path(input_file)
        output_dir = str(input_path.parent / 'chapters')
    
    if not os.path.exists(input_file):
        print(f"错误：文件不存在: {input_file}")
        sys.exit(1)
    
    print(f"输入文件: {input_file}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    split_chapters(input_file, output_dir)


if __name__ == '__main__':
    main()

