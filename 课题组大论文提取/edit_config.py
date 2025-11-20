#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 PDF 文件名自动更新 DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py 中的
INPUT_PATH / OUTPUT_PATH，避免手动编辑。

示例：
    python edit_config.py 刘浩杨-毕业论文.pdf
    python edit_config.py 周雅君-毕业论文.pdf --output outputs/周雅君-毕业论文
"""

import argparse
import re
from pathlib import Path

CONFIG_PATH = Path("../DeepSeek-OCR-master/DeepSeek-OCR-vllm/config.py")
def update_config(input_path: str, output_path: str):
    text = CONFIG_PATH.read_text(encoding="utf-8")
    text = re.sub(
        r"INPUT_PATH\s*=\s*'.*?'",
        f"INPUT_PATH = '课题组大论文提取/{input_path}'",
        text,
        count=1,
    )
    text = re.sub(
        r"OUTPUT_PATH\s*=\s*'.*?'",
        f"OUTPUT_PATH = '课题组大论文提取/{output_path}'",
        text,
        count=1,
    )
    CONFIG_PATH.write_text(text, encoding="utf-8")
    print(f"已更新 config.py -> INPUT_PATH='课题组大论文提取/{input_path}', OUTPUT_PATH='课题组大论文提取/{output_path}'")


def main():
    parser = argparse.ArgumentParser(description="配置路径并记录执行指令")
    parser.add_argument("pdf", help="位于 papers/ 下的 PDF 文件名，例如 刘浩杨-毕业论文.pdf")
    parser.add_argument(
        "--output",
        help="输出目录（默认 outputs/<PDF无扩展名>）",
        default=None,
    )
    args = parser.parse_args()

    pdf_name = args.pdf.strip()
    output_path = args.output.strip() if args.output else f"outputs/{Path(pdf_name).stem}"

    input_path = f"papers/{pdf_name}"

    update_config(input_path, output_path)


if __name__ == "__main__":
    main()

