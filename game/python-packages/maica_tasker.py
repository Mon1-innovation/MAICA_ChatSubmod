import websocket

# 常量定义：WebSocket事件类型
MAICATASKEVENT_TYPE_WS = 0
MAICATASKEVENT_TYPE_TASK = 1


class DefaultLogger:
    """
    默认日志记录器，用于在没有提供日志记录器的情况下输出日志信息。
    """
    def debug(self, msg):
        """输出调试级别的日志"""
        print("[DEBUG] {}".format(msg))

    def info(self, msg):
        """输出信息级别的日志"""
        print("[INFO] {}".format(msg))

    def error(self, msg):
        """输出错误级别的日志"""
        print("[ERROR] {}".format(msg))

    def warning(self, msg):
        """输出警告级别的日志"""
        print("[WARNING] {}".format(msg))


default_logger = DefaultLogger()


class MaicaTaskManager:
    """
    任务管理器，负责管理所有MAICA任务的注册、事件分发和WebSocket客户端管理。

    主要职责：
    - 管理任务列表
    - 处理WebSocket消息并将其分发给相关任务
    - 管理WebSocket和HTTP客户端
    """

    def __init__(self):
        """
        初始化任务管理器。

        Attributes:
            task_list (list): 注册的任务列表
            ws_client (WebSocketApp|None): WebSocket客户端实例
            http_client (None): HTTP客户端实例（预留）
        """
        self.task_list = []
        self.ws_client = None
        self.http_client = None

    def _ws_onmessage(self, wsapp, message):
        """
        WebSocket消息到达时的回调函数。

        Args:
            wsapp: WebSocket应用实例
            message (str): 接收到的JSON格式消息

        创建MaicaTaskEvent事件并分发给所有监听的任务。
        """
        event = MaicaTaskEvent(
            taskowner=self,
            event_type=MAICATASKEVENT_TYPE_WS,
            data=WSResponse(message)
        )
        self._on_event(event)

    def _on_event(self, event_object):
        """
        将事件分发给任务列表中的所有任务。

        Args:
            event_object (MaicaTaskEvent): 要分发的事件对象

        遍历所有注册的任务，调用其on_event方法处理事件。
        """
        for t in self.task_list:
            t.on_event(event_object)

    def create_event(self, event_object):
        """
        创建并分发一个事件（预留接口，当前实现有误）。

        Args:
            event_object: 事件对象
        """
        self.on_event(event_object)

    def close_ws(self):
        """关闭WebSocket连接。"""
        self.ws_client.close()

    def register_task(self, task):
        """
        将任务注册到管理器的任务列表中。

        Args:
            task (MaicaTask): 要注册的任务对象

        防止重复注册同一个任务。
        """
        if not task in self.task_list:
            if self.get_task(task.name):
                raise Exception("Task {} already exists".format(task.name))
            self.task_list.append(task)

    def reset_all_task(self):
        """
        重置所有注册的任务。

        遍历任务列表，调用每个任务的reset方法。
        """
        for t in self.task_list:
            t.reset()

    def get_task(self, name):
        """
        根据任务名称获取任务对象。

        Args:
            name (str): 任务名称

        Returns:
            MaicaTask|None: 找到的任务对象，如果未找到返回None
        """
        for t in self.task_list:
            if t.name == name:
                return t


class MaicaTaskEvent:
    """
    MAICA事件对象，用于在任务之间传递事件信息。

    Attributes:
        taskowner (MaicaTaskManager): 产生该事件的任务管理器
        event_type (int): 事件类型（MAICATASKEVENT_TYPE_WS或MAICATASKEVENT_TYPE_TASK）
        data: 事件数据（通常是WSResponse或其他事件数据）
    """

    def __init__(self, taskowner, event_type, data):
        """
        初始化任务事件。

        Args:
            taskowner (MaicaTaskManager): 事件所有者（任务管理器）
            event_type (int): 事件类型标识
            data: 事件携带的数据
        """
        self.taskowner = taskowner
        self.event_type = event_type
        self.data = data


