# 跨终端记忆通信系统

## 新终端首次使用

当你在新终端（电脑）首次使用此项目时，需要进行以下配置：

### 1. 拉取项目

```bash
git fetch origin
git checkout memory
git pull origin memory
```

### 2. 创建终端配置文件

复制模板创建你的配置文件：

```bash
cp .memory/config/system.json.example .memory/config/system.json
```

### 3. 编辑配置文件

编辑 `.memory/config/system.json`，设置你的终端标识：

```json
{
  "version": "1.0.0-mvp",
  "current_terminal_id": "YOUR_TERMINAL_ID",    // 改成你的ID，如：xiaohei_local
  "display_name": "【计算机名：环境名】",        // 改成你的显示名称，如：【小黑：本地】
  "memory_branch": "memory",
  "last_harvest": null,
  "last_sync": null,
  "created_at": "2025-11-17T00:00:00Z"         // 改成当前时间
}
```

**终端标识命名规范**：
- **terminal_id**（英文ID）：
  - 格式：`计算机名_环境` （如：xiaohei_local, dahei_ubuntu）
  - 使用小写字母和下划线
  - 要唯一，不与其他终端重复
- **display_name**（中文显示名）：
  - 格式：`【计算机名：环境名】` （如：【小黑：本地】、【大黑-毕业win10：Ubuntu】）
  - 用于在输出中友好显示

### 4. 在Cursor中执行首次同步

在Cursor的对话中输入：

```
SYNC
```

AI会识别这是新终端，引导你完成注册并学习已有的记忆。

## 日常使用

### 工作结束时收获记忆

```
HARVEST
```

### 新的一天开始工作前同步

```
SYNC
```

## 重要说明

- **system.json 是终端独立的配置文件**，类似 `.env`，不会同步到Git
- 每个终端维护自己的 `system.json`
- 其他记忆文件（索引、归档等）会通过Git在终端间同步
- 详细协议说明见：`config/MEMORY-PROTOCOL.md`

## 查看已参与终端

可以从 `index/memory_index.json` 中查看所有产生过记忆的终端（每条记忆都记录了 `source_terminal_display`）。

