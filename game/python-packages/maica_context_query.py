"""
MAICA 上下文查询构建器模块

提供构建和管理 -1 session 查询对象的工具。
"""

import json

try:
    basestring
except NameError:
    basestring = str


class MAICAContextQueryMessage(object):
    """上下文查询单条消息"""

    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, role, content):
        valid_roles = [self.ROLE_SYSTEM, self.ROLE_USER, self.ROLE_ASSISTANT]
        if role not in valid_roles:
            raise ValueError("role must be one of: {}".format(valid_roles))
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}


class MAICAContextQueryBuilder(object):
    """
    -1 session 上下文查询构建器

    Example:
        builder = MAICAContextQueryBuilder()
        builder.add_system_message("You are Monika...")
        builder.add_user_message("Hello!")
        query = builder.build()
    """

    MAX_MESSAGES = 10
    MAX_BYTES = 16 * 1024

    def __init__(self):
        self._messages = []

    def add_system_message(self, content):
        """添加系统消息"""
        self._messages.append(MAICAContextQueryMessage(
            MAICAContextQueryMessage.ROLE_SYSTEM, content
        ))
        return self

    def add_user_message(self, content):
        """添加用户消息"""
        self._messages.append(MAICAContextQueryMessage(
            MAICAContextQueryMessage.ROLE_USER, content
        ))
        return self

    def add_assistant_message(self, content):
        """添加助手消息"""
        self._messages.append(MAICAContextQueryMessage(
            MAICAContextQueryMessage.ROLE_ASSISTANT, content
        ))
        return self

    def build(self):
        """构建查询列表"""
        return [msg.to_dict() for msg in self._messages]

    def get_length(self):
        """获取紧凑 JSON 的 UTF-8 字节数。"""
        dumped = json.dumps(
            self.build(), ensure_ascii=False, separators=(",", ":")
        )
        if not isinstance(dumped, bytes):
            dumped = dumped.encode("utf-8")
        return len(dumped)

    def is_within_limit(self):
        """检查消息数和紧凑 JSON UTF-8 字节数是否均在限制内。"""
        return (self.message_count() <= self.MAX_MESSAGES and
                self.get_length() <= self.MAX_BYTES)

    def clear(self):
        """清空所有消息"""
        self._messages = []
        return self

    def message_count(self):
        """获取消息数量"""
        return len(self._messages)
