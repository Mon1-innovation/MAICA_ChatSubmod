"""
MAICA任务子模块 - WebSocket任务的具体实现

此模块包含各种具体的WebSocket任务处理器，用于处理不同类型的WebSocket消息。
"""

from maica_tasker import *
import bot_interface
import time
import threading
import json
from maica_mtrigger import MTriggerAction


def _format_ws_message(status, content, code=None, custom_prefix=None):
    status = bot_interface.to_unicode(status)
    content = bot_interface.to_unicode(content)
    if custom_prefix is None:
        if code is None:
            return u"<{}> {}".format(status, content)
        return u"<{}({})> {}".format(status, code, content)
    return u"<DISABLE_VERBOSITY>{}{}".format(custom_prefix, content)


class GeneralTaskEventLogger(MaicaTask):
    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_TASK:
            data = getattr(event, "data", None)
            event_name = getattr(data, "name", type(data).__name__)
            content = getattr(data, "content", None)
            if event_name == "websocket_closed" and isinstance(content, dict):
                content = {
                    "close_status_code": content.get("close_status_code"),
                    "close_msg": content.get("close_msg"),
                }
            owner = getattr(getattr(event, "taskowner", None), "name", None)
            self.logger.debug(
                "[TaskEvent] owner={} name={} content={}".format(
                    owner or type(getattr(event, "taskowner", None)).__name__,
                    event_name,
                    content,
                )
            )
class GeneralTaskErrorHandler(MaicaTask):
    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_TASK and event.type == 'error':
            data = getattr(event, "data", None)
            self.logger.debug(
                "[GeneralTaskErrorHandler] handling task error {}".format(
                    getattr(data, "name", type(data).__name__)
                )
            )
            self.manager.close_ws()

class GeneralWsErrorHandler(MaicaWSTask):
    """
    通用WebSocket错误处理器。

    监听WebSocket错误消息，在接收到错误类型的消息或服务器返回5xx错误时，
    关闭WebSocket连接并记录错误日志。

    Attributes:
        logger: 日志记录器实例
    """

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化错误处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
            logger: 日志记录器
        """
        super(GeneralWsErrorHandler, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self._error_callback = None

    def set_error_callback(self, callback):
        self._error_callback = callback

    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            self.on_received(event)
    def on_received(self, event):
        """
        处理接收到的WebSocket消息。

        检查消息状态是否为'error'或状态码是否在5xx范围内，
        如果是则关闭WebSocket连接并记录错误。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.event_type != MAICATASKEVENT_TYPE_WS:
            return
        else:
            wspack = event.data
            try:
                is_server_error = 500 <= int(wspack.code) < 600
            except (TypeError, ValueError):
                is_server_error = False
            if wspack.type == 'error' or is_server_error:
                if self._error_callback:
                    if self._error_callback(wspack.status, wspack.content, wspack.code) is False:
                        return
                if self.logger:
                    self.logger.debug(
                        u"[GeneralWsErrorHandler] requesting close after status={} code={}".format(
                            wspack.status,
                            wspack.code,
                        )
                    )
                event.taskowner.close_ws()
