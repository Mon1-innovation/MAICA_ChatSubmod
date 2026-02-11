# MAICA -1 Session (原始上下文会话)

-1 Session 是 MAICA 的实验性功能，允许用户完全自行管理对话上下文，而不是依赖服务器端的会话管理。

## 功能概述

传统的 MAICA 会话由服务器管理对话历史，每次发送消息时只需提供当前用户输入。而 -1 Session 则要求客户端自行维护完整的对话上下文，包括系统提示、历史消息等。

### 适用场景

- 需要精确控制对话上下文的高级用户
- 实现自定义对话流程
- 多轮对话的上下文管理
- 需要动态调整系统提示的场景

### 限制

- **字符限制**: 序列化后的上下文不能超过 4096 字符
- **无 MFocus 介入**: 不会触发 MTrigger，AI 不会自动调整好感度等
- **实验性功能**: API 可能随时变更

---

## 快速开始

### 基本用法

```python
from maica_context_query import MAICAContextQueryBuilder

# 1. 创建构建器
builder = MAICAContextQueryBuilder()

# 2. 添加系统消息（定义 AI 人格）
builder.add_system_message("你叫莫妮卡，是一名虚拟角色...")

# 3. 添加对话历史（可选）
builder.add_user_message("你好！")
builder.add_assistant_message("你好呀！")

# 4. 添加当前用户输入
builder.add_user_message("今天天气怎么样？")

# 5. 检查长度限制
if builder.is_within_limit():
    # 6. 发送请求
    maica.start_raw_context(builder.build())
```

### 在 Ren'Py 中使用

```renpy
label my_raw_session:
    # 初始化连接
    call maica_init_connect

    python:
        import maica_context_query

        # 构建上下文
        ctx = maica_context_query.MAICAContextQueryBuilder()
        ctx.add_system_message("你是莫妮卡...")
        ctx.add_user_message("你好！")

    # 发送请求并处理响应
    call maica_raw_session(ctx)

    return
```

---

## API 参考

### MAICAContextQueryBuilder

上下文查询构建器，用于逐步构建对话上下文。

#### 构造函数

```python
builder = MAICAContextQueryBuilder()
```

#### 方法

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `add_system_message(content)` | content: str | self | 添加系统消息，定义 AI 角色和行为规则 |
| `add_user_message(content)` | content: str | self | 添加用户消息 |
| `add_assistant_message(content)` | content: str | self | 添加助手（AI）消息 |
| `build()` | - | list | 构建消息列表，用于发送请求 |
| `get_length()` | - | int | 获取序列化后的字符长度 |
| `is_within_limit()` | - | bool | 检查是否在 4096 字符限制内 |
| `clear()` | - | self | 清空所有消息 |
| `message_count()` | - | int | 获取消息数量 |

#### 常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `MAX_LENGTH` | 4096 | 最大字符限制 |

#### 链式调用

所有 `add_*` 方法和 `clear()` 方法都返回 `self`，支持链式调用：

```python
query = (MAICAContextQueryBuilder()
    .add_system_message("...")
    .add_user_message("...")
    .add_assistant_message("...")
    .build())
```

---

### MAICAContextQueryMessage

单条消息对象，通常不需要直接使用。

#### 类常量

```python
MAICAContextQueryMessage.ROLE_SYSTEM = "system"
MAICAContextQueryMessage.ROLE_USER = "user"
MAICAContextQueryMessage.ROLE_ASSISTANT = "assistant"
```

---

### MaicaAi.start_raw_context()

发起 -1 session 请求。

```python
maica.start_raw_context(query, pprt=False)
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | list | 是 | 消息列表，由 `MAICAContextQueryBuilder.build()` 生成 |
| `pprt` | bool | 否 | 是否启用自动断句和实时后处理，默认 `False` |

#### 前置条件

- MAICA 已连接且可用 (`maica.is_ready_to_input()` 返回 `True`)
- query 是有效的消息列表
- 上下文长度不超过 4096 字符


## 完整示例

### 示例 1: 简单对话

```python
from maica_context_query import MAICAContextQueryBuilder

# 构建
builder = MAICAContextQueryBuilder()
builder.add_system_message("你是一个友好的助手。")
builder.add_user_message("你好！")

# 检查并发送
if builder.is_within_limit():
    maica.start_raw_context(builder.build())
```

### 示例 2: 多轮对话

```python
from maica_context_query import MAICAContextQueryBuilder

builder = MAICAContextQueryBuilder()
builder.add_system_message("你是莫妮卡...")

# 第一轮
builder.add_user_message("你好")
builder.add_assistant_message("你好呀！很高兴见到你。")

# 第二轮
builder.add_user_message("你今天过得怎么样？")

if builder.is_within_limit():
    maica.start_raw_context(builder.build())

# 发送后保存 AI 回复，继续添加到 builder 进行下一轮...
```

### 示例 3: Ren'Py 集成

参考 `game/Submods/MAICA_ChatSubmod/raw_session_example.rpy` 文件。

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `game/python-packages/maica_context_query.py` | 上下文构建器模块 |
| `game/python-packages/maica_tasker_sub_sessionsender.py` | 包含 `MAICARawContextProcessor` |
| `game/python-packages/maica.py` | MAICA 主模块，包含 `start_raw_context()` 方法 |
| `game/Submods/MAICA_ChatSubmod/raw_session_example.rpy` | Ren'Py 使用示例 |

---

## 注意事项

1. **长度检查**: 始终在发送前调用 `is_within_limit()` 检查长度
2. **连接状态**: 确保在调用 `start_raw_context()` 前检查连接状态
3. **响应处理**: -1 Session 的响应处理与普通会话相同，使用相同的消息队列机制
4. **无 Trigger**: MFocus 不会介入，不会自动调整好感度或触发 MTrigger
5. **上下文管理**: 需要自行管理对话历史，包括保存和恢复上下文
