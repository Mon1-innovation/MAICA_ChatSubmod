"""
MAICA任务子模块 - WebSocket任务的具体实现

此模块包含各种具体的WebSocket任务处理器，用于处理不同类型的WebSocket消息。
"""

from maica_tasker import *


class GeneralWsErrorHandler(MaicaWSTask):
    """
    通用WebSocket错误处理器。

    监听WebSocket错误消息，在接收到错误类型的消息或服务器返回5xx错误时，
    关闭WebSocket连接并记录错误日志。

    Attributes:
        logger: 日志记录器实例
    """

    def __init__(self, task_type, name, manager, except_ws_status=[], logger=None):
        """
        初始化错误处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
            logger: 日志记录器
        """
        super().__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.logger = logger
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
            if wspack.type == 'error' or 500 <= wspack.code <= 600:
                event.taskowner.close_ws()
                if self.logger:
                    self.logger.error(
                        "[GeneralWsErrorHandler] websocket error: " + wspack.content + "\nwebsocket connection closed"
                    )


class GeneralWsLogger(MaicaWSTask):
    """
    通用WebSocket日志记录器。

    根据WebSocket消息的类型（info、warn、error、debug）进行日志记录，
    用于跟踪和调试WebSocket通信过程。

    Attributes:
        logger: 日志记录器实例
    """

    def __init__(self, task_type, name, manager, except_ws_status=[], logger=None):
        """
        初始化日志记录器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
            logger: 日志记录器
        """
        super().__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        if logger:
            self.logger = logger
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
                if wspack.type == 'info':
                    self.logger.info(
                        "[GeneralWsLogger] " + "<{}({})> {}".format(wspack.status, wspack.code, wspack.content)
                    )
                elif wspack.type == 'warn':
                    self.logger.warning(
                        "[GeneralWsLogger] " + "<{}({})> {}".format(wspack.status, wspack.code, wspack.content)
                    )
                elif wspack.type == 'error':
                    self.logger.error(
                        "[GeneralWsLogger] " + "<{}({})> {}".format(wspack.status, wspack.code, wspack.content)
                    )
                else:
                    self.logger.debug(
                        "[GeneralWsLogger] " + "<{}({})> {}".format(wspack.status, wspack.code, wspack.content)
                    )


class MAICALoopWarnHandler(GeneralWsErrorHandler):
    """
    MAICA循环警告处理器。

    监听特定的循环警告消息，记录警告日志并关闭WebSocket连接。
    继承自GeneralWsErrorHandler以复用错误处理逻辑。
    """
    def on_event(self, event):
        return super(GeneralWsErrorHandler, self).on_event(event)
    def on_received(self, event):
        """
        处理循环警告消息。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        wspack = event.data
        if self.logger:
            self.logger.warning(
                "[MAICALoopWarnHandler] " + "<{}> {}".format(wspack.status, wspack.content)
            )
        event.taskowner.close_ws()


class HistoryStatusHandler(MaicaWSTask):
    """
    历史记录状态处理器。

    监听历史记录切片相关的消息，跟踪token使用状态：
    - TOKEN_NORMAL: 正常状态
    - TOKEN_24000_EXCEEDED: token超过24000
    - TOKEN_MAX_EXCEEDED: token达到最大限制

    Attributes:
        status (int): 当前token状态
    """

    # Token状态常量
    TOKEN_NORMAL = 0
    TOKEN_24000_EXCEEDED = 1
    TOKEN_MAX_EXCEEDED = 2

    def __init__(self, task_type, name, manager):
        """
        初始化历史状态处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
        """
        super().__init__(
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
            self.status = self.TOKEN_24000_EXCEEDED
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
        super().__init__(
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


class MTriggerWsHandler(MaicaWSTask):
    """
    MAICA触发器WebSocket处理器。

    监听触发器相关的WebSocket消息，当接收到触发器信息时，
    将其传递给触发器管理器进行处理。

    Attributes:
        manager: 触发器管理器实例（注意：此处覆盖了父类的task_manager）
    """

    def __init__(self, task_type, name, manager, mt_manager):
        """
        初始化触发器处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): WebSocket任务管理器实例
            mt_manager: 触发器管理器实例
        """
        super().__init__(
            task_type, name, manager=manager,
            except_ws_status=['maica_mtrigger_trigger']
        )
        self.mt_manager = mt_manager  # 覆盖为触发器管理器

    def on_received(self, event):
        """
        处理触发器消息。

        解析JSON格式的触发器数据，调用触发器管理器进行处理。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        if event.data.status == 'maica_mtrigger_trigger':
            import json
            from maica_mtrigger import MTriggerAction

            data = json.loads(event.data.content)
            for item in data:
                self.mt_manager.triggered(item, data[item])
            self.mt_manager.run_trigger(MTriggerAction.instant)


