"""
MAICA会话发送者和接收者模块

此模块包含处理聊天会话消息发送和接收的任务类。
提供了多种聊天处理器，支持不同的聊天模式和场景。
"""

from maica_tasker import *
from bot_interface import PY2
import threading
import json

try:
    text_types = (basestring,)
except NameError:
    text_types = (str,)

try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)

QUERY_TEXT_MAX_BYTES = 4 * 1024
RAW_CONTEXT_MAX_MESSAGES = 10
RAW_CONTEXT_MAX_BYTES = 16 * 1024
_UNSET = object()

CORE_INPUT_STREAM = "stream"
CORE_INPUT_COMPLETE = "complete"
CORE_OUTPUT_INCREMENTAL = "incremental"
CORE_OUTPUT_COMPLETE = "complete"


def _normalize_core_mode(value, allowed, name):
    if value not in allowed:
        raise ValueError("{} must be one of {}".format(name, sorted(allowed)))
    return value


def _utf8_bytes(value):
    if PY2 and isinstance(value, str):
        try:
            value.decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("text must contain valid UTF-8 bytes: {}".format(exc))
        return value
    if isinstance(value, bytes):
        return value
    return value.encode("utf-8")


def validate_query_text(query):
    """Validate a normal session query as at most 4 KiB of UTF-8 text."""
    if not isinstance(query, text_types):
        raise ValueError("query must be text for a normal session")
    if len(_utf8_bytes(query)) > QUERY_TEXT_MAX_BYTES:
        raise ValueError("query exceeds the 4 KiB UTF-8 limit")
    return query


def validate_raw_context(query):
    """Validate a -1 session list and its compact JSON UTF-8 size."""
    if not isinstance(query, list):
        raise ValueError("query must be a list for -1 session")
    if len(query) > RAW_CONTEXT_MAX_MESSAGES:
        raise ValueError("raw context cannot contain more than 10 messages")
    try:
        dumped = json.dumps(
            query, ensure_ascii=False, separators=(",", ":"), allow_nan=False
        )
        size = len(_utf8_bytes(dumped))
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError("raw context must be JSON serializable: {}".format(exc))
    if size > RAW_CONTEXT_MAX_BYTES:
        raise ValueError("raw context exceeds the 16 KiB compact JSON limit")
    return query


def normalize_mspire_weight(value=10):
    """Return an MSpire category weight in the inclusive range 1..100."""
    if isinstance(value, bool) or not isinstance(value, integer_types):
        raise ValueError("ctg_weight must be an integer from 1 to 100")
    if value < 1 or value > 100:
        raise ValueError("ctg_weight must be an integer from 1 to 100")
    return int(value)


def normalize_session(value):
    """Return a strict MAICA chat session integer from -1 through 9."""
    if isinstance(value, bool) or not isinstance(value, integer_types):
        raise ValueError("session must be an integer from -1 to 9")
    if value < -1 or value > 9:
        raise ValueError("session must be an integer from -1 to 9")
    return int(value)


def normalize_mspire_session(value):
    """Return a strict MSpire session integer from 0 through 9."""
    session = normalize_session(value)
    if session < 0:
        raise ValueError("MSpire session must be an integer from 0 to 9")
    return session


def normalize_mspire_categories(category):
    """Copy and validate an ordered MSpire title list."""
    if not isinstance(category, list):
        raise ValueError("category must be a list")
    categories = list(category)
    for item in categories:
        if not isinstance(item, text_types):
            raise ValueError("each category must be non-empty text")
        _utf8_bytes(item)
        if not item.strip():
            raise ValueError("each category must be non-empty text")
    return categories


def normalize_use_cache(value):
    """Return an explicit boolean MSpire cache flag."""
    if not isinstance(value, bool):
        raise ValueError("use_cache must be a boolean")
    return value


MSPIRE_TYPES = (
    "precise_page",
    "fuzzy_page",
    "in_precise_category",
    "in_fuzzy_category",
    "in_fuzzy_all",
)