class GeneralWsConsoleLogger(MaicaWSTask):

    def __init__(self, task_type, name, manager, except_ws_status=None, console_logger=None):
        super(GeneralWsConsoleLogger, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.console_logger = console_logger
        self.ui_lang_zh = False
    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            ws = event.data
            self.on_received(event)
    def on_received(self, event):
        """
        处理接收到的WebSocket消息并记录日志。

        根据消息状态选择相应的日志级别进行记录。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.event_type != MAICATASKEVENT_TYPE_WS:
            return
        if event.data.status in ['maica_core_streaming_continue']:
            return
        if event.data.status in ('maica_connection_initiated', 'pong'):
            try:
                welcome_zh, welcome_en = event.data.content.split("|", 1)
                event.data.content = welcome_zh if self.ui_lang_zh else welcome_en
            except Exception:
                pass
        wspack = event.data
        if self.console_logger:
            log_message = _format_ws_message(wspack.status, wspack.content)
            if wspack.type == 'info':
                self.console_logger.info(log_message)
            elif wspack.type == 'warn':
                self.console_logger.warning(log_message)
            elif wspack.type == 'error':
                self.console_logger.error(log_message)
            else:
                self.console_logger.debug(log_message)



class GeneralWsLogger(MaicaWSTask):
    """
    通用WebSocket日志记录器。

    根据WebSocket消息的类型（info、warn、error、debug）进行日志记录，
    用于跟踪和调试WebSocket通信过程。

    Attributes:
        logger: 日志记录器实例
    """

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化日志记录器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
            logger: 日志记录器
        """
        super(GeneralWsLogger, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            ws = event.data
            self.on_received(event)
    def on_received(self, event):
        """
        处理接收到的WebSocket消息并记录日志。

        根据消息状态选择相应的日志级别进行记录。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.event_type != MAICATASKEVENT_TYPE_WS:
            return
        else:
            wspack = event.data
            if self.logger:
                log_message = u"[GeneralWsLogger] " + _format_ws_message(
                    wspack.status,
                    wspack.content,
                    wspack.code
                )
                if wspack.type == 'info':
                    self.logger.info(log_message)
                elif wspack.type == 'warn':
                    self.logger.warning(log_message)
                elif wspack.type == 'error':
                    self.logger.error(log_message)
                else:
                    self.logger.debug(log_message)


class MAICALoopWarnHandler(MaicaWSTask):
    """Handle an operation-level loop reset without closing the transport."""

    def set_reset_callback(self, callback):
        self._reset_callback = callback

    def on_received(self, event):
        wspack = event.data
        if self.logger:
            self.logger.debug(
                "[MAICALoopWarnHandler] operation reset after status={} code={}; "
                "keeping WebSocket open".format(
                    wspack.status,
                    wspack.code,
                )
            )
        callback = getattr(self, "_reset_callback", None)
        if callback:
            callback(event)


class HistoryStatusHandler(MaicaWSTask):
    """
    历史记录状态处理器。

    监听历史记录切片相关的消息，跟踪token使用状态：
    - TOKEN_NORMAL: 正常状态
    - TOKEN_WARN_EXCEEDED: token超过24000
    - TOKEN_MAX_EXCEEDED: token达到最大限制

    Attributes:
        status (int): 当前token状态
    """

    # Token状态常量
    TOKEN_NORMAL = 0
    TOKEN_WARN_EXCEEDED = 1
    TOKEN_MAX_EXCEEDED = 2

    def __init__(self, task_type, name, manager):
        """
        初始化历史状态处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
        """
        super(HistoryStatusHandler, self).__init__(
            task_type, name, manager=manager,
            except_ws_status=['maica_history_slice_hint', 'maica_history_sliced']
        )
        self.status = self.TOKEN_NORMAL

    def on_received(self, event):
        """
        处理历史记录状态消息。

        根据消息状态更新token状态。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.data.status == 'maica_history_slice_hint':
            self.status = self.TOKEN_WARN_EXCEEDED
        elif event.data.status == 'maica_history_sliced':
            self.status = self.TOKEN_MAX_EXCEEDED


class MAICAUserDataHandler(MaicaWSTask):
    """
    MAICA用户数据处理器。

    监听用户信息相关的WebSocket消息，提取并存储用户的账号、ID和昵称信息。

    Attributes:
        id (str|None): 用户ID
        nickname (str|None): 用户昵称
        account (str|None): 用户账号
    """

    def __init__(self, task_type, name, manager):
        """
        初始化用户数据处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
        """
        super(MAICAUserDataHandler, self).__init__(
            task_type, name, manager=manager,
            except_ws_status=['maica_login_user', 'maica_login_id', 'maica_login_nickname']
        )
        self.id = None
        self.nickname = None
        self.account = None

    def on_received(self, event):
        """
        处理用户信息消息。

        根据消息状态提取相应的用户信息。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.data.status == 'maica_login_user':
            self.account = event.data.content
        elif event.data.status == 'maica_login_id':
            self.id = event.data.content
        elif event.data.status == 'maica_login_nickname':
            self.nickname = event.data.content
    
    def reset(self):
        super(MAICAUserDataHandler, self).reset()
        self.account = None
        self.id = None
        self.nickname = None


class MTriggerWsHandler(MaicaWSTask):
    """
    MAICA触发器WebSocket处理器。

    监听触发器相关的WebSocket消息，当接收到触发器信息时，
    将其传递给触发器管理器进行处理。

    Attributes:
        manager: 触发器管理器实例
    """

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化触发器处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): WebSocket任务管理器实例
        """
        super(MTriggerWsHandler, self).__init__(
            task_type, name, manager=manager,
            except_ws_status=except_ws_status
        )
        self._trigger_func = self.none_triggered_func
    
    def none_triggered_func(self, name, datadict):
        pass

    def on_received(self, event):
        """
        处理触发器消息。

        解析JSON格式的触发器数据，调用触发器管理器进行处理。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        content = event.data.content
        if not isinstance(content, dict):
            self.logger.error(
                '[MTriggerWsHandler] trigger payload is not a dict (type={})'.format(
                    type(content).__name__
                )
            )
            return
        name = content.get('name')
        arguments = content.get('arguments')
        try:
            string_types = (basestring,)
        except NameError:
            string_types = (str,)
        if not isinstance(name, string_types) or not isinstance(arguments, dict):
            self.logger.error(
                '[MTriggerWsHandler] invalid trigger fields (name_type={}, arguments_type={})'.format(
                    type(name).__name__,
                    type(arguments).__name__,
                )
            )
            return
        try:
            self._trigger_func(name, arguments)
        except Exception as e:
            self.logger.error("[MTriggerWsHandler] Error processing trigger {}: {}".format(name, e))

    def set_trigger_function(self, func):
        self._trigger_func = func


class QualityStatusWsHandler(MaicaWSTask):
    """Receive post-core quality results without treating them as triggers."""

    def __init__(self, task_type, name, manager, except_ws_status=None):
        super(QualityStatusWsHandler, self).__init__(
            task_type, name, manager=manager,
            except_ws_status=except_ws_status
        )
        self._pending = []
        self._pending_lock = threading.Lock()

    def on_received(self, event):
        content = event.data.content
        if not isinstance(content, (list, tuple)) or len(content) != 2:
            self.logger.error(
                '[QualityStatusWsHandler] invalid quality payload shape (type={}, length={})'.format(
                    type(content).__name__,
                    len(content) if isinstance(content, (list, tuple)) else "n/a",
                )
            )
            return

        reasonable, confidence = content
        try:
            number_types = (int, long, float)
        except NameError:
            number_types = (int, float)

        if (
            not isinstance(reasonable, bool)
            or isinstance(confidence, bool)
            or not isinstance(confidence, number_types)
            or not 0.0 <= confidence <= 1.0
        ):
            self.logger.error(
                '[QualityStatusWsHandler] invalid quality fields (reasonable_type={}, confidence={})'.format(
                    type(reasonable).__name__,
                    confidence,
                )
            )
            return

        result = (reasonable, float(confidence))
        with self._pending_lock:
            self._pending.append(result)

    def drain(self):
        with self._pending_lock:
            pending = list(self._pending)
            self._pending = []
        return pending

    def clear(self):
        with self._pending_lock:
            self._pending = []

    def reset(self):
        super(QualityStatusWsHandler, self).reset()
        self.clear()

import json


class MAICALoginTasker(MaicaWSTask):
    """
    MAICA登录任务处理器。

    负责发送登录请求，使用访问令牌进行身份验证。
    """

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化登录任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
        """
        super(MAICALoginTasker, self).__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.success = False
        self._result_callback = None
        self._frontend_id = None
        self.__token = ''

    LOGIN_FAILURE_STATUSES = (
        'maica_login_token_corrupted',
        'maica_login_token_invalid',
        'maica_login_f2b',
        'maica_login_banned',
        'maica_login_email_unchecked',
        'maica_login_tos_unaccepted',
        'maica_connection_reuse_denied',
    )

    PREAUTH_FAILURE_STATUSES = (
        'maica_unified_warning',
        'maica_unified_error',
        'maica_uncaught_exception',
    )

    def set_result_callback(self, callback):
        self._result_callback = callback

    def set_frontend_id(self, frontend_id):
        self._frontend_id = frontend_id

    def _notify_result(self, success, status=None, message=None, code=None):
        if self._result_callback:
            self._result_callback(success, status, message, code)

    def on_manual_run(self, token):
        """
        执行登录操作。

        构建登录请求JSON并通过WebSocket发送。

        Args:
            token (str): MAICA系统的访问令牌

        Raises:
            RuntimeError: 如果manager或ws_client为None
        """
        request = {'type': 'auth', 'access_token': token}
        if self._frontend_id:
            request['frontend_id'] = self._frontend_id
        data = json.dumps(request)
        if self.manager is None:
            raise RuntimeError("MAICALoginTasker: manager is None")
        if self.manager.ws_client is None:
            raise RuntimeError("MAICALoginTasker: manager.ws_client is None")
        self.logger.info("[MAICALoginTasker] sending authentication request")
        self.manager.ws_client.send(data)

    def set_token(self, token):
        self.logger.debug("[MAICALoginTasker] set token: {}...".format(token[:15]))
        self.__token = token

    def login(self, token):
        """
        启动登录流程。

        使用访问令牌登录MAICA系统。

        Args:
            token (str): MAICA系统的访问令牌，用于身份验证

        Returns:
            None: 该方法无返回值，通过父类的start_event方法启动登录流程
        """
        super(MAICALoginTasker, self).start_event(token)

    def on_received(self, event):
        if event.data.status == 'maica_connection_initiated':
            self.start_event(self.__token)
        elif event.data.status == 'maica_connection_established':
            self.success = True
            self._notify_result(True)
            self.manager.create_event(
                MaicaTaskEvent(
                    taskowner=self,
                    event_type=MAICATASKEVENT_TYPE_TASK,
                    data=maica_tasker_events.GenericData(
                        name='maica_login_successful',
                        content={}
                    )            
                )
            )
        elif not self.success and event.data.status in (
            self.LOGIN_FAILURE_STATUSES + self.PREAUTH_FAILURE_STATUSES
        ):
            self.success = False
            self.status = MaicaTask.MAICATASK_STATUS_ERROR
            self._notify_result(
                False,
                event.data.status,
                event.data.content,
                getattr(event.data, 'code', None),
            )
            self.manager.create_event(
                MaicaTaskEvent(
                    taskowner=self,
                    event_type=MAICATASKEVENT_TYPE_TASK,
                    data=maica_tasker_events.GenericData(
                        name='maica_login_failed',
                        content={
                            'status': event.data.status,
                            'message': event.data.content,
                            'code': getattr(event.data, 'code', None),
                        }
                    )            
                )
            )
            if self.manager:
                self.manager.close_ws()
    
    def reset(self):
        super(MAICALoginTasker, self).reset()
        self.success = False


class MAICASessionResetTasker(MaicaWSTask):
    """
    MAICA会话重置任务处理器。

    负责发送会话重置请求，用于重置当前的聊天会话。
    """


    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化会话重置任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
        """
        if except_ws_status is None:
            except_ws_status = ['maica_session_reset']
        super(MAICASessionResetTasker, self).__init__(task_type, name, manager, except_ws_status)

    def on_manual_run(self, chat_session):
        """
        执行会话重置操作。

        构建会话重置请求JSON并通过WebSocket发送。
        """
        self.status = MaicaTask.MAICATASK_STATUS_READY
        data = {
            "type": "query",
            "chat_session": chat_session,
            "reset": True
        }
        self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))

    def on_received(self, event):
        """
        处理会话重置响应。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        return None


class MAICASettingSendTasker(MaicaWSTask):
    """
    MAICA设置发送任务处理器。

    负责发送聊天模型配置参数到服务器。支持手动发送和自动发送两种模式：
    - 手动模式：通过 on_manual_run() 直接发送配置
    - 自动模式：监听 'loginer_ready' 事件，自动调用生成函数并发送配置

    Attributes:
        _generate_setting_func (callable|None): 生成配置参数的回调函数，返回配置字典
    """

    def __init__(self, task_type, name, manager, except_ws_status=None):
        """
        初始化设置发送任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表，默认监听 'maica_params_accepted'
        """
        if except_ws_status is None:
            except_ws_status = ['maica_params_accepted']
        super(MAICASettingSendTasker, self).__init__(task_type, name, manager, except_ws_status=except_ws_status)
        self._generate_setting_func = None

    def on_manual_run(self, request_body):
        """
        执行设置发送操作。

        将配置参数作为JSON发送给服务器。

        Note:
            你必须在Loginer完成后才能执行发送!

        Args:
            request_body (dict): 包含配置参数的请求体字典
        """
        request_body['reset']=True
        self.logger.debug(
            "[MAICASettingSendTasker] sending settings: {}".format(request_body)
        )
        self.manager.ws_client.send(json.dumps(request_body, ensure_ascii=False))

    def on_event(self, event):
        """
        处理任务事件。

        监听 'maica_login_successful' 事件，当登录完成后自动调用生成函数并发送配置。

        Args:
            event (MaicaTaskEvent): 任务事件对象

        Returns:
            调用父类on_event方法的返回值
        """
        if event.event_type == MAICATASKEVENT_TYPE_TASK and \
           event.data.name == 'maica_login_successful':
            if self._generate_setting_func is not None:
                settings = self._generate_setting_func()
                self.on_manual_run(settings)
        return super(MAICASettingSendTasker, self).on_event(event)

    def on_received(self, event):
        """
        处理设置接受响应。

        当服务器接受配置参数后会收到此响应。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        return None

    def set_generate_setting_func(self, func):
        """
        设置生成配置参数的回调函数。

        设置后，当收到 'loginer_ready' 事件时会自动调用该函数生成配置并发送。

        Args:
            func (callable): 回调函数，无参数，返回包含配置参数的字典。
                           字典应包含聊天模型的配置参数。

        Example:
            def generate_my_settings():
                return {
                    'type': 'params',
                    'temperature': 0.7,
                    'max_tokens': 2000,
                    # 其他配置参数...
                }

            tasker.set_generate_setting_func(generate_my_settings)
        """
        self._generate_setting_func = func
        self.logger.debug("[MAICASettingSendTasker] set custom generate_setting_func")

    @property
    def generate_setting_func(self):
        """
        获取当前的配置生成函数。

        Returns:
            callable|None: 配置生成函数，如果未设置则返回None
        """
        return self._generate_setting_func


class AutoReconnector(MaicaWSTask):
    """
    WebSocket自动重连处理器。

    监听WebSocket关闭事件，在连接断开时自动触发重连操作。

    Attributes:
        _reconnect_func (callable|None): 重连回调函数
        _enabled (bool): 自动重连是否启用
        _reconnect_delay (float): 首次重连延迟时间（秒）
        _max_reconnect_delay (float): 指数退避的最大延迟时间（秒）
        _max_reconnect_attempts (int): 连续重连次数上限
        _login_successful (bool): 是否已成功登录，用于防止在登录失败后重连
    """
    def __init__(self, task_type, name, manager=None, except_ws_status=None):
        """
        初始化自动重连处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status: 监听的消息状态列表
        """
        super(AutoReconnector, self).__init__(task_type, name, manager, except_ws_status)
        self._reconnect_func = None
        self._enabled = False
        self._reconnect_delay = 2.0
        self._max_reconnect_delay = 30.0
        self._max_reconnect_attempts = 8
        self._reconnect_attempts = 0
        self._reconnect_thread = None
        self._reconnect_cancel = threading.Event()
        self._reconnect_lock = threading.Lock()
        self._login_successful = False

    def on_event(self, event):
        """
        处理任务事件。

        监听maica_login_successful事件标记登录成功，
        监听websocket_closed事件并在登录成功后触发重连。

        Args:
            event (MaicaTaskEvent): 任务事件对象
        """
        if event.event_type == MAICATASKEVENT_TYPE_TASK:
            if event.data.name == 'maica_login_successful':
                with self._reconnect_lock:
                    self._login_successful = True
                    self._reconnect_attempts = 0
                return
            if event.data.name == 'maica_login_failed':
                with self._reconnect_lock:
                    self._login_successful = False
                    self._enabled = False
                    self._reconnect_cancel.set()
                self.logger.warning("[AutoReconnector] reconnect disabled after login failure")
                return
            if event.data.name == 'websocket_closed':
                if not self._enabled:
                    return
                if not self._login_successful:
                    self.logger.debug("[AutoReconnector] skipping reconnect: login not successful")
                    return
                if self.reconnect():
                    self._emit_task_event('auto_reconnector_start_reconnect')
                    self.logger.info("[AutoReconnector] reconnect scheduled")

    def _emit_task_event(self, name):
        if not self.manager:
            return
        self.manager.create_event(
            MaicaTaskEvent(
                taskowner=self,
                event_type=MAICATASKEVENT_TYPE_TASK,
                data=maica_tasker_events.GenericData(name=name, content={})
            )
        )


    def set_reconnect_func(self, func):
        """
        设置重连回调函数。

        Args:
            func (callable): 重连回调函数
        """
        self._reconnect_func = func

    def reconnect(self):
        """
        执行重连操作。

        调用预设的重连回调函数进行重连。

        Returns:
            bool: 是否成功安排了新的重连任务

        Raises:
            RuntimeError: 如果未设置重连函数
        """
        if not self._reconnect_func:
            raise RuntimeError("No reconnect function set.")

        give_up = False
        with self._reconnect_lock:
            if not self._enabled:
                return False
            if self._reconnect_thread and self._reconnect_thread.is_alive():
                self.logger.debug("[AutoReconnector] reconnect already pending")
                return False
            if self._reconnect_attempts >= self._max_reconnect_attempts:
                self._enabled = False
                self._reconnect_cancel.set()
                give_up = True
            else:
                attempt_index = self._reconnect_attempts
                self._reconnect_attempts += 1
                delay = min(
                    self._reconnect_delay * (2 ** attempt_index),
                    self._max_reconnect_delay
                )
                cancel_event = self._reconnect_cancel

                def _delayed_reconnect():
                    if cancel_event.wait(delay):
                        return
                    with self._reconnect_lock:
                        if not self._enabled or cancel_event is not self._reconnect_cancel:
                            return
                    self._reconnect_func()

                self._reconnect_thread = threading.Thread(target=_delayed_reconnect)
                self._reconnect_thread.daemon = True
                self._reconnect_thread.start()

        if give_up:
            self.logger.warning(
                "[AutoReconnector] giving up after {} attempts".format(
                    self._max_reconnect_attempts
                )
            )
            self._emit_task_event('auto_reconnector_give_up')
            return False
        return True

    def enable(self):
        """
        启用自动重连功能。

        启用后，当WebSocket连接关闭时会自动触发重连。
        """
        changed = False
        with self._reconnect_lock:
            if not self._enabled:
                self._enabled = True
                self._reconnect_attempts = 0
                self._reconnect_cancel = threading.Event()
                changed = True
        if changed:
            self.logger.info("[AutoReconnector] auto-reconnect enabled")
        return changed

    def is_enabled(self):
        with self._reconnect_lock:
            return self._enabled

    def disable(self):
        """
        禁用自动重连功能。

        禁用后，WebSocket连接关闭时不会自动重连。
        """
        with self._reconnect_lock:
            was_enabled = self._enabled
            self._enabled = False
            self._reconnect_cancel.set()
        if was_enabled:
            self._emit_task_event('auto_reconnector_stopped')
            self.logger.info("[AutoReconnector] auto-reconnect disabled")
        return was_enabled

    def reset(self):
        super(AutoReconnector, self).reset()
        # Connection errors reset tasks before the close event is delivered.
        # Keep login/retry state until a definitive login result changes it.


class AutoResumeTasker(MaicaWSTask):
    """
    自动恢复任务处理器。

    监听WebSocket重连事件，在重连成功后自动发送恢复会话请求，
    用于在连接断开后恢复之前的聊天会话状态。

    工作流程：
    1. 监听 'auto_reconnector_start_reconnect' 事件，标记进入重连状态
    2. 监听 'maica_mcore_gen_start' 事件，标记生成已受续传保护
    3. 监听 'maica_login_successful' 事件，在重连状态下发送恢复请求
    4. 监听终止和失败事件，清理恢复状态

    Attributes:
        _on_reconnect (bool): 是否处于重连状态
        _enabled (bool): 自动恢复功能是否启用
        _generation_started (bool): 后端是否已发送生成开始标记
    """
    def __init__(self, task_type, name, manager=None, except_ws_status=None):
        """
        初始化自动恢复任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status: 监听的消息状态列表
        """
        super(AutoResumeTasker, self).__init__(task_type, name, manager, except_ws_status)
        self._on_reconnect = False
        self._enabled = False
        self._generation_started = False

    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_TASK:
            self.on_received(event)
            return
        return super(AutoResumeTasker, self).on_event(event)

    def _clear_resume_state(self):
        self._on_reconnect = False
        self._generation_started = False

    def on_received(self, event):
        """
        处理接收到的任务事件。

        根据不同的事件类型执行相应操作：
        - maica_login_successful: 登录成功后，如果重连前生成已经开始，发送恢复请求
        - auto_reconnector_start_reconnect: 标记进入重连状态
        - websocket_closed: 重置重连状态

        Args:
            event (MaicaTaskEvent): 任务事件对象

        Returns:
            调用父类on_received方法的返回值
        """
        if not self._enabled:
            return

        if event.event_type == MAICATASKEVENT_TYPE_WS:
            if event.data.status == 'maica_mcore_gen_start':
                self._generation_started = True
            elif event.data.status in (
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ):
                self._clear_resume_state()
            return

        if event.event_type == MAICATASKEVENT_TYPE_TASK:
            if event.data.name == 'maica_login_successful':
                if self._on_reconnect and self._generation_started:
                    try:
                        data = {'type': 'reconn'}
                        self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))
                        self.logger.info("[AutoResumeTasker] sent resume request")
                    finally:
                        self._clear_resume_state()
            elif event.data.name == 'auto_reconnector_start_reconnect':
                self._on_reconnect = True
                self.logger.debug("[AutoResumeTasker] marked as reconnecting")
            elif event.data.name == 'websocket_closed':
                self.reset_on_closed()
            elif event.data.name == 'maica_login_failed':
                self._clear_resume_state()
            elif event.data.name in ('auto_reconnector_give_up', 'auto_reconnector_stopped'):
                self._clear_resume_state()

        return None

    def reset_on_closed(self):
        """
        在WebSocket连接关闭时重置重连状态。

        将_on_reconnect标志重置为False，准备下一次重连。
        """
        if not (self._on_reconnect and self._generation_started):
            self._clear_resume_state()
        self.logger.debug("[AutoResumeTasker] reset reconnect state")

    def enable(self):
        """
        启用自动恢复功能。

        启用后，在WebSocket重连成功时会自动发送恢复会话请求。
        """
        if self._enabled:
            return False
        self._enabled = True
        self.logger.info("[AutoResumeTasker] auto-resume enabled")
        return True

    def disable(self):
        """
        禁用自动恢复功能。

        禁用后，重连成功时不会自动发送恢复会话请求。
        """
        was_enabled = self._enabled
        self._enabled = False
        self._clear_resume_state()
        if was_enabled:
            self.logger.info("[AutoResumeTasker] auto-resume disabled")
        return was_enabled

    def reset(self):
        super(AutoResumeTasker, self).reset()
        # WebSocket errors reset tasks before the close event marks a reconnect.
        if not (self._enabled and self._generation_started):
            self._clear_resume_state()

class KeepWsAliveTasker(MaicaWSTask):
    """
    WebSocket心跳保活处理器。

    在登录成功后定时发送静默心跳（sping）保持连接活跃。
    提供显式的ping()方法用于堵塞式获取网络延迟。

    Attributes:
        _enabled (bool): 心跳是否启用
        _logged_in (bool): 是否已登录
        _ping_interval (float): 静默心跳间隔时间（秒）
        _last_sping_time (float|None): 上次发送静默心跳的时间戳
        _ping_sent_time (float|None): 显式ping发送的时间戳
        _latency (float): 最近一次的延迟（毫秒）
        _pong_content (str|unicode): 上次pong返回的content
        ui_lang_zh (bool): 是否选择中文的pong内容
        _timer_thread (threading.Thread|None): 定时器线程
        _pong_event (threading.Event|None): 用于等待pong响应的事件
    """

    def __init__(self, task_type, name, manager=None, except_ws_status=None, ping_interval=30.0):
        """
        初始化心跳保活处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表，默认监听'pong'
            ping_interval (float): 静默心跳间隔时间（秒），默认30秒
        """
        if except_ws_status is None:
            except_ws_status = ['pong']
        super(KeepWsAliveTasker, self).__init__(task_type, name, manager, except_ws_status)
        self._enabled = False
        self._logged_in = False
        self._ping_interval = ping_interval
        self._last_sping_time = None
        self._ping_sent_time = None
        self._latency = 0.0
        self._pong_content = u""
        self.ui_lang_zh = False
        self._timer_thread = None
        self._stop_timer = False
        import threading
        self._pong_event = threading.Event()

    def on_event(self, event):
        """
        处理任务事件。

        监听登录成功事件和WebSocket关闭事件。

        Args:
            event (MaicaTaskEvent): 任务事件对象
        """
        if event.event_type == MAICATASKEVENT_TYPE_TASK:
            if event.data.name == 'maica_login_successful':
                self._logged_in = True
                if self._enabled and self._start_timer():
                    self.logger.info("[KeepWsAliveTasker] keep-alive started after login")
            elif event.data.name == 'websocket_closed':
                self._logged_in = False
                self._stop_timer_thread()
                self._pong_event.set()  # 唤醒可能在等待的ping()调用
        elif event.event_type == MAICATASKEVENT_TYPE_WS:
            if event.data.status == 'pong':
                self.on_received(event)

    def on_received(self, event):
        """
        处理接收到的pong响应。

        计算从发送ping到接收pong的延迟时间，并唤醒等待的线程。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if self._ping_sent_time is not None:
            import time
            current_time = time.time()
            self._latency = (current_time - self._ping_sent_time) * 1000  # 转换为毫秒

            try:
                welcome_zh, welcome_en = event.data.content.split("|", 1)
                event.data.content = welcome_zh if self.ui_lang_zh else welcome_en
            except Exception:
                pass
            self._pong_content = event.data.content

            self.logger.debug("[KeepWsAliveTasker] received pong, latency: {:.2f}ms".format(self._latency))
            self._ping_sent_time = None
            self._pong_event.set()  # 唤醒等待pong的线程

    def _start_timer(self):
        """启动定时器线程，定期发送静默心跳。"""
        if self._timer_thread is not None and self._timer_thread.is_alive():
            return False

        self._stop_timer = False
        import threading
        self._timer_thread = threading.Thread(target=self._timer_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()
        self.logger.debug("[KeepWsAliveTasker] timer thread started")
        return True

    def _stop_timer_thread(self):
        """停止定时器线程。"""
        was_running = bool(
            self._timer_thread is not None and self._timer_thread.is_alive()
        )
        self._stop_timer = True
        if self._timer_thread is not None:
            self._timer_thread = None
        if was_running:
            self.logger.debug("[KeepWsAliveTasker] timer stop requested")
        return was_running

    def _timer_loop(self):
        """定时器循环，定期发送静默心跳。"""
        import time
        while not self._stop_timer and self._enabled and self._logged_in:
            current_time = time.time()

            # 检查是否需要发送静默心跳
            if self._last_sping_time is None or (current_time - self._last_sping_time) >= self._ping_interval:
                self._send_sping()
                self._last_sping_time = current_time

            # 短暂休眠，避免CPU占用过高
            time.sleep(1.0)

    def _send_sping(self):
        """发送静默心跳到服务器（不期望响应）。"""
        if not self._logged_in or not self.manager or not self.manager.ws_client:
            return

        try:
            import json
            data = {'type': 'sping'}

            self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))
            self.logger.debug("[KeepWsAliveTasker] sent silent ping (sping)")
        except Exception as e:
            self.logger.error("[KeepWsAliveTasker] failed to send sping: {}".format(e))

    def ping(self, timeout=5.0):
        """
        显式发送ping请求并堵塞等待pong响应，用于测量网络延迟。

        Args:
            timeout (float): 等待超时时间（秒），默认5秒

        Returns:
            float|None: 如果成功接收到pong，返回延迟（毫秒）；否则返回None
        """
        if not self._logged_in or not self.manager or not self.manager.ws_client:
            self.logger.warning("[KeepWsAliveTasker] cannot ping: not logged in or no ws_client")
            return None

        try:
            import time
            import json

            # 重置pong事件
            self._pong_event.clear()

            # 发送ping
            data = {'type': 'ping'}

            self._ping_sent_time = time.time()
            self.manager.ws_client.send(json.dumps(data, ensure_ascii=False))
            self.logger.debug("[KeepWsAliveTasker] sent explicit ping")

            # 等待pong响应
            if self._pong_event.wait(timeout):
                # 成功接收到pong
                self.logger.debug("[KeepWsAliveTasker] ping successful, latency: {:.2f}ms".format(self._latency))
                return self._latency
            else:
                # 超时
                self.logger.warning("[KeepWsAliveTasker] ping timeout after {:.1f}s".format(timeout))
                self._ping_sent_time = None
                return None

        except Exception as e:
            self.logger.error("[KeepWsAliveTasker] ping failed: {}".format(e))
            self._ping_sent_time = None
            return None

    @property
    def latency(self):
        """
        获取最近一次的延迟（毫秒）。

        Returns:
            float: 延迟时间（毫秒）
        """
        return self._latency

    def enable(self):
        """
        启用心跳保活功能。

        如果已登录，则立即启动定时器。
        """
        if self._enabled:
            return False
        self._enabled = True
        if self._logged_in:
            self._start_timer()
        self.logger.info("[KeepWsAliveTasker] keep-alive enabled")
        return True

    def disable(self):
        """
        禁用心跳保活功能。

        停止定时器线程。
        """
        was_enabled = self._enabled
        self._enabled = False
        self._stop_timer_thread()
        if was_enabled:
            self.logger.info("[KeepWsAliveTasker] keep-alive disabled")
        return was_enabled

    def reset(self):
        """重置心跳保活状态。"""
        super(KeepWsAliveTasker, self).reset()
        self._logged_in = False
        self._last_sping_time = None
        self._ping_sent_time = None
        self._latency = 0.0
        self._pong_event.clear()
        self._stop_timer_thread()