class MAICAWSCookiesHandler(MaicaWSTask):
    """
    WebSocket Cookie处理器。

    监听WebSocket安全Cookie消息，存储服务器下发的Cookie用于后续请求。

    Attributes:
        _cookie (str|None): 存储的Cookie值
        _enabled (bool): Cookie是否启用，只有启用时才返回实际的cookie值
    """
    _cookie = None
    _enabled = False
    def __init__(self, task_type, name, manager, except_ws_status=[]):
        """
        初始化Cookie处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
        """
        super().__init__(
            task_type, name, manager=manager,
            except_ws_status=except_ws_status
        )

    def on_received(self, event):
        """
        处理Cookie消息。

        提取并存储服务器下发的Cookie。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        self.logger.info("[MAICAWSCookiesHandler] received cookie")
        MAICAWSCookiesHandler._cookie = event.data.content
    @classmethod
    @property
    def cookie(self):
        """
        获取存储的Cookie值。

        只有当_enabled为True时才返回实际的cookie值，否则返回None。

        Returns:
            str|None: Cookie值，如果_enabled为False则返回None
        """
        if MAICAWSCookiesHandler._enabled:
            return MAICAWSCookiesHandler._cookie
        return None

    def reset(self):
        """重置Cookie和启用状态。"""
        MAICAWSCookiesHandler._cookie = None
        MAICAWSCookiesHandler._enabled = False

    def enable_cookie(self):
        """启用Cookie返回。"""
        MAICAWSCookiesHandler._enabled = True

    def disable_cookie(self):
        """禁用Cookie返回。"""
        MAICAWSCookiesHandler._enabled = False


import json


class MAICALoginTasker(MaicaWSTask):
    """
    MAICA登录任务处理器。

    负责发送登录请求，使用访问令牌进行身份验证。
    """

    def __init__(self, task_type, name, manager, except_ws_status=[]):
        """
        初始化登录任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
        """
        super().__init__(task_type, name, manager=manager, except_ws_status=except_ws_status)
        self.success = False

    def on_manual_run(self, token):
        """
        执行登录操作。

        构建登录请求JSON并通过WebSocket发送。

        Args:
            token (str): MAICA系统的访问令牌

        Raises:
            RuntimeError: 如果manager或ws_client为None
        """
        data = json.dumps({
            'access_token': token
        })
        if self.manager is None:
            raise RuntimeError("MAICALoginTasker: manager is None")
        if self.manager.ws_client is None:
            raise RuntimeError("MAICALoginTasker: manager.ws_client is None")
        self.logger.info("[MAICALoginTasker] login: {}".format(data))
        self.manager.ws_client.send(data)

    def login(self, token):
        """
        启动登录流程。

        使用访问令牌登录MAICA系统。

        Args:
            token (str): MAICA系统的访问令牌，用于身份验证

        Returns:
            None: 该方法无返回值，通过父类的start_event方法启动登录流程
        """
        super().start_event(token)

    def on_received(self, event):
        self.success = True
    
    def reset(self):
        self.success = False


class MAICASessionResetTasker(MaicaWSTask):
    """
    MAICA会话重置任务处理器。

    负责发送会话重置请求，用于重置当前的聊天会话。

    Attributes:
        strict_cookie (str|None): 严格模式下使用的Cookie值
    """

    strict_cookie = None

    def __init__(self, task_type, name, manager, except_ws_status=['maica_session_reset']):
        """
        初始化会话重置任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
        """
        super().__init__(task_type, name, manager, except_ws_status)

    def on_manual_run(self):
        """
        执行会话重置操作。

        构建会话重置请求JSON并通过WebSocket发送。
        """
        self.status = MaicaTask.MAICATASK_STATUS_READY
        data = {
            "type": "query",
            "chat_session": self.manager.chat_session,
            "reset": True
        }
        if MAICASessionResetTasker.strict_cookie:
            data["cookie"] = MAICASessionResetTasker.strict_cookie
        self.manager.ws_client.send(json.dumps(data))

    def on_received(self, event):
        """
        处理会话重置响应。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        self.logger.debug(
            "[MAICASessionResetTasker] received: {}".format(self.name, event.data.content)
        )


class MAICASettingSendTasker(MaicaWSTask):
    """
    MAICA设置发送任务处理器。

    负责发送聊天模型配置参数到服务器。
    """

    def __init__(self, task_type, name, manager, except_ws_status=['maica_params_accepted']):
        """
        初始化设置发送任务处理器。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager): 任务管理器实例
            except_ws_status (list): 监听的消息状态列表
        """
        super().__init__(task_type, name, manager, except_ws_status=except_ws_status)

    def on_manual_run(self, request_body):
        """
        执行设置发送操作。

        将配置参数作为JSON发送给服务器。

        Args:
            request_body (dict): 包含配置参数的请求体字典
        """
        self.manager.ws_client.send(json.dumps(request_body))

    def on_received(self, event):
        """
        处理设置接受响应。

        Args:
            event (MaicaTaskEvent): WebSocket事件对象
        """
        self.logger.debug(
            "[MAICASettingSendTasker] received: {}".format(self.name, event.data.content)
        )
