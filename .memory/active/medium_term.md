# 中期记忆（活跃）

**最后更新**: 2025-11-20 19:53 (UTC+8)

---

## 架构与部署

### DeepSeek-OCR 环境部署完成
- Python 3.12 + CUDA 11.8 + vLLM 0.8.5 环境
- UV 虚拟环境 `.venv-vllm`
- 解决依赖冲突：transformers/tokenizers 版本与 vLLM 兼容
- flash-attn 使用预编译 wheel 避免源码构建失败
- 模型权重预下载到 `models/deepseek-ocr/`
- GPU 2/3（避开 0/1），A100-40G 可处理 90+ 页论文

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `deployment`, `vllm`, `cuda`, `dependency-conflict`, `environment`

---

## 工作流程

### 课题组论文批量转换流程固化
四步流水线（在 `课题组大论文提取/` 目录执行）：
1. `cd 课题组大论文提取 && python edit_config.py <论文>.pdf`（配置路径）
2. `cd /home/xxy/projects/DeepSeek-OCR && CUDA_VISIBLE_DEVICES=2 .venv-vllm/bin/python DeepSeek-OCR-master/DeepSeek-OCR-vllm/run_dpsk_ocr_pdf.py`（推理）
3. `cd 课题组大论文提取 && python split_chapters.py outputs/<论文>/<论文>.mmd outputs/<论文>/chapters`（拆章）
4. `python postprocess_chapter_md.py outputs/<论文>/chapters`（清理）

**目录约定**：
- `课题组大论文提取/papers/` 存放 PDF
- `课题组大论文提取/outputs/<论文名>/` 存放所有输出（`.mmd`、`images/`、`chapters/`）

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `workflow`, `pdf-to-markdown`, `batch-processing`

---

## 工具脚本

### 配置自动化脚本 edit_config.py
- 自动修改 `config.py` 的 `INPUT_PATH` / `OUTPUT_PATH`
- 用法：`python edit_config.py 刘浩杨-毕业论文.pdf`
- 设计原则：职责单一，仅修改配置，不生成后续命令

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `automation`, `config-management`, `script`

### 章节拆分脚本 split_chapters.py
- 智能识别 `##` 级别章节标题
- 保留：摘要（中/英文合并）、正文章节、总结/展望
- 过滤：致谢、目录、参考文献、作者简历
- 支持多种编号格式："第X章"、"X 标题"、"X标题"
- 排除子章节（`## X.Y`）和目录页码行

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `chapter-splitting`, `regex`, `markdown-processing`, `script`

### Markdown 后处理脚本 postprocess_chapter_md.py
- 移除 `<--- Page Split --->` 分页标记
- HTML `<table>` 转 Markdown 表格
- 修正标题级别（`## 1.1` → `### 1.1`）
- 标准化图片路径（`![](images/xxx.jpg)` → `![](../images/xxx.jpg)`）
- 移除 `## 参考文献` 章节

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `markdown-cleanup`, `html-to-markdown`, `heading-fix`, `script`

---

## 配置与经验

### DeepSeek-OCR 推理参数配置经验
- **GPU 选择**：服务器 4 张 A100，使用 2/3（0/1 被占用）
- **推理性能**：60-90 页论文 10-30 分钟
- **Prompt 设计**：保持简洁 `<image>\n<|grounding|>Convert the document to markdown.`
  - ❌ 不推荐在 Prompt 中要求模型标记章节（输出不可控）
  - ✅ 推荐用后处理脚本拆分章节
- **配置文件**：`MODEL_PATH='models/deepseek-ocr'`（本地路径）

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `model-inference`, `gpu-config`, `prompt-engineering`, `performance`

### memory 分支为主工作分支，main 仅用于上游更新
- **memory 分支**（主工作分支）：
  - 包含所有实际工作成果：
    - `课题组大论文提取/` 工作目录（脚本、papers、outputs、文档）
    - `.memory/` 记忆系统
    - `DeepSeek-OCR-master/` 源码
  - 推送到 `git@github.com:x0chaoren0s/DeepSeek-OCR.git`
- **main 分支**（临时中转）：
  - 只跟踪上游 `deepseek-ai/DeepSeek-OCR`
  - 仅用于接收代码更新
- **日常操作**：始终在 `memory` 分支工作
- **上游更新**（罕见）：`git switch main` → `git pull origin main` → `git switch memory` → `git merge main`
- **config.py 被还原**：用 `edit_config.py` 重新配置即可

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `git-workflow`, `branch-strategy`, `memory-primary-branch`

---

## 方法论

### 记忆系统执行方式：AI 智能交互 vs 僵化脚本
- **核心理念**：记忆系统由 AI 直接执行，而非依赖脚本自动化
- **AI 职责**：
  - 分析 Git 提交和文件变更，智能推断工作内容
  - 应用协议标准判断记忆重要性
  - 与用户交互确认推断、补充细节、权衡取舍
  - 手动生成结构化记忆文件
- **为什么不用脚本**：
  - 脚本无法区分"非显而易见的 Bug"与"拼写错误"
  - 脚本无法区分"架构决策"与"临时调试"
  - 脚本无法与用户交互、无法权衡
- **协议中脚本的定位**：工具辅助（生成文件结构、解析日志），不是决策者

**来源**: 【大黑-毕业win10：hainan：dpskocr】| 2025-11-20  
**标签**: `memory-protocol`, `ai-interaction`, `methodology`, `clarification`

---

**统计**：8 条中期记忆 | 0 条短期记忆

