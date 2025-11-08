class MaicaTaskEvent(object):
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

    def __str__(self):
        """
        返回事件的字符串表示。

        Returns:
            str: 事件的可读字符串表示
        """
        return "MaicaTaskEvent(taskowner={}, event_type={}, data={})".format(
            self.taskowner,
            self.event_type,
            self.data
        )

class GenericData(object):

    def __init__(self, name, content):
        self.name = name
        self.content = content

class WebSocketClosedEvent(MaicaTaskEvent):
    def __init__(self, taskowner, event_type, data):
        super(WebSocketClosedEvent, self).__init__(taskowner, event_type, data)