def normalize_mspire_type(value):
    """Return a backend-supported MSpire search type."""
    if value not in MSPIRE_TYPES:
        raise ValueError("mspire_type must be one of {}".format(list(MSPIRE_TYPES)))
    return value

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
        self._acquire_time = None

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
            result = self._lock.acquire(blocking)
        else:
            # Python 3 支持timeout参数
            if timeout is None:
                result = self._lock.acquire(blocking)
            else:
                result = self._lock.acquire(blocking, timeout)
        if result:
            import time
            self._acquire_time = time.time()
        return result

    def release(self):
        """
        释放锁。

        同时清空running_info，表示没有聊天任务在运行。
        """
        self._lock.release()
        self.running_info = ""
        self._acquire_time = None

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

    @property
    def occupied_time(self):
        """
        获取锁的占用时间（秒）。

        Returns:
            float: 如果锁被占用，返回占用时长（秒）；否则返回0
        """
        if self._acquire_time is not None:
            import time
            return time.time() - self._acquire_time
        return 0


class SessionSenderAndReceiver(MaicaWSTask):
    """
    会话发送者和接收者基类。

    此类提供聊天会话消息发送和接收的基础框架，
    使用ChatLock确保同时只有一个聊天请求在处理。

    Class Attributes:
        multi_lock (ChatLock): 全局聊天锁，保证串行处理

    Instance Attributes:
        processing (bool): 是否正在处理请求
        logger: 日志记录器
        _external_callback: 外部回调函数，接收(processor, event)参数
    """

    # 全局聊天锁，保证同时只有一个聊天会话在处理
    multi_lock = ChatLock()
    

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化会话发送者和接收者。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息类型列表
        """
        if except_ws_status is None:
            except_ws_status = [
                'maica_core_streaming_continue',
                'maica_chat_loop_finished'
            ]
        super(SessionSenderAndReceiver, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.processing = False
        self._external_callback = None
        self.core_input_mode = CORE_INPUT_STREAM
        self.core_output_mode = CORE_OUTPUT_INCREMENTAL
        self._core_output_parts = []
        self._request_timeout = 300.0
        self._request_generation = 0
        self._request_timer = None
        self._request_timed_out = False
        self._timeout_callback = None

    def set_timeout_callback(self, callback):
        self._timeout_callback = callback

    def _configure_core_output(self, input_mode, output_mode, request_timeout):
        self.core_input_mode = _normalize_core_mode(
            input_mode, {CORE_INPUT_STREAM, CORE_INPUT_COMPLETE}, "core_input_mode"
        )
        self.core_output_mode = _normalize_core_mode(
            output_mode, {CORE_OUTPUT_INCREMENTAL, CORE_OUTPUT_COMPLETE}, "core_output_mode"
        )
        if request_timeout is not None:
            if request_timeout <= 0:
                raise ValueError("request_timeout must be positive")
            self._request_timeout = float(request_timeout)

    def _start_request_timeout(self):
        self._request_generation += 1
        generation = self._request_generation
        self._request_timed_out = False
        if self._request_timer is not None:
            self._request_timer.cancel()
        self._request_timer = threading.Timer(
            self._request_timeout, self._on_request_timeout, (generation,)
        )
        self._request_timer.daemon = True
        self._request_timer.start()

    def _cancel_request_timeout(self):
        self._request_generation += 1
        if self._request_timer is not None:
            self._request_timer.cancel()
            self._request_timer = None

    def _on_request_timeout(self, generation):
        if generation != self._request_generation or not self.processing:
            return
        self._request_timed_out = True
        self.processing = False
        self._core_output_parts = []
        self.logger.error(
            "[{}] request timed out after {:.1f} seconds".format(
                self.__class__.__name__, self._request_timeout
            )
        )
        if self._timeout_callback:
            self._timeout_callback(self.__class__.__name__, self._request_timeout)
        if SessionSenderAndReceiver.multi_lock.locked():
            SessionSenderAndReceiver.multi_lock.release()
        if self.manager and self.manager.ws_client:
            try:
                self.manager.close_ws()
            except Exception as error:
                self.logger.error(
                    "[{}] failed to close WebSocket after timeout: {}".format(
                        self.__class__.__name__, error
                    )
                )

    @property
    def request_timed_out(self):
        return self._request_timed_out

    def consume_core_output(self, event):
        """Normalize core output packets for incremental or complete delivery."""
        status = event.data.status
        if status == 'maica_core_streaming_continue':
            content = event.data.content
            if not isinstance(content, text_types):
                self.logger.error(
                    "[{}] ignored non-text core output: {}".format(
                        self.__class__.__name__, type(content).__name__
                    )
                )
                return []
            self._core_output_parts.append(content)
            if self.core_output_mode == CORE_OUTPUT_INCREMENTAL:
                return [content]
            return []
        if status == 'maica_chat_loop_finished':
            if self.core_output_mode == CORE_OUTPUT_COMPLETE:
                output = "".join(self._core_output_parts)
                self._core_output_parts = []
                return [output] if output else []
            self._core_output_parts = []
        return []
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
        input_mode = kwargs.pop("core_input_mode", self.core_input_mode)
        output_mode = kwargs.pop("core_output_mode", self.core_output_mode)
        request_timeout = kwargs.pop("request_timeout", None)
        self._configure_core_output(input_mode, output_mode, request_timeout)
        # 尝试非阻塞地获取锁，避免竞态条件
        if not SessionSenderAndReceiver.multi_lock.acquire(blocking=False):
            raise RuntimeError("SessionSenderAndReceiver is already processing a request.")
        self.logger.debug("[{}] start_request args: {}, kwargs: {}".format(self.__class__.__name__, args, kwargs))

        self.processing = True
        self._core_output_parts = []
        SessionSenderAndReceiver.multi_lock.running_info = self.__str__()
        self._start_request_timeout()
        try:
            self.process_request(*args, **kwargs)
        except Exception:
            # 如果发生异常，立即释放锁
            self.processing = False
            self._cancel_request_timeout()
            if SessionSenderAndReceiver.multi_lock.locked():
                SessionSenderAndReceiver.multi_lock.release()
            raise

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
        super(SessionSenderAndReceiver, self).reset()
        self.processing = False
        self._cancel_request_timeout()
        self._core_output_parts = []
        # 释放锁
        if SessionSenderAndReceiver.multi_lock.locked():
            SessionSenderAndReceiver.multi_lock.release()


class MAICAGeneralChatProcessor(SessionSenderAndReceiver):
    """
    通用聊天处理器。

    用于处理常规的聊天请求，支持触发器和自定义会话。
    """

    @staticmethod
    def build_request(query, session, triggers, visions=None, pprt=False):
        data = {
            'type': 'query',
            'chat_session': session,
            'query': query,
            'triggers': triggers,
            'pprt': pprt,
        }
        if visions:
            data['vision'] = visions
        return data

    def process_request(self, query, session, triggers, taskowner, visions=None, pprt=False):
        """
        处理通用聊天请求。

        构建聊天查询请求JSON并通过WebSocket发送。

        Args:
            query (str): 聊天查询内容
            session (int): 聊天会话ID
            triggers: 触发器信息
            taskowner: 任务所有者（通常是MaicaTaskManager）
            visions (list|None): 视觉列表，可选
            pprt (bool): 是否启用自动断句和实时后处理
        """
        session = normalize_session(session)
        if session == -1:
            validate_raw_context(query)
        else:
            validate_query_text(query)
        data = self.build_request(query, session, triggers, visions, pprt)
        dumped_data = json.dumps(data, ensure_ascii=False)
        taskowner.ws_client.send(dumped_data)

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
    ctg_weight = 10

    def process_request(self, category, session, pprt=False, flush=False,
                        ctg_weight=_UNSET, use_cache=_UNSET,
                        mspire_type=_UNSET):
        """
        处理MSpire聊天请求。

        构建MSpire查询请求JSON并通过WebSocket发送。

        Args:
            category (list): 灵感分类列表，若为空则不使用分类过滤
            session (int): 聊天会话ID
            taskowner: 任务所有者（通常是MaicaTaskManager）
        """
        if ctg_weight is _UNSET:
            ctg_weight = self.ctg_weight
        weight = normalize_mspire_weight(ctg_weight)
        session = normalize_mspire_session(session)
        categories = normalize_mspire_categories(category)
        if use_cache is _UNSET:
            use_cache = self.use_cache
        cache_enabled = normalize_use_cache(use_cache)
        if mspire_type is _UNSET:
            mspire_type = self.mspire_type
        search_type = normalize_mspire_type(mspire_type)
        if cache_enabled and session != 0:
            raise ValueError("use_cache is only available for session 0")

        if flush and str(session) != '0':
            data = {
                "type": "query",
                "chat_session": session,
                "reset": True
            }
            self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))

        if categories:
            data = {
                "type": "query",
                "chat_session": session,
                "inspire": {
                    "type": search_type,
                    "sample": 250,
                    "title": categories,
                    "ctg_weight": weight,
                    "use_cache": cache_enabled,
                },
                "pprt": pprt
            }
        else:
            data = {
                "type": "query",
                "chat_session": session,
                "inspire": {},
                "pprt": pprt
            }
        self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))



class MAICAMPostalProcessor(SessionSenderAndReceiver):
    """
    MPostal（邮递）聊天处理器。

    用于处理MPostal模式的聊天请求，用于特殊的聊天场景。

    Class Attributes:
        use_session (int): 使用的聊天会话ID，默认为0
    """

    use_session = 0

    def __init__(self, *args, **kwargs):
        super(MAICAMPostalProcessor, self).__init__(*args, **kwargs)
        self.core_input_mode = CORE_INPUT_COMPLETE
        self.core_output_mode = CORE_OUTPUT_COMPLETE

    def process_request(self, query, visions=None):
        """
        处理MPostal聊天请求。

        构建MPostal查询请求JSON并通过WebSocket发送。

        Args:
            query (str): 聊天内容
        """
        query = dict(query)
        query.setdefault('twk_super', True)
        query['bypass_stream'] = self.core_input_mode == CORE_INPUT_COMPLETE
        data = {
            'type': 'query',
            'chat_session': MAICAMPostalProcessor.use_session,
            'postmail': query,
        }
        if visions:
            data['vision'] = visions
        self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))


class MAICARawContextProcessor(SessionSenderAndReceiver):
    """
    原始上下文处理器，用于 -1 session。

    实验性功能，允许用户自行管理 session 上下文。
    query 必须为消息列表。

    Note:
        - chat_session = -1
        - MFocus 不会介入 (无 trigger)
        - 最多 10 条消息，紧凑 JSON 的 UTF-8 编码不超过 16 KiB
    """

    MAX_CONTEXT_MESSAGES = RAW_CONTEXT_MAX_MESSAGES
    MAX_CONTEXT_BYTES = RAW_CONTEXT_MAX_BYTES

    def process_request(self, query, taskowner, visions=None, pprt=False):
        """
        处理原始上下文查询请求。

        Args:
            query (list): 消息列表，格式:
                [{"role": "system/user/assistant", "content": "..."}, ...]
            taskowner: 任务管理器实例
            visions: 可选，图像数据
            pprt (bool): 是否启用自动断句和实时后处理

        Raises:
            ValueError: 如果 query 非列表、超过 10 条、无法序列化或超过 16 KiB
        """
        validate_raw_context(query)

        data = {
            'type': 'query',
            'chat_session': -1,
            'query': query,
            'pprt': pprt
        }
        if visions:
            data['vision'] = visions
        taskowner.ws_client.send(json.dumps(data, ensure_ascii=False))

