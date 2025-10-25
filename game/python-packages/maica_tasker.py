import websocket

class MaicaTaskManager():
    def __init__(self, ):
        self.task_list = []
        self.ws_client = None
        self.http_client = None
    
    def __ws_onmessage(self, wsapp, message):
        event = MaicaTaskEvent(
            taskowner=self,
            event_type=MAICATASKEVENT_TYPE_WS,
            data=message
        )
        self._on_event(event)

    def _on_event(self, event_object):
        for t in self.task_list:
            t.on_event(event_object)
    
    def create_event(self, event_object):
        self.on_event(event_object)
    
    def close_ws(self):
        self.ws_client.close()
    
    def register_task(self, task):
        if not task in self.task_list:
            self.task_list.append(task)
    
    def reset_all_task():
        for t in self.task_list:
            t.reset()

MAICATASKEVENT_TYPE_WS = 0
MAICATASKEVENT_TYPE_TASK = 1

class MaicaTaskEvent:
    def __init__(self, taskowner, event_type, data):
        self.taskowner = taskowner
        self.event_type = event_type
        self.data = data



class MaicaTask:
    MAICATASK_TYPE_NORMAL = 0
    MAICATASK_TYPE_WS = 1

    MAICATASK_STATUS_READY = 0
    MAICATASK_STATUS_RUNNING = 1
    MAICATASK_STATUS_ERROR = 2

    def __init__(self, task_type, name, manager):
        self.task_type = task_type,
        self.name = name
        self.status = MaicaTask.MAICATASK_STATUS_READY
        self.manager = manager
    
    def on_event(event):
        raise NotImplementedError()
    def reset(self):
        pass
    def start_event(self, *args, **kwargs):
        if self.status == MaicaTask.MAICATASK_STATUS_READY:
            self.status = MaicaTask.MAICATASK_STATUS_RUNNING
            self.on_manual_run(self.manager, *args, **kwargs)
            self.status = MaicaTask.MAICATASK_STATUS_READY
        else:
            if self.status == MaicaTask.MAICATASK_STATUS_RUNNING:
                raise RuntimeError("MaicaTask {} is running".format(self.name))
            elif self.status == MaicaTask.MAICATASK_STATUS_ERROR:
                raise RuntimeError("MaicaTask {} is broken, check log for details".format(self.name))
    def on_manual_run(self, manager, *args, **kwargs):
        raise NotImplementedError()
class WSResponse():
    def __init__(self, ws_response):
        # {"code": "状态码", "status": "状态标识", "content": "具体内容", "type": "信息类型", "timestamp": 时间戳}
        self.code = ws_response["code"]
        self.status = ws_response["status"]
        self.content = ws_response["content"]
        self.type = ws_response["type"]
        self.timestamp = ws_response["timestamp"]
        self.ws_response = ws_response
class MaicaWSTask(MaicaTask):
    def __init__(self, task_type, name, manager, except_ws_types = []):
        super().__init__(task_type, name, manager)
        self.except_ws_types = except_ws_types

    
    def on_event(self, event):
        if event.event_type == MAICATASKEVENT_TYPE_WS:
            ws = event.data
            if ws.type in self.except_ws_types or self.except_ws_types == []:
                self.on_received(ws)
    def on_received(self, ws):
        raise NotImplementedError()
        