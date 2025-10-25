from maica_tasker import *
from bot_interface import PY2
import threading
class SessionSenderAndReceiver(MaicaWSTask):
    multi_lock = threading.Lock()
    def __init__(self, task_type, name, except_ws_types=..., logger = None):
        super().__init__(task_type, name, except_ws_types)
        self.logger = logger

    def start_request(self, requests):
        SessionSenderAndReceiver.multi_lock.acquire()
        try:
            self.process_request(self.request)
        except Exception as e:
            if self.logger:
                self.logger.error("[SessionSenderAndReceiver] start_request error: " + str(e))
        finally:
            SessionSenderAndReceiver.multi_lock.release()
    def on_received(self, event):
        wspack = event.data
        raise NotImplementedError

    def process_request(self, request):
        raise NotImplementedError