class MaicaTask:
    """
    MAICA任务基类，所有任务都应继承此类。

    任务生命周期：
    - READY: 任务就绪，可以执行
    - RUNNING: 任务正在执行
    - ERROR: 任务执行出错

    任务类型：
    - NORMAL: 普通任务
    - WS: WebSocket相关任务

    Attributes:
        task_type (int): 任务类型
        name (str): 任务名称
        status (int): 任务状态
        manager (MaicaTaskManager): 任务所属的管理器
        logger: 日志记录器
    """

    # 任务类型常量
    MAICATASK_TYPE_NORMAL = 0
    MAICATASK_TYPE_WS = 1

    # 任务状态常量
    MAICATASK_STATUS_READY = 0
    MAICATASK_STATUS_RUNNING = 1
    MAICATASK_STATUS_ERROR = 2

    def __init__(self, task_type, name, manager):
        """
        初始化任务。

        Args:
            task_type (int): 任务类型（MAICATASK_TYPE_NORMAL或MAICATASK_TYPE_WS）
            name (str): 任务名称，用于标识和查找任务
            manager (MaicaTaskManager): 任务所属的任务管理器

        当manager不为None时，该任务会自动注册到manager的任务列表中。
        """
        self.task_type = task_type,
        self.name = name
        self.status = MaicaTask.MAICATASK_STATUS_READY
        self.manager = manager
        self.logger = default_logger
        if manager:
            self.manager = manager
            self.manager.register_task(self)

    def on_event(self, event):
        """
        处理事件的抽象方法。

        Args:
            event (MaicaTaskEvent): 要处理的事件

        子类必须实现此方法以处理特定的事件类型。

        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError()

    def reset(self):
        """
        重置任务状态。

        子类可以重写此方法以实现自定义的重置逻辑。
        默认情况下不做任何操作。
        """
        pass

    def start_event(self, *args, **kwargs):
        """
        启动任务执行。

        Args:
            *args: 传递给on_manual_run的位置参数
            **kwargs: 传递给on_manual_run的关键字参数

        只有在任务处于READY状态时才能启动。
        执行过程中会改变任务状态为RUNNING，执行完毕后恢复为READY。

        Raises:
            RuntimeError: 如果任务已在运行或出错，则抛出异常
        """
        if self.status == MaicaTask.MAICATASK_STATUS_READY:
            self.status = MaicaTask.MAICATASK_STATUS_RUNNING
            self.on_manual_run(*args, **kwargs)
            self.status = MaicaTask.MAICATASK_STATUS_READY
        else:
            if self.status == MaicaTask.MAICATASK_STATUS_RUNNING:
                raise RuntimeError("MaicaTask {} is running".format(self.name))
            elif self.status == MaicaTask.MAICATASK_STATUS_ERROR:
                raise RuntimeError("MaicaTask {} is broken, check log for details".format(self.name))

    def on_manual_run(self, *args, **kwargs):
        """
        任务的实际执行方法。

        Args:
            *args: 从start_event传递的位置参数
            **kwargs: 从start_event传递的关键字参数

        子类必须实现此方法以定义任务的执行逻辑。

        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError()


class WSResponse:
    """
    WebSocket响应解析器，用于解析和存储WebSocket消息内容。

    WebSocket消息格式：
    {
        "code": 状态码,
        "status": 状态标识,
        "content": 具体内容,
        "type": 信息类型,
        "timestamp": 时间戳
    }

    Attributes:
        code (int): 状态码
        status (str): 状态标识
        content (str): 消息内容
        type (str): 消息类型
        timestamp: 时间戳
        ws_response (dict): 原始WebSocket响应字典
    """

    def __init__(self, ws_response):
        """
        初始化WebSocket响应对象。

        Args:
            ws_response (str): JSON格式的WebSocket消息字符串

        解析JSON并提取各个字段。
        """
        import json
        ws_response = json.loads(ws_response)
        self.code = int(ws_response["code"])
        self.status = ws_response["status"]
        self.content = ws_response["content"]
        self.type = ws_response["type"]
        self.timestamp = ws_response["timestamp"]
        self.ws_response = ws_response


class MaicaWSTask(MaicaTask):
    """
    WebSocket相关任务的基类。

    此类在MaicaTask的基础上添加了WebSocket消息过滤功能，
    只处理特定类型的WebSocket消息。

    Attributes:
        except_ws_types (list): 需要处理的WebSocket消息类型列表

    注意:
      - 未传入except_ws_types时, 将不会收到on_received方法的调用
    """

    def __init__(self, task_type, name, manager=None, except_ws_types=[]):
        """
        初始化WebSocket任务。

        Args:
            task_type (int): 任务类型
            name (str): 任务名称
            manager (MaicaTaskManager|None): 任务所属的管理器
            except_ws_types (list): 感兴趣的WebSocket消息类型列表
                                   空列表表示处理所有类型的消息
        """
        super().__init__(task_type, name, manager)
        self.except_ws_types = except_ws_types

    def on_event(self, event):
        """
        处理事件，仅处理WebSocket类型的事件。

        Args:
            event (MaicaTaskEvent): 要处理的事件

        如果事件是WebSocket消息类型，且消息类型在except_ws_types中，
        则调用on_received方法处理该消息。
        如果except_ws_types为空列表，则处理所有WebSocket消息。
        """
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            ws = event.data
            if ws.type in self.except_ws_types or self.except_ws_types == []:
                self.on_received(event)

    def on_received(self, event):
        """
        处理接收到的WebSocket消息。

        Args:
            event (MaicaTaskEvent): 包含WebSocket消息的事件对象

        子类必须实现此方法以处理特定的WebSocket消息。

        Raises:
            NotImplementedError: 如果子类未实现此方法
        """
        raise NotImplementedError(self.__class__)
