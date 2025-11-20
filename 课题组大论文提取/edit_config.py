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
RUN_SCRIPT_PATH = Path("../DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py")

def update_config(input_path: str, output_path: str, gpu_id: int = 2):
    """更新 config.py 的路径和模型配置"""
    text = CONFIG_PATH.read_text(encoding="utf-8")
    
    # 1. 更新 MODEL_PATH（固定为本地路径）
    text = re.sub(
        r"MODEL_PATH\s*=\s*['\"].*?['\"]",
        "MODEL_PATH = 'models/deepseek-ocr'",
        text,
        count=1,
    )
    
    # 2. 更新 INPUT_PATH
    text = re.sub(
        r"INPUT_PATH\s*=\s*['\"].*?['\"]",
        f"INPUT_PATH = '课题组大论文提取/{input_path}'",
        text,
        count=1,
    )
    
    # 3. 更新 OUTPUT_PATH
    text = re.sub(
        r"OUTPUT_PATH\s*=\s*['\"].*?['\"]",
        f"OUTPUT_PATH = '课题组大论文提取/{output_path}'",
        text,
        count=1,
    )
    
    CONFIG_PATH.write_text(text, encoding="utf-8")
    print(f"✓ 已更新 config.py:")
    print(f"  MODEL_PATH = 'models/deepseek-ocr'")
    print(f"  INPUT_PATH = '课题组大论文提取/{input_path}'")
    print(f"  OUTPUT_PATH = '课题组大论文提取/{output_path}'")
    
    # 4. 更新 run_dpsk_ocr_pdf.py 的 CUDA_VISIBLE_DEVICES
    update_gpu_setting(gpu_id)

def update_gpu_setting(gpu_id: int):
    """更新 run_dpsk_ocr_pdf.py 中的 GPU 设置"""
    text = RUN_SCRIPT_PATH.read_text(encoding="utf-8")
    
    # 查找是否已有 CUDA_VISIBLE_DEVICES 设置
    if re.search(r'os\.environ\["CUDA_VISIBLE_DEVICES"\]', text):
        # 已存在，更新值
        text = re.sub(
            r'os\.environ\["CUDA_VISIBLE_DEVICES"\]\s*=\s*[\'"].*?[\'"]',
            f'os.environ["CUDA_VISIBLE_DEVICES"] = \'{gpu_id}\'',
            text,
            count=1,
        )
    else:
        # 不存在，在文件开头插入（import 语句之后）
        import_lines = []
        other_lines = []
        in_imports = True
        
        for line in text.split('\n'):
            if in_imports and (line.startswith('import ') or line.startswith('from ') or line.strip() == '' or line.startswith('#')):
                import_lines.append(line)
            else:
                if in_imports:
                    in_imports = False
                    import_lines.append(f'\nos.environ["CUDA_VISIBLE_DEVICES"] = \'{gpu_id}\'')
                other_lines.append(line)
        
        text = '\n'.join(import_lines + other_lines)
    
    RUN_SCRIPT_PATH.write_text(text, encoding="utf-8")
    print(f"✓ 已更新 run_dpsk_ocr_pdf.py: CUDA_VISIBLE_DEVICES = '{gpu_id}'")


def main():
    parser = argparse.ArgumentParser(description="配置路径、模型和GPU设置")
    parser.add_argument("pdf", help="位于 papers/ 下的 PDF 文件名，例如 刘浩杨-毕业论文.pdf")
    parser.add_argument(
        "--output",
        help="输出目录（默认 outputs/<PDF无扩展名>）",
        default=None,
    )
    parser.add_argument(
        "--gpu",
        help="GPU 编号（默认 2）",
        type=int,
        default=2,
    )
    args = parser.parse_args()

    pdf_name = args.pdf.strip()
    output_path = args.output.strip() if args.output else f"outputs/{Path(pdf_name).stem}"
    input_path = f"papers/{pdf_name}"

    update_config(input_path, output_path, gpu_id=args.gpu)


if __name__ == "__main__":
    main()

