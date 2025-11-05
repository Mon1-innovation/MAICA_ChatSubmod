"""
MAICA会话发送者和接收者模块

此模块包含处理聊天会话消息发送和接收的任务类。
提供了多种聊天处理器，支持不同的聊天模式和场景。
"""

from maica_tasker import *
from bot_interface import PY2
import threading
import json
from maica_tasker_sub import MAICAWSCookiesHandler

class ChatLock(object):
    """
    聊天锁，用于保证同时只有一个聊天会话在处理。

    这个锁用于防止并发聊天请求导致的状态混乱，
    确保聊天请求的串行处理。

    Attributes:
        _lock (threading.Lock): 底层线程锁
        running_info (str): 当前正在运行的聊天操作信息
    """

    def __init__(self):
        """初始化聊天锁。"""
        self._lock = threading.Lock()
        self.running_info = ""

    def acquire(self, blocking=True, timeout=None):
        """
        获取锁。

        Args:
            blocking (bool): 是否阻塞等待。默认为True
            timeout (float): 超时时间（秒），None表示永久等待。默认为None

        Returns:
            bool: 是否成功获取锁
        """
        if PY2:
            # Python 2 不支持timeout参数
            return self._lock.acquire(blocking)
        else:
            # Python 3 支持timeout参数
            if timeout is None:
                return self._lock.acquire(blocking)
            else:
                return self._lock.acquire(blocking, timeout)

    def release(self):
        """
        释放锁。

        同时清空running_info，表示没有聊天任务在运行。
        """
        self._lock.release()
        self.running_info = ""

    def __enter__(self):
        """
        上下文管理器入口。

        获取锁并返回自身实例，允许使用with语句。

        Returns:
            ChatLock: 返回自身实例
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口。

        释放锁。

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        self.release()

    def locked(self):
        """
        检查锁是否被占用。

        Returns:
            bool: 如果锁被占用返回True，否则返回False
        """
        return self._lock.locked()


class SessionSenderAndReceiver(MaicaWSTask):
    """
    会话发送者和接收者基类。

    此类提供聊天会话消息发送和接收的基础框架，
    使用ChatLock确保同时只有一个聊天请求在处理。

    Class Attributes:
        multi_lock (ChatLock): 全局聊天锁，保证串行处理
        strict_cookie (str|None): 严格模式下使用的Cookie值

    Instance Attributes:
        processing (bool): 是否正在处理请求
        logger: 日志记录器
        _external_callback: 外部回调函数，接收(processor, event)参数
    """

    # 全局聊天锁，保证同时只有一个聊天会话在处理
    multi_lock = ChatLock()
    

    def __init__(self, task_type, name, manager, except_ws_status=[
            'maica_core_streaming_continue',
            'maica_chat_loop_finished'
        ]):
        """
        初始化会话发送者和接收者。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息类型列表
        """
        super(SessionSenderAndReceiver, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.processing = False
        self._external_callback = None

    def start_request(self, *args, **kwargs):
        """
        启动一个聊天请求。

        使用全局ChatLock确保同时只有一个请求在处理。
        如果有其他请求正在处理，会抛出异常。

        锁在以下情况释放：
        1. 收到 maica_chat_loop_finished 事件
        2. 调用 reset() 方法

        Args:
            *args: 传递给process_request的位置参数
            **kwargs: 传递给process_request的关键字参数

        Raises:
            RuntimeError: 如果已有其他请求在处理中
        """
        # 尝试非阻塞地获取锁，避免竞态条件
        if not SessionSenderAndReceiver.multi_lock.acquire(blocking=False):
            raise RuntimeError("SessionSenderAndReceiver is already processing a request.")
        self.logger.debug("[{}] start_request args: {}, kwargs: {}".format(self.__class__, args, kwargs))

        self.processing = True
        SessionSenderAndReceiver.multi_lock.running_info = self.__str__()
        try:
            self.process_request(*args, **kwargs)
        except Exception as e:
            import traceback
            if self.logger:
                self.logger.error("[SessionSenderAndReceiver] start_request error: {}".format(traceback.format_exc()))
            # 如果发生异常，立即释放锁
            self.processing = False
            SessionSenderAndReceiver.multi_lock.release()

    def on_event(self, event):
        """
        处理MAICA任务事件，特别是WebSocket类型的事件。

        当接收到指定状态且处理中的WebSocket事件时，会触发on_received回调。

        Args:
            event: MAICA任务事件对象，包含以下属性:
                event_type: 事件类型
                data: 事件数据，包含status字段
        """
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            if event.data.status in self.except_ws_status and self.processing:
                self.on_received(event)
    def on_received(self, event):
        """
        处理接收到的WebSocket消息。

        如果设置了外部回调(_external_callback)，则调用它。
        否则抛出NotImplementedError。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象

        Raises:
            NotImplementedError: 如果未设置外部回调且未被子类实现
        """
        if self._external_callback:
            self._external_callback(self, event)
        else:
            wspack = event.data
            raise NotImplementedError

    def process_request(self, request):
        """
        处理聊天请求。

        此方法必须由子类实现，定义具体的请求处理逻辑。

        Args:
            request: 聊天请求数据

        Raises:
            NotImplementedError: 此方法必须由子类实现
        """
        raise NotImplementedError

    def reset(self):
        """
        重置处理状态。

        将processing标志设置为False，并释放全局聊天锁。
        """
        self.processing = False
        # 释放锁
        if SessionSenderAndReceiver.multi_lock.locked():
            SessionSenderAndReceiver.multi_lock.release()


class MAICAGeneralChatProcessor(SessionSenderAndReceiver):
    """
    通用聊天处理器。

    用于处理常规的聊天请求，支持触发器和自定义会话。
    """

    def process_request(self, query, session, trigger, taskowner):
        """
        处理通用聊天请求。

        构建聊天查询请求JSON并通过WebSocket发送。

        Args:
            query (str): 聊天查询内容
            session (int): 聊天会话ID
            trigger: 触发器信息
            taskowner: 任务所有者（通常是MaicaTaskManager）
        """
        data = {
            'type': 'query',
            'chat_session': session,
            'query': query,
            'trigger': trigger
        }
        if MAICAWSCookiesHandler.cookie:
            data['cookie'] = MAICAWSCookiesHandler.cookie
        self.logger.debug("[{}] send data: {}".format(self.__class__, data))
        taskowner.ws_client.send(json.dumps(data))



class MAICAMSpireProcessor(SessionSenderAndReceiver):
    """
    MSpire（灵感）聊天处理器。

    用于处理灵感相关的聊天请求，可以进行模糊搜索和缓存使用。

    Class Attributes:
        mspire_type (str): MSpire类型，默认为"in_fuzzy_all"（模糊全文搜索）
        use_cache (bool): 是否使用缓存结果，默认为False
    """

    mspire_type = "in_fuzzy_all"
    use_cache = False

    def process_request(self, category, session):
        """
        处理MSpire聊天请求。

        构建MSpire查询请求JSON并通过WebSocket发送。

        Args:
            category (list): 灵感分类列表，若为空则不使用分类过滤
            session (int): 聊天会话ID
            taskowner: 任务所有者（通常是MaicaTaskManager）
        """
        import random
        data = {
            "type": "query",
            "chat_session": session,
            "inspire": {
                "type": MAICAMSpireProcessor.mspire_type,
                "sample": 250,
                "title": random.choice(category),
            } if len(category) else True,
            "use_cache": MAICAMSpireProcessor.use_cache,
        }
        if MAICAWSCookiesHandler.cookie:
            data['cookie'] = MAICAWSCookiesHandler.cookie
        self.manager.ws_client.send(json.dumps(data))



class MAICAMPostalProcessor(SessionSenderAndReceiver):
    """
    MPostal（邮递）聊天处理器。

    用于处理MPostal模式的聊天请求，用于特殊的聊天场景。

    Class Attributes:
        use_session (int): 使用的聊天会话ID，默认为0
    """

    use_session = 0

    def process_request(self, query):
        """
        处理MPostal聊天请求。

        构建MPostal查询请求JSON并通过WebSocket发送。

        Args:
            query (str): 聊天内容
        """
        data = {
            'type': 'query',
            'chat_session': MAICAMPostalProcessor.use_session,
            'postmail': query,
        }
        if MAICAWSCookiesHandler.cookie:
            data['cookie'] = MAICAWSCookiesHandler.cookie
        self.logger.debug("[{}] send data: {}".format(self.__class__, data))
        self.manager.ws_client.send(json.dumps(data))

