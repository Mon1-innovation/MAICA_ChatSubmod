import websocket

class MaicaTaskManager():
    def __init__(self):
        self.task_list = []
        #self.task_event = []
        self.ws_client = websocket.WebSocketApp
        self.http_client = None
    
    def _on_event(self, event_object):
        for t in self.task_list:
            t.on_event(event_object)
    
    def create_event(self, event_object):
        self.on_event(event_object)
    
    def close_ws(self):
        self.ws_client.close()

MAICATASKEVENT_TYPE_WS = 0
MAICATASKEVENT_TYPE_TASK = 1

class MaicaTaskEvent:
    def __init__(self, taskowner, event_type, data):
        self.taskowner = taskowner
        self.manager = self
        self.event_type = event_type
        self.data = data



class MaicaTask:
    MAICATASK_TYPE_NORMAL = 0
    MAICATASK_TYPE_WS = 1

    MAICATASK_STATUS_READY = 0
    MAICATASK_STATUS_RUNNING = 1
    MAICATASK_STATUS_ERROR = 2

    def __init__(self, task_type, name):
        self.task_type = task_type,
        self.name = name
        self.status = MaicaTask.MAICATASK_STATUS_READY
    
    def on_event(event):
        raise NotImplementedError()

    def start_event(self):
        if self.status == MaicaTask.MAICATASK_STATUS_READY:
            self.status = MaicaTask.MAICATASK_STATUS_RUNNING
            self.on_manual_run()
            self.status = MaicaTask.MAICATASK_STATUS_READY
        else:
            if self.status == MaicaTask.MAICATASK_STATUS_RUNNING:
                raise RuntimeError("MaicaTask {} is running".format(self.name))
            elif self.status == MaicaTask.MAICATASK_STATUS_ERROR:
                raise RuntimeError("MaicaTask {} is broken, check log for details".format(self.name))
    def on_manual_run(self):
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
    def __init__(self, task_type, name, except_ws_types = []):
        super().__init__(task_type, name)
        self.except_ws_types = except_ws_types
    
    def on_event(self, event):
        if event.event_type != MAICATASKEVENT_TYPE_WS:
            ws = event.data
            if ws.type in self.except_ws_types:
                self.on_received(ws)
    def on_received(self, ws):
        raise NotImplementedError()
        